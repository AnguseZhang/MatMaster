import logging
from typing import AsyncGenerator

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from google.adk.models.lite_llm import LiteLlm
from opik.integrations.adk import track_adk_agent_recursive
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_agents.io_agent import HandleFileUploadLlmAgent
from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.base_callbacks.private_callback import remove_function_call
from agents.matmaster_agent.callback import (
    matmaster_prepare_state,
    matmaster_set_lang,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.analysis_agent.prompt import (
    get_analysis_instruction,
)
from agents.matmaster_agent.flow_agents.execution_agent.agent import (
    MatMasterSupervisorAgent,
)
from agents.matmaster_agent.flow_agents.model import FlowStatusEnum, PlanSchema
from agents.matmaster_agent.flow_agents.plan_execution_check_agent.prompt import (
    PLAN_EXECUTION_CHECK_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.planner_agent.prompt import (
    PLAN_MAKE_INSTRUCTION,
    PLAN_SUMMARY_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.utils import check_plan
from agents.matmaster_agent.llm_config import (
    DEFAULT_MODEL,
    MatMasterLlmConfig,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.agent import (
    bohriumpublic_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.agent import (
    mofdb_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.agent import (
    openlam_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.agent import (
    optimade_toolset,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.agent import (
    structure_generate_toolset,
)
from agents.matmaster_agent.utils.event_utils import (
    send_error_event,
)

logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(
    logging.ERROR
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MatMasterAgent(HandleFileUploadLlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self._plan_make_agent = SchemaAgent(
            name='plan_make_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='根据用户的问题依据现有工具执行计划，如果没有工具可用，告知用户，不要自己制造工具或幻想',
            instruction=PLAN_MAKE_INSTRUCTION,
            tools=[
                structure_generate_toolset,
                optimade_toolset,
                bohriumpublic_toolset,
                openlam_toolset,
                mofdb_toolset,
            ],
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            before_agent_callback=[
                matmaster_prepare_state,
                matmaster_set_lang,
            ],
            after_model_callback=remove_function_call,
            output_schema=PlanSchema,
            state_key='plan',
        )

        self._plan_summary_agent = ErrorHandleLlmAgent(
            name='plan_summary_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='根据 materials_plan 返回的计划进行总结',
            instruction=PLAN_SUMMARY_INSTRUCTION,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )

        self._plan_execution_check_agent = ErrorHandleLlmAgent(
            name='plan_execution_check_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='汇总计划的执行情况，并根据计划提示下一步的动作',
            instruction=PLAN_EXECUTION_CHECK_INSTRUCTION,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )

        self._execution_agent = MatMasterSupervisorAgent(
            name='execution_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='根据 materials_plan 返回的计划进行总结',
            instruction='',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )

        self._analysis_agent = ErrorHandleLlmAgent(
            name='post_execution_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction='使用 {target_language} 回答',
            description='总结本轮的计划执行情况',
            instruction='',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )

        self.sub_agents = [
            self.plan_make_agent,
            self.plan_summary_agent,
            self.execution_agent,
            self.analysis_agent,
        ]

        return self

    @computed_field
    @property
    def plan_make_agent(self) -> LlmAgent:
        return self._plan_make_agent

    @computed_field
    @property
    def plan_summary_agent(self) -> LlmAgent:
        return self._plan_summary_agent

    @computed_field
    @property
    def plan_execution_check_agent(self) -> LlmAgent:
        return self._plan_execution_check_agent

    @computed_field
    @property
    def execution_agent(self) -> LlmAgent:
        return self._execution_agent

    @computed_field
    @property
    def analysis_agent(self) -> LlmAgent:
        return self._analysis_agent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            # 判断要不要制定计划
            if check_plan(ctx) == FlowStatusEnum.NO_PLAN:
                # 制定计划
                async for plan_event in self.plan_make_agent.run_async(ctx):
                    yield plan_event

                # 检查计划的合理性，TODO: tool_name 伪造, target_agent 为 None

                # 总结计划
                async for plan_summary_event in self.plan_summary_agent.run_async(ctx):
                    yield plan_summary_event

            # 计划出错或者无可调用工具，直接返回
            if (
                ctx.session.state['error_occurred']
                or not ctx.session.state['plan']['feasibility']
            ):
                return

            if check_plan(ctx) not in [FlowStatusEnum.NO_PLAN, FlowStatusEnum.NEW_PLAN]:
                # 检查之前的计划执行情况，老计划才执行
                async for (
                    plan_execution_check_event
                ) in self.plan_execution_check_agent.run_async(ctx):
                    yield plan_execution_check_event

            # 执行计划
            if ctx.session.state['plan']['feasibility'] in ['full', 'part']:
                async for execution_event in self.execution_agent.run_async(ctx):
                    yield execution_event

            # 总结执行情况
            self._analysis_agent.instruction = get_analysis_instruction(
                ctx.session.state['plan']
            )
            async for analysis_event in self.analysis_agent.run_async(ctx):
                yield analysis_event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

            error_handel_agent = LlmAgent(
                name='error_handel_agent',
                model=LiteLlm(model=DEFAULT_MODEL),
            )
            # 调用错误处理 Agent
            async for error_handel_event in error_handel_agent.run_async(ctx):
                yield error_handel_event


#
# class MatMasterSupervisorAgent(HandleFileUploadLlmAgent):
#     def __init__(self, llm_config: LLMConfig):
#         piloteye_electro_agent = init_piloteye_electro_agent(llm_config)
#         traj_analysis_agent = init_traj_analysis_agent(llm_config)
#         mrdice_agent = init_MrDice_agent(llm_config)
#         dpa_calculator_agent = init_dpa_calculations_agent(llm_config)
#         thermoelectric_agent = init_thermoelectric_agent(llm_config)
#         superconductor_agent = init_superconductor_agent(llm_config)
#         compdart_agent = init_compdrt_agent(llm_config)
#         structure_generate_agent = init_structure_generate_agent(llm_config)
#         apex_agent = init_apex_agent(llm_config)
#         abacus_calculator_agent = init_abacus_calculation_agent(llm_config)
#         organic_reaction_agent = init_organic_reaction_agent(llm_config)
#         HEA_assistant_agent = init_HEA_assistant_agent(llm_config)
#         hea_calculator_agent = init_hea_calculator_agent(llm_config, use_deepseek=False)
#         ssebrain_agent = init_ssebrain_agent(llm_config)
#         chembrain_agent = init_chembrain_agent(llm_config)
#         perovskite_agent = init_perovskite_agent(llm_config)
#         document_parser_agent = init_document_parser_agent(llm_config)
#         finetune_dpa_agent = init_finetune_dpa_agent(llm_config)
#         task_orchestrator_agent = init_task_orchestrator_agent(llm_config)
#
#         super().__init__(
#             name=MATMASTER_AGENT_NAME,
#             model=llm_config.default_litellm_model,
#             sub_agents=[
#                 piloteye_electro_agent,
#                 traj_analysis_agent,
#                 dpa_calculator_agent,
#                 mrdice_agent,
#                 thermoelectric_agent,
#                 superconductor_agent,
#                 apex_agent,
#                 structure_generate_agent,
#                 abacus_calculator_agent,
#                 compdart_agent,
#                 organic_reaction_agent,
#                 HEA_assistant_agent,
#                 hea_calculator_agent,
#                 ssebrain_agent,
#                 chembrain_agent,
#                 perovskite_agent,
#                 document_parser_agent,
#                 finetune_dpa_agent,
#                 task_orchestrator_agent,
#             ],
#             global_instruction=GlobalInstruction,
#             instruction=AgentInstruction,
#             description=AgentDescription,
#             before_agent_callback=[
#                 matmaster_prepare_state,
#                 matmaster_set_lang,
#             ],
#             after_model_callback=[
#                 matmaster_check_job_status,
#                 check_transfer(
#                     prompt=MatMasterCheckTransferPrompt,
#                     target_agent_enum=MatMasterSubAgentsEnum,
#                 ),
#                 matmaster_hallucination_retry,
#             ],
#         )
#
#     @override
#     async def _run_async_impl(
#         self, ctx: InvocationContext
#     ) -> AsyncGenerator[Event, None]:
#         try:
#             # Delegate to parent implementation for the actual processing
#             async for event in super()._run_async_impl(ctx):
#                 # 对于 [matmaster_check_job_status] 生成的消息， 手动拼一个流式消息
#                 if ctx.session.state['special_llm_response']:
#                     yield frontend_text_event(
#                         ctx, self.name, event.content.parts[0].text, ModelRole
#                     )
#                     yield update_state_event(
#                         ctx, state_delta={'special_llm_response': False}
#                     )
#                 yield event
#         except BaseException as err:
#             async for error_event in send_error_event(err, ctx, self.name):
#                 yield error_event
#
#             error_handel_agent = LlmAgent(
#                 name='error_handel_agent',
#                 model=LiteLlm(model=DEFAULT_MODEL),
#             )
#             # 调用错误处理 Agent
#             async for error_handel_event in error_handel_agent.run_async(ctx):
#                 yield error_handel_event
#
#         matmaster_events_only_author = [item[2] for item in cherry_pick_events(ctx)]
#         logger.info(
#             f'[{MATMASTER_AGENT_NAME}] matmaster_events_only_author = {matmaster_events_only_author}'
#         )
#         last_user_index = (
#             len(matmaster_events_only_author)
#             - 1
#             - matmaster_events_only_author[::-1].index('user')
#         )
#         last_event_author = matmaster_events_only_author[-1]
#         slice_from_last_user = matmaster_events_only_author[last_user_index:]
#         only_user_matmaster = set(slice_from_last_user).issubset(
#             {'user', MATMASTER_AGENT_NAME}
#         )
#         if last_event_author == MATMASTER_AGENT_NAME and (
#             only_user_matmaster
#             or matmaster_events_only_author[-2] not in ['user', MATMASTER_AGENT_NAME]
#         ):
#             for generate_nps_event in context_function_event(
#                 ctx,
#                 self.name,
#                 'matmaster_generate_nps',
#                 {},
#                 ModelRole,
#                 {'session_id': ctx.session.id, 'invocation_id': ctx.invocation_id},
#             ):
#                 yield generate_nps_event
#
#         logger.info(
#             f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} state = {ctx.session.state}'
#         )
#


def init_matmaster_agent() -> LlmAgent:
    matmaster_agent = MatMasterAgent(
        name=MATMASTER_AGENT_NAME,
        model=MatMasterLlmConfig.default_litellm_model,
        after_model_callback=remove_function_call,
    )
    track_adk_agent_recursive(matmaster_agent, MatMasterLlmConfig.opik_tracer)

    return matmaster_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
