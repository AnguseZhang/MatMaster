from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

from agents.matmaster_agent.constant import LOCAL_EXECUTOR, BohriumStorge
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.sub_agents.structure_search_agent.constant import (
    STRUCTURE_SEARCH_AGENT_NAME,
    STRUCTURE_SEARCH_URL,
)

mcp_params = StreamableHTTPServerParams(
    url=STRUCTURE_SEARCH_URL,
)
structure_search_toolset = CalculationMCPToolset(
    connection_params=mcp_params,
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class StructureSearchAgentBase(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=STRUCTURE_SEARCH_AGENT_NAME,
            description='',
            instruction='',
            tools=[structure_search_toolset],
            render_tool_response=True,
            supervisor_agent=MrDice_Agent_Name,
        )


def init_structure_search_agent(llm_config, name_suffix='') -> BaseAgent:
    return StructureSearchAgentBase(llm_config, name_suffix=name_suffix)
