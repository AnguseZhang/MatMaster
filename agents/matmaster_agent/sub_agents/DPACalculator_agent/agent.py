from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.DPACalculator_agent.callback import (
    before_tool_callback,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
    DPAMCPServerUrl,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.finance import dpa_cost_func
from agents.matmaster_agent.sub_agents.DPACalculator_agent.prompt import (
    DPAAgentDescription,
    DPAAgentInstruction,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.toolset import (
    DPACalulator_BOHRIUM_EXECUTOR,
    DPACalulator_BOHRIUM_STORAGE,
)

dpa_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=DPAMCPServerUrl),
    storage=DPACalulator_BOHRIUM_STORAGE,
    executor=DPACalulator_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class DPACalculationsAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=DPACalulator_AGENT_NAME,
            tools=[dpa_toolset],
            model=llm_config.default_litellm_model,
            description=DPAAgentDescription,
            instruction=DPAAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            cost_func=dpa_cost_func,
            before_tool_callback=before_tool_callback,
        )


def init_dpa_calculations_agent(llm_config) -> BaseAgent:
    return DPACalculationsAgent(llm_config)
