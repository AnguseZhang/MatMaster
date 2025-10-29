from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import LOCAL_EXECUTOR, BohriumStorge
from agents.matmaster_agent.MrDice_agent.bohriumpublic_agent.constant import (
    BOHRIUMPUBLIC_URL,
)
from agents.matmaster_agent.MrDice_agent.bohriumpublic_agent.finance import cost_func
from agents.matmaster_agent.MrDice_agent.bohriumpublic_agent.prompt import (
    BohriumPublicAgentDescription,
    BohriumPublicAgentInstruction,
    BohriumPublicAgentName,
)
from agents.matmaster_agent.MrDice_agent.constant import MrDice_Agent_Name

load_dotenv()

# Initialize MCP tools and agent
mcp_tools = CalculationMCPToolset(
    connection_params=SseServerParams(url=BOHRIUMPUBLIC_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR,
)


class Bohriumpublic_AgentBase(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config):
        super().__init__(
            # model=llm_config.deepseek_chat,
            model=llm_config.gpt_5_chat,
            name=BohriumPublicAgentName,
            description=BohriumPublicAgentDescription,
            instruction=BohriumPublicAgentInstruction,
            tools=[mcp_tools],
            render_tool_response=True,
            supervisor_agent=MrDice_Agent_Name,
            cost_func=cost_func,
        )


def init_bohriumpublic_database_agent(llm_config) -> BaseAgent:
    return Bohriumpublic_AgentBase(llm_config)
