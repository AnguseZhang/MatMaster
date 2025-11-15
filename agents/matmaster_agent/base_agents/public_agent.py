import logging
from typing import AsyncGenerator, Optional, Union, override

from google.adk.agents import InvocationContext, SequentialAgent
from google.adk.events import Event
from google.adk.models import BaseLlm
from pydantic import Field, computed_field, model_validator

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferLlmAgent,
)
from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleBaseAgent,
    ErrorHandleLlmAgent,
)
from agents.matmaster_agent.base_agents.job_agent import (
    RecommendParamsAgent,
    ResultMCPAgent,
    SubmitCoreMCPAgent,
    SubmitRenderAgent,
    SubmitValidatorAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.base_agents.prompt import (
    gen_recommend_params_agent_instruction,
)
from agents.matmaster_agent.base_agents.schema import create_tool_args_schema
from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.base_agents.sync_agent import (
    SyncMCPAgent,
    ToolValidatorAgent,
)
from agents.matmaster_agent.base_callbacks.private_callback import (
    default_before_model_callback,
    remove_function_call,
)
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.model import ToolCallInfoSchema
from agents.matmaster_agent.prompt import (
    gen_result_agent_description,
    gen_result_agent_instruction,
    gen_submit_agent_description,
    gen_submit_core_agent_description,
    gen_submit_core_agent_instruction,
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
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
    SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleLlmAgent
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
            after_model_callback=self.after_model_callback,
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
            instruction=gen_result_agent_instruction(agent_prefix),
            enable_tgz_unpack=self.enable_tgz_unpack,
        )

        self._result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description=gen_result_agent_description(),
            sub_agents=[result_core_agent],
        )

        self._recommend_params_agent = RecommendParamsAgent(
            model=self.model,
            name=f"{agent_prefix}_recommend_params_agent",
            instruction=gen_recommend_params_agent_instruction(),
            tools=self.mcp_tools,
            after_model_callback=remove_function_call,
        )

        self._recommend_params_schema_agent = SchemaAgent(
            model=MatMasterLlmConfig.tool_schema_model,
            name=f"{agent_prefix}_recommend_params_schema_agent",
            instruction=gen_recommend_params_agent_instruction(),
            state_key='recommend_params',
        )

        self._tool_call_info_agent = SchemaAgent(
            model=self.model,
            name=f"{agent_prefix}_tool_call_info_agent",
            tools=self.mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_model_callback=default_before_model_callback,
            after_model_callback=remove_function_call,
            output_schema=ToolCallInfoSchema,
            state_key='tool_call_info',
        )

        self._auto_add_params_agent = SchemaAgent(
            model=MatMasterLlmConfig.tool_schema_model,
            name=f"{agent_prefix}_auto_add_params_agent",
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=ToolCallInfoSchema,
            state_key='tool_call_info',
        )

        self._execution_summary_agent = DisallowTransferLlmAgent(
            name=f"{agent_prefix}_execution_summary_agent",
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction='使用 {target_language} 回答',
            description='总结本轮的计划执行情况',
            instruction='',
        )

        self.sub_agents = [
            self.submit_agent,
            self.result_agent,
            self.recommend_params_agent,
            self.tool_call_info_agent,
            self.execution_summary_agent,
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
    def recommend_params_agent(self) -> RecommendParamsAgent:
        return self._recommend_params_agent

    @computed_field
    @property
    def recommend_params_schema_agent(self) -> SchemaAgent:
        return self._recommend_params_schema_agent

    @computed_field
    @property
    def tool_call_info_agent(self) -> SchemaAgent:
        return self._tool_call_info_agent

    @computed_field
    @property
    def auto_add_params_agent(self) -> SchemaAgent:
        return self._auto_add_params_agent

    @computed_field
    @property
    def execution_summary_agent(self) -> DisallowTransferLlmAgent:
        return self._execution_summary_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        yield update_state_event(
            ctx,
            state_delta={
                'dflow': self.dflow_flag,
                'sync_tools': self.sync_tools,
            },
        )

        async for result_event in self.result_agent.run_async(ctx):
            yield result_event

        session_state = get_session_state(ctx)
        frontend_origin_id = session_state[FRONTEND_STATE_KEY]['biz'].get('origin_id')
        # 检查是否需要查询任务结果
        has_origin_job_id = session_state.get('origin_job_id') is not None
        has_matching_job = (
            frontend_origin_id is not None
            and frontend_origin_id in session_state.get('long_running_jobs', {})
            and ctx.invocation_id
            == session_state['long_running_jobs'][frontend_origin_id][
                'last_invocation_id'
            ]
        )
        logger.info(
            f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} has_origin_job_id = {has_origin_job_id}, has_matching_job = {has_matching_job}, {ctx.invocation_id}, {session_state['long_running_jobs']}'
        )

        if (
            has_origin_job_id
            or has_matching_job
            or ctx.session.state['scene']['type'][0] == SceneEnum.JobResultRetrieval
        ):
            # Only Query Job Result
            pass
        else:
            # 根据计划来
            current_step = session_state['plan']['steps'][session_state['plan_index']]
            for materials_plan_function_call_event in context_function_event(
                ctx,
                self.name,
                'materials_plan_function_call',
                {
                    'msg': f'According to the plan, I will call the `{current_step['tool_name']}`: {current_step['description']}'
                },
                ModelRole,
            ):
                yield materials_plan_function_call_event

            self.tool_call_info_agent.instruction = gen_tool_call_info_instruction(
                user_prompt=current_step['description']
            )
            async for tool_call_info_event in self.tool_call_info_agent.run_async(ctx):
                yield tool_call_info_event
            tool_call_info = ctx.session.state['tool_call_info']

            function_declaration = [
                item
                for item in ctx.session.state['function_declarations']
                if item['name'] == tool_call_info['tool_name']
            ]
            required_params = function_declaration[0]['parameters']['required']

            for param in required_params:
                if (
                    param in tool_call_info['tool_args'].keys()
                    or param in tool_call_info['missing_tool_args']
                ):
                    continue
                else:
                    tool_call_info['missing_tool_args'].append(param)

            yield update_state_event(
                ctx, state_delta={'tool_call_info': tool_call_info}
            )

            logger.info(
                f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} tool_call_info = {tool_call_info}'
            )
            if not tool_call_info:
                return

            # prompt = gen_params_check_completed_agent_instruction().format(
            #     context_messages=context_messages
            # )
            # response = litellm.completion(
            #     model='azure/gpt-4o',
            #     messages=[{'role': 'user', 'content': prompt}],
            #     response_format=ParamsCheckComplete,
            # )

            # self.auto_add_params_agent.instruction = gen_auto_add_params_instruction(
            #     update_tool_call_info
            # )
            # async for auto_add_params_event in self.auto_add_params_agent.run_async(
            #     ctx
            # ):
            #     yield auto_add_params_event
            # tool_call_info = ctx.session.state['tool_call_info']

            missing_tool_args = tool_call_info.get('missing_tool_args', None)

            if missing_tool_args:
                async for (
                    recommend_params_event
                ) in self.recommend_params_agent.run_async(ctx):
                    yield recommend_params_event

                self.recommend_params_schema_agent.output_schema = (
                    create_tool_args_schema(missing_tool_args, function_declaration)
                )
                async for (
                    recommend_params_schema_event
                ) in self.recommend_params_schema_agent.run_async(ctx):
                    yield recommend_params_schema_event

            # 前置 tool_hallucination 为 False
            yield update_state_event(ctx, state_delta={'tool_hallucination': False})
            yield update_state_event(ctx, state_delta={'validation_error': False})
            for _ in range(2):
                async for submit_event in self.submit_agent.run_async(ctx):
                    yield submit_event

                if not ctx.session.state['tool_hallucination']:
                    break

            if ctx.session.state['validation_error']:
                async for (
                    recommend_params_event
                ) in self.recommend_params_agent.run_async(ctx):
                    yield recommend_params_event

                self.recommend_params_schema_agent.output_schema = (
                    create_tool_args_schema(function_declaration)
                )
                async for (
                    recommend_params_schema_event
                ) in self.recommend_params_schema_agent.run_async(ctx):
                    yield recommend_params_schema_event

                async for submit_event in self.submit_agent.run_async(ctx):
                    yield submit_event

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
