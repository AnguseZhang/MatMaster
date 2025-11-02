import copy
import logging
from typing import AsyncGenerator, Optional, Union, override

from google.adk.agents import InvocationContext, SequentialAgent
from google.adk.events import Event
from google.adk.models import BaseLlm
from pydantic import Field, computed_field, model_validator

from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleBaseAgent,
)
from agents.matmaster_agent.base_agents.job_agent import (
    ParamsCheckInfoAgent,
    ResultMCPAgent,
    SubmitCoreMCPAgent,
    SubmitRenderAgent,
    SubmitValidatorAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_agents.sync_agent import (
    SyncMCPAgent,
    ToolValidatorAgent,
)
from agents.matmaster_agent.base_callbacks.private_callback import (
    remove_function_call,
)
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.model import ToolCallInfo
from agents.matmaster_agent.prompt import (
    gen_params_check_info_agent_instruction,
    gen_result_agent_description,
    gen_result_core_agent_instruction,
    gen_submit_agent_description,
    gen_submit_core_agent_description,
    gen_submit_core_agent_instruction,
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    is_function_response,
    update_state_event,
)
from agents.matmaster_agent.utils.helper_func import (
    get_session_state,
)

logger = logging.getLogger(__name__)


# 同步计算 Agent，可自动 transfer 回主 Agent
class BaseSyncAgent(SubordinateFeaturesMixin, SyncMCPAgent):
    pass


class BaseSyncAgentWithToolValidator(
    SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleBaseAgent
):
    model: Union[str, BaseLlm]
    instruction: str
    tools: list

    @model_validator(mode='after')
    def after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        self._sync_mcp_agent = SyncMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_sync_mcp_agent",
            description=self.description,
            instruction=self.instruction,
            tools=self.tools,
            disallow_transfer_to_peers=True,
            disallow_transfer_to_parent=True,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
            render_tool_response=self.render_tool_response,
        )

        self._tool_validator_agent = ToolValidatorAgent(
            name=f"{agent_prefix}_tool_validator_agent",
        )

        self.sub_agents = [self.sync_mcp_agent, self.tool_validator_agent]

        return self

    @computed_field
    @property
    def sync_mcp_agent(self) -> SyncMCPAgent:
        return self._sync_mcp_agent

    @computed_field
    @property
    def tool_validator_agent(self) -> ToolValidatorAgent:
        return self._tool_validator_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        yield update_state_event(ctx, state_delta={'tool_hallucination': False})
        for _ in range(2):
            async for sync_mcp_event in self.sync_mcp_agent.run_async(ctx):
                yield sync_mcp_event

            async for tool_validator_event in self.tool_validator_agent.run_async(ctx):
                yield tool_validator_event

            if not ctx.session.state['tool_hallucination']:
                break


class BaseAsyncJobAgent(SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleBaseAgent):
    """
    Base agent class for handling asynchronous job submissions.

    Agents that need to submit asynchronous tasks should inherit from this class.
    It provides a complete workflow for job submission, result retrieval, and
    parameter validation through specialized sub-agents.
    """

    model: Union[str, BaseLlm] = MatMasterLlmConfig.default_litellm_model
    agent_instruction: str
    mcp_tools: list
    dflow_flag: bool = Field(
        False,
        description='Indicates if this agent is related to dflow workflows',
        exclude=True,
    )
    sync_tools: Optional[list] = Field(
        None,
        description='List of tools that will be executed synchronously on the server',
    )

    @model_validator(mode='after')
    def after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        # Create submission workflow agents
        submit_core_agent = SubmitCoreMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_submit_core_agent",
            description=gen_submit_core_agent_description(agent_prefix),
            instruction=gen_submit_core_agent_instruction(agent_prefix),
            tools=self.mcp_tools,
            disallow_transfer_to_parent=True,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
        )

        submit_render_agent = SubmitRenderAgent(
            model=self.model, name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = SubmitValidatorAgent(
            name=f"{agent_prefix}_submit_validator_agent"
        )

        # Create sequential agent for submission process
        self._submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=gen_submit_agent_description(agent_prefix),
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent],
        )

        # Create result retrieval agent
        result_core_agent = ResultMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_result_core_agent",
            tools=self.mcp_tools,
            instruction=gen_result_core_agent_instruction(agent_prefix),
            enable_tgz_unpack=self.enable_tgz_unpack,
        )

        self._result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description=gen_result_agent_description(),
            sub_agents=[result_core_agent],
        )

        # Create validation and information agents
        self._params_check_info_agent = ParamsCheckInfoAgent(
            model=self.model,
            name=f"{agent_prefix}_params_check_info_agent",
            instruction=gen_params_check_info_agent_instruction(),
            tools=self.mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            after_model_callback=remove_function_call,
        )

        self._tool_call_info_agent = SchemaAgent(
            model=self.model,
            name=f"{agent_prefix}_tool_call_info_agent",
            instruction=gen_tool_call_info_instruction(),
            tools=self.mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            after_model_callback=remove_function_call,
            output_schema=ToolCallInfo,
        )

        self.sub_agents = [
            self.submit_agent,
            self.result_agent,
            self.params_check_info_agent,
            self.tool_call_info_agent,
        ]

        return self

    @computed_field
    @property
    def submit_agent(self) -> SequentialAgent:
        return self._submit_agent

    @computed_field
    @property
    def result_agent(self) -> SequentialAgent:
        return self._result_agent

    @computed_field
    @property
    def params_check_info_agent(self) -> ParamsCheckInfoAgent:
        return self._params_check_info_agent

    @computed_field
    @property
    def tool_call_info_agent(self) -> SchemaAgent:
        return self._tool_call_info_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        session_state = get_session_state(ctx)
        update_plan = copy.deepcopy(session_state['plan'])
        update_plan['steps'][session_state['plan_index']]['status'] = 'process'
        yield update_state_event(
            ctx,
            state_delta={
                'dflow': self.dflow_flag,
                'sync_tools': self.sync_tools,
                'plan': update_plan,
            },
        )

        async for result_event in self.result_agent.run_async(ctx):
            yield result_event

        if session_state.get('origin_job_id', None) is not None or (
            session_state[FRONTEND_STATE_KEY]['biz'].get('origin_id', None) is not None
            and list(session_state['long_running_jobs'].keys())
            and session_state[FRONTEND_STATE_KEY]['biz']['origin_id']
            in list(session_state['long_running_jobs'].keys())
        ):  # Only Query Job Result
            pass
        else:
            # 根据计划来
            for materials_plan_function_call_event in context_function_event(
                ctx,
                self.name,
                'materials_plan_function_call',
                {
                    'msg': f'According to the plan, I will call the `{update_plan['steps'][session_state['plan_index']]['tool_name']}`'
                },
                ModelRole,
            ):
                yield materials_plan_function_call_event

            tool_call_info = {}
            async for tool_call_info_event in self.tool_call_info_agent.run_async(ctx):
                if (
                    is_function_response(tool_call_info_event)
                    and tool_call_info_event.content.parts[0].function_response.name
                    == 'materials_schema'
                ):
                    tool_call_info = tool_call_info_event.content.parts[
                        0
                    ].function_response.response
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] tool_call_info = {tool_call_info}'
                    )
                yield tool_call_info_event

            if not tool_call_info:
                return

            missing_tool_args = tool_call_info.get('missing_tool_args', None)

            if missing_tool_args:
                async for (
                    params_check_info_event
                ) in self.params_check_info_agent.run_async(ctx):
                    yield params_check_info_event
            else:
                yield update_state_event(ctx, state_delta={'tool_hallucination': False})
                for _ in range(2):
                    async for submit_event in self.submit_agent.run_async(ctx):
                        yield submit_event

                    if not ctx.session.state['tool_hallucination']:
                        break

            # cherry_pick_parts = cherry_pick_events(ctx)[-5:]
            # context_messages = '\n'.join(
            #     [
            #         f'<{item[0].title()}> said: \n{item[1]}\n'
            #         for item in cherry_pick_parts
            #     ]
            # )
            # logger.info(
            #     f"[{MATMASTER_AGENT_NAME}]:[{self.name}] context_messages = {context_messages}"
            # )
            #
            # prompt = gen_params_check_completed_agent_instruction().format(
            #     context_messages=context_messages
            # )
            # response = litellm.completion(
            #     model='azure/gpt-4o',
            #     messages=[{'role': 'user', 'content': prompt}],
            #     response_format=ParamsCheckComplete,
            # )
            # params_check_completed_json: dict = json.loads(
            #     response.choices[0].message.content
            # )
            # logger.info(
            #     f"[{MATMASTER_AGENT_NAME}]:[{self.name}] params_check_completed_json = {params_check_completed_json}"
            # )
            # params_check_completed = params_check_completed_json['flag']
            # params_check_reason = params_check_completed_json['reason']
            # params_check_msg = params_check_completed_json['analyzed_messages']
            #
            # # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
            # for params_check_reason_event in context_function_event(
            #     ctx,
            #     self.name,
            #     'system_params_check_result',
            #     {
            #         'complete': params_check_completed,
            #         'reason': params_check_reason,
            #         'analyzed_messages': params_check_msg,
            #     },
            #     ModelRole,
            # ):
            #     yield params_check_reason_event
            #
            # if not params_check_completed:
            #     # Call ParamsCheckInfoAgent to generate params needing check
            #     async for (
            #         params_check_info_event
            #     ) in self.params_check_info_agent.run_async(ctx):
            #         yield params_check_info_event
            # else:
            #     async for tool_call_info_event in self.tool_call_info_agent.run_async(
            #         ctx
            #     ):
            #         yield tool_call_info_event
            #     async for submit_event in self.submit_agent.run_async(ctx):
            #         yield submit_event
