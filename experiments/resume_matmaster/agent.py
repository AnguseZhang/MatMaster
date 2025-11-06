import copy
import logging

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.apps import App, ResumabilityConfig
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.structure_generate_agent.agent import (
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


# before_tool_callback
async def default_before_tool_callback(tool: BaseTool, args, tool_context: ToolContext):
    if tool.name == 'build_bulk_structure_by_template':
        tool_confirmation = tool_context.tool_confirmation
        if not tool_confirmation:
            tool_context.request_confirmation(
                hint=(
                    f'Please approve or reject the tool call {tool.name}() by'
                    ' responding with a FunctionResponse with an expected'
                    ' ToolConfirmation payload.'
                ),
                # payload={
                #     'approved_days': 0,
                # },
            )
            return {
                'error': (
                    'This tool call requires confirmation, please approve or' ' reject.'
                )
            }
        elif not tool_context.tool_confirmation.confirmed:
            return {'error': 'This tool call is rejected.'}

        return await tool.run_async(args=args, tool_context=tool_context)

    return


class MatResumeAgent(LlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            name=MATMASTER_AGENT_NAME,
            model=llm_config.gpt_5_chat,
            global_instruction='当回答用户问题的时候，不要再最后再提出一个问题',
            instruction='AgentInstruction',
            description='AgentDescription',
            tools=[toolset],
            before_tool_callback=default_before_tool_callback,
        )


def init_resume_agent() -> LlmAgent:
    matmaster_agent = MatResumeAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmaster_agent, MatMasterLlmConfig.opik_tracer)

    return matmaster_agent


# Global instance of the agent
root_agent = init_resume_agent()

app = App(
    name='resume_matmaster',
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
