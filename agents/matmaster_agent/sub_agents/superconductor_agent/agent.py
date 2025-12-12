from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.superconductor_agent.prompt import (
    SuperconductorAgentDescription,
    SuperconductorAgentInstruction,
)

from .constant import SuperconductorAgentName, SuperconductorServerUrl
from .toolset import SuperconductorBohriumExecutor, SuperconductorBohriumStorge

sse_params = SseServerParams(url=SuperconductorServerUrl)

superconductor_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=SuperconductorBohriumStorge,
    executor=SuperconductorBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class SuperconductorAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[superconductor_toolset],
            name=SuperconductorAgentName,
            description=SuperconductorAgentDescription,
            instruction=SuperconductorAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_superconductor_agent(llm_config) -> BaseAgent:
    return SuperconductorAgent(llm_config)
