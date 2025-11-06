from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseSyncAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.prompt import (
    HEA_assistant_AgentDescription,
    HEA_assistant_AgentInstruction,
    HEA_assistant_AgentName,
)

from .constant import HEA_assistant_agent_ServerUrl

sse_params = SseServerParams(url=HEA_assistant_agent_ServerUrl)

hea_assistant_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    async_mode=False,
    wait=True,
)


class HEA_assistant_AgentBase(BaseSyncAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=HEA_assistant_AgentName,
            description=HEA_assistant_AgentDescription,
            instruction=HEA_assistant_AgentInstruction,
            tools=[hea_assistant_toolset],
        )


def init_HEA_assistant_agent(llm_config) -> BaseAgent:
    return HEA_assistant_AgentBase(llm_config)
