from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseSyncAgent
from agents.matmaster_agent.constant import LOCAL_EXECUTOR, BohriumStorge
from agents.matmaster_agent.sub_agents.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.constant import (
    OPENLAM_URL,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.prompt import (
    OpenlamAgentDescription,
    OpenlamAgentInstruction,
    OpenlamAgentName,
)

load_dotenv()

# Initialize MCP tools and agent
openlam_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=OPENLAM_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class Openlam_AgentBase(BaseSyncAgent):
    def __init__(self, llm_config, name_suffix=''):
        super().__init__(
            # model=llm_config.deepseek_chat,
            model=llm_config.gpt_5_chat,
            name=OpenlamAgentName + name_suffix,
            description=OpenlamAgentDescription,
            instruction=OpenlamAgentInstruction,
            tools=[openlam_toolset],
            render_tool_response=True,
            supervisor_agent=MrDice_Agent_Name,
        )


def init_openlam_database_agent(llm_config, name_suffix) -> BaseAgent:
    return Openlam_AgentBase(llm_config, name_suffix)
