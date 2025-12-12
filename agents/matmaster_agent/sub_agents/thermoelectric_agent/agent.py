from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.thermoelectric_agent.prompt import (
    ThermoAgentDescription,
    ThermoAgentInstruction,
    ThermoAgentName,
)

from .constant import ThermoelectricServerUrl
from .toolset import ThermoelectricBohriumExecutor, ThermoelectricBohriumStorge

sse_params = SseServerParams(url=ThermoelectricServerUrl)

thermoelectric_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=ThermoelectricBohriumStorge,
    executor=ThermoelectricBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class ThermoAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[thermoelectric_toolset],
            name=ThermoAgentName,
            description=ThermoAgentDescription,
            instruction=ThermoAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_thermoelectric_agent(llm_config) -> BaseAgent:
    return ThermoAgent(llm_config)
