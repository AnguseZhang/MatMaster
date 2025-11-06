import copy
import logging
from functools import wraps
from typing import AsyncGenerator, Optional

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent, InvocationContext, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import BeforeToolCallback
from google.adk.events import Event
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.genai import types
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.base_agents.mcp_agent import MCPAgent
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
    Transfer2Agent,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.structure_generate_agent import (
    StructureGenerateServerUrl,
)

logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(
    logging.ERROR
)

StructureGenerateBohriumExecutor = copy.deepcopy(BohriumExecutor)
StructureGenerateBohriumStorge = copy.deepcopy(BohriumStorge)
StructureGenerateBohriumExecutor['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-788025/structure-generate-agent:small'
StructureGenerateBohriumExecutor['machine']['remote_profile'][
    'machine_type'
] = 'c8_m32_1 * NVIDIA 4090'

sse_params = SseServerParams(url=StructureGenerateServerUrl)

toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=StructureGenerateBohriumStorge,
    executor=StructureGenerateBohriumExecutor,
    async_mode=False,
    logging_callback=matmodeler_logging_handler,
)


async def demo_before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    callback_context.state['agent_state'] = 1
    callback_context.state['model_state'] = None
    callback_context.state['tool_state'] = None


async def demo_before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    callback_context.state['model_state'] = {'step': 'demo_before_model_callback'}


async def demo_after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    callback_context.state['model_state'] = {'step': 'demo_after_model_callback'}


def catch_before_tool_callback_error(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 如果 tool 为 Transfer2Agent，直接 return
        if tool.name == Transfer2Agent:
            return None

        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

    return wrapper


async def demo_before_tool_callback(tool: BaseTool, args, tool_context: ToolContext):
    tool_context.state['tool_state'] = 1


class MatSubAgent(MCPAgent):
    def __init__(self, llm_config):
        super().__init__(
            name='mat_subagent',
            model=llm_config.gpt_5_chat,
            global_instruction='负责构建结构',
            instruction='AgentInstruction',
            description='AgentDescription',
            tools=[toolset],
            disallow_transfer_to_peers=True,
            disallow_transfer_to_parent=True,
            before_model_callback=demo_before_model_callback,
            after_model_callback=demo_after_model_callback,
            before_tool_callback=catch_before_tool_callback_error(
                demo_before_tool_callback
            ),
        )


class MatBaseAgent(BaseAgent):
    mat_subagent: LlmAgent

    def __init__(self, llm_config):
        mat_subagent = MatSubAgent(llm_config)
        super().__init__(
            name='mat_subagent',
            description='AgentDescription',
            mat_subagent=mat_subagent,
            sub_agents=[mat_subagent],
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in self.mat_subagent.run_async(ctx):
            yield event


class MatCallbackAgent(LlmAgent):
    mat_baseagent: BaseAgent

    def __init__(self, llm_config):
        mat_baseagent = MatBaseAgent(llm_config)

        super().__init__(
            name=MATMASTER_AGENT_NAME,
            model=llm_config.gpt_5_chat,
            global_instruction='当回答用户问题的时候，不要再最后再提出一个问题',
            instruction='AgentInstruction',
            description='AgentDescription',
            before_agent_callback=demo_before_agent_callback,
            mat_baseagent=mat_baseagent,
            sub_agents=[mat_baseagent],
        )

        self.mat_baseagent = mat_baseagent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in self.mat_baseagent.run_async(ctx):
            yield event


def init_callback_agent() -> LlmAgent:
    matmaster_agent = MatCallbackAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmaster_agent, MatMasterLlmConfig.opik_tracer)

    return matmaster_agent


# Global instance of the agent
root_agent = init_callback_agent()
