from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import LOCAL_EXECUTOR, BohriumStorge
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.sub_agents.MrDice_agent.structure_search_agent.constant import (
    STRUCTURE_SEARCH_URL,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.structure_search_agent.prompt import (
    StructureSearchAgentName,
)

load_dotenv()

# Initialize MCP tools and agent
structure_search_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=STRUCTURE_SEARCH_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class StructureSearchAgentBase(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config, name_suffix=''):
        super().__init__(
            # model=llm_config.deepseek_chat,
            model=llm_config.default_litellm_model,
            name=StructureSearchAgentName + name_suffix,
            description='',
            instruction='',
            tools=[structure_search_toolset],
            render_tool_response=True,
            supervisor_agent=MrDice_Agent_Name,
        )


def init_structure_search_agent(llm_config, name_suffix='') -> BaseAgent:
    return StructureSearchAgentBase(llm_config, name_suffix=name_suffix)
