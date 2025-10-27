import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from google.adk.models.lite_llm import LiteLlm
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.ABACUS_agent.agent import init_abacus_calculation_agent
from agents.matmaster_agent.apex_agent.agent import init_apex_agent
from agents.matmaster_agent.base_agents.io_agent import HandleFileUploadLlmAgent
from agents.matmaster_agent.callback import (
    matmaster_check_job_status,
    matmaster_hallucination_retry,
    matmaster_prepare_state,
    matmaster_set_lang,
)
from agents.matmaster_agent.chembrain_agent.agent import init_chembrain_agent
from agents.matmaster_agent.CompDART_agent.agent import init_compdrt_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.document_parser_agent.agent import (
    init_document_parser_agent,
)
from agents.matmaster_agent.DPACalculator_agent.agent import init_dpa_calculations_agent
from agents.matmaster_agent.finetune_dpa_agent.agent import init_finetune_dpa_agent
from agents.matmaster_agent.HEA_assistant_agent.agent import init_HEA_assistant_agent
from agents.matmaster_agent.HEACalculator_agent.agent import init_hea_calculator_agent
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.model import MatMasterTargetAgentEnum
from agents.matmaster_agent.MrDice_agent.agent import init_MrDice_agent
from agents.matmaster_agent.organic_reaction_agent.agent import (
    init_organic_reaction_agent,
)
from agents.matmaster_agent.perovskite_agent.agent import init_perovskite_agent
from agents.matmaster_agent.piloteye_electro_agent.agent import (
    init_piloteye_electro_agent,
)
from agents.matmaster_agent.prompt import (
    AgentDescription,
    AgentInstruction,
    GlobalInstruction,
    MatMasterCheckTransferPrompt,
)
from agents.matmaster_agent.public.callback import check_transfer
from agents.matmaster_agent.ssebrain_agent.agent import init_ssebrain_agent
from agents.matmaster_agent.structure_generate_agent.agent import (
    init_structure_generate_agent,
)
from agents.matmaster_agent.superconductor_agent.agent import init_superconductor_agent
from agents.matmaster_agent.task_orchestrator_agent.agent import (
    init_task_orchestrator_agent,
)
from agents.matmaster_agent.thermoelectric_agent.agent import init_thermoelectric_agent
from agents.matmaster_agent.traj_analysis_agent.agent import init_traj_analysis_agent
from agents.matmaster_agent.utils.event_utils import (
    frontend_text_event,
    send_error_event,
    update_state_event,
)

logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(
    logging.ERROR
)


class MatMasterAgent(HandleFileUploadLlmAgent):
    def __init__(self, llm_config):
        piloteye_electro_agent = init_piloteye_electro_agent(llm_config)
        traj_analysis_agent = init_traj_analysis_agent(llm_config)
        mrdice_agent = init_MrDice_agent(llm_config)
        dpa_calculator_agent = init_dpa_calculations_agent(llm_config)
        thermoelectric_agent = init_thermoelectric_agent(llm_config)
        superconductor_agent = init_superconductor_agent(llm_config)
        compdart_agent = init_compdrt_agent(llm_config)
        structure_generate_agent = init_structure_generate_agent(llm_config)
        apex_agent = init_apex_agent(llm_config)
        abacus_calculator_agent = init_abacus_calculation_agent(llm_config)
        organic_reaction_agent = init_organic_reaction_agent(llm_config)
        HEA_assistant_agent = init_HEA_assistant_agent(llm_config)
        hea_calculator_agent = init_hea_calculator_agent(llm_config, use_deepseek=False)
        ssebrain_agent = init_ssebrain_agent(llm_config)
        chembrain_agent = init_chembrain_agent(llm_config)
        perovskite_agent = init_perovskite_agent(llm_config)
        document_parser_agent = init_document_parser_agent(llm_config)
        finetune_dpa_agent = init_finetune_dpa_agent(llm_config)
        task_orchestrator_agent = init_task_orchestrator_agent(llm_config)

        super().__init__(
            name=MATMASTER_AGENT_NAME,
            model=llm_config.gpt_5_chat,
            sub_agents=[
                piloteye_electro_agent,
                traj_analysis_agent,
                dpa_calculator_agent,
                mrdice_agent,
                thermoelectric_agent,
                superconductor_agent,
                apex_agent,
                structure_generate_agent,
                abacus_calculator_agent,
                compdart_agent,
                organic_reaction_agent,
                HEA_assistant_agent,
                hea_calculator_agent,
                ssebrain_agent,
                chembrain_agent,
                perovskite_agent,
                document_parser_agent,
                finetune_dpa_agent,
                task_orchestrator_agent,
            ],
            global_instruction=GlobalInstruction,
            instruction=AgentInstruction,
            description=AgentDescription,
            before_agent_callback=[matmaster_prepare_state, matmaster_set_lang],
            after_model_callback=[
                matmaster_check_job_status,
                check_transfer(
                    prompt=MatMasterCheckTransferPrompt,
                    target_agent_enum=MatMasterTargetAgentEnum,
                ),
                matmaster_hallucination_retry,
            ],
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            # Delegate to parent implementation for the actual processing
            async for event in super()._run_async_impl(ctx):
                # 对于 [matmaster_check_job_status] 生成的消息， 手动拼一个流式消息
                if ctx.session.state['special_llm_response']:
                    yield frontend_text_event(
                        ctx, self.name, event.content.parts[0].text, ModelRole
                    )
                    yield update_state_event(
                        ctx, state_delta={'special_llm_response': False}
                    )
                yield event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

            error_handel_agent = LlmAgent(
                name='error_handel_agent',
                model=LiteLlm(model='litellm_proxy/azure/gpt-5-chat'),
            )
            # 调用错误处理 Agent
            async for error_handel_event in error_handel_agent.run_async(ctx):
                yield error_handel_event


def init_matmaster_agent() -> LlmAgent:
    matmaster_agent = MatMasterAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmaster_agent, MatMasterLlmConfig.opik_tracer)

    return matmaster_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
