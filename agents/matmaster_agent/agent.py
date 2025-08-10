from google.adk.agents import LlmAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.apex_agent.agent import init_apex_agent
from agents.matmaster_agent.base_agents.io_agent import (
    HandleFileUploadLlmAgent,
)
from agents.matmaster_agent.callback import matmaster_before_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.DPACalculator_agent.agent import (
    init_dpa_calculations_agent,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from agents.matmaster_agent.piloteye_electro_agent.agent import init_piloteye_electro_agent
from agents.matmaster_agent.DPACalculator_agent.agent import init_dpa_calculations_agent
from agents.matmaster_agent.thermoelectric_agent.agent import init_thermoelectric_agent
from agents.matmaster_agent.optimade_database_agent.agent import init_optimade_database_agent
from agents.matmaster_agent.superconductor_agent.agent import init_superconductor_agent
from agents.matmaster_agent.HEA_assistant_agent.agent import init_HEA_assistant_agent
from agents.matmaster_agent.crystalformer_agent.agent import init_crystalformer_agent
from agents.matmaster_agent.ABACUS_agent.agent import init_abacus_calculation_agent
from agents.matmaster_agent.optimade_database_agent.agent import (
    init_optimade_database_agent,
)
from agents.matmaster_agent.piloteye_electro_agent.agent import (
    init_piloteye_electro_agent,
)

from agents.matmaster_agent.prompt import (
    AgentDescription,
    AgentInstruction,
    GlobalInstruction,
)
from agents.matmaster_agent.superconductor_agent.agent import (
    init_superconductor_agent,
)
from agents.matmaster_agent.thermoelectric_agent.agent import (
    init_thermoelectric_agent,
)
from agents.matmaster_agent.traj_analysis_agent.agent import (
    init_traj_analysis_agent,
)


class MatMasterAgent(HandleFileUploadLlmAgent):

    def __init__(self, llm_config):
        piloteye_electro_agent = init_piloteye_electro_agent(llm_config)
        traj_analysis_agent = init_traj_analysis_agent(llm_config)
        optimade_agent = init_optimade_database_agent(llm_config)
        dpa_calculator_agent = init_dpa_calculations_agent(llm_config)
        thermoelectric_agent = init_thermoelectric_agent(llm_config)
        superconductor_agent = init_superconductor_agent(llm_config)
        crystalformer_agent = init_crystalformer_agent(llm_config)
        apex_agent = init_apex_agent(llm_config, use_deepseek=True)
        abacus_calculator_agent = init_abacus_calculation_agent(llm_config)
        HEA_assistant_agent = init_HEA_assistant_agent(llm_config)

        super().__init__(
            name=MATMASTER_AGENT_NAME,
            model=llm_config.gpt_4o,
            sub_agents=[
                piloteye_electro_agent,
                traj_analysis_agent,
                dpa_calculator_agent,
                optimade_agent,
                thermoelectric_agent,
                superconductor_agent,
                apex_agent,
                crystalformer_agent,
                abacus_calculator_agent,
                HEA_assistant_agent
            ],
            global_instruction=GlobalInstruction,
            instruction=AgentInstruction,
            description=AgentDescription,
            before_agent_callback=matmaster_before_agent
        )


def init_matmaster_agent() -> LlmAgent:
    matmodeler_agent = MatMasterAgent(MatMasterLlmConfig)
    track_adk_agent_recursive(matmodeler_agent, MatMasterLlmConfig.opik_tracer)

    return matmodeler_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
