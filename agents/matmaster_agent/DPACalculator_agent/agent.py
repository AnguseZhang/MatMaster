from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.DPACalculator_agent.constant import (
    DPACalulator_BOHRIUM_EXECUTOR,
    DPACalulator_BOHRIUM_STORAGE,
    DPA_CALCULATOR_URL, DPACalulator_AGENT_NAME,
)
from agents.matmaster_agent.DPACalculator_agent.prompt import (
    DPAAgentDescription,
    DPAAgentInstruction,
    DPAResultAgentDescription,
    DPAResultAgentName,
    DPAResultCoreAgentInstruction,
    DPAResultCoreAgentName,
    DPAResultTransferAgentInstruction,
    DPAResultTransferAgentName,
    DPASubmitAgentDescription,
    DPASubmitAgentName,
    DPASubmitCoreAgentDescription,
    DPASubmitCoreAgentInstruction,
    DPASubmitCoreAgentName,
    DPASubmitRenderAgentName,
    DPATransferAgentInstruction,
    DPATransferAgentName,
)
from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME
)
from agents.matmaster_agent.logger import matmodeler_logging_handler

mcp_tools_dpa = CalculationMCPToolset(
    connection_params=SseServerParams(url=DPA_CALCULATOR_URL),
    storage=DPACalulator_BOHRIUM_STORAGE,
    executor=DPACalulator_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    executor_map={
        "build_bulk_structure": None,
        "build_molecule_structure": None,
        "build_surface_slab": None,
        "build_surface_adsorbate": None
    },
    logging_callback=matmodeler_logging_handler
)


class DPACalculationsAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            agent_name=DPACalulator_AGENT_NAME,
            mcp_tools=[mcp_tools_dpa],
            model=llm_config.gpt_4o,
            agent_description=DPAAgentDescription,
            agent_instruction=DPAAgentInstruction,
            submit_core_agent_class=SubmitCoreCalculationMCPLlmAgent,
            submit_core_agent_name=DPASubmitCoreAgentName,
            submit_core_agent_description=DPASubmitCoreAgentDescription,
            submit_core_agent_instruction=DPASubmitCoreAgentInstruction,
            submit_render_agent_name=DPASubmitRenderAgentName,
            result_core_agent_class=ResultCalculationMCPLlmAgent,
            result_core_agent_name=DPAResultCoreAgentName,
            result_core_agent_instruction=DPAResultCoreAgentInstruction,
            result_transfer_agent_name=DPAResultTransferAgentName,
            result_transfer_agent_instruction=DPAResultTransferAgentInstruction,
            transfer_agent_name=DPATransferAgentName,
            transfer_agent_instruction=DPATransferAgentInstruction,
            submit_agent_name=DPASubmitAgentName,
            submit_agent_description=DPASubmitAgentDescription,
            result_agent_name=DPAResultAgentName,
            result_agent_description=DPAResultAgentDescription,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME
        )


def init_dpa_calculations_agent(llm_config) -> BaseAgent:
    return DPACalculationsAgent(llm_config)
