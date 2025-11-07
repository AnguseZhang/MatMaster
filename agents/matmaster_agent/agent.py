import logging

from google.adk.agents import LlmAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.base_callbacks.private_callback import remove_function_call
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.agent import MatMasterFlowAgent
from agents.matmaster_agent.llm_config import (
    MatMasterLlmConfig,
)

logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(
    logging.ERROR
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    matmaster_agent = MatMasterFlowAgent(
        name=MATMASTER_AGENT_NAME,
        model=MatMasterLlmConfig.default_litellm_model,
        after_model_callback=remove_function_call,
    )
    track_adk_agent_recursive(matmaster_agent, MatMasterLlmConfig.opik_tracer)

    return matmaster_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
