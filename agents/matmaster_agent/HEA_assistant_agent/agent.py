from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent

from agents.matmaster_agent.HEA_assistant_agent.prompt import (
    HEA_assistant_AgentName,
    HEA_assistant_AgentDescription,
    HEA_assistant_AgentInstruction,
)

from .constant import HEA_assistant_agent_ServerUrl
from ..base_agents.job_agent import CalculationMCPLlmAgent

from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
sse_params = SseServerParams(url=HEA_assistant_agent_ServerUrl)

toolset = CalculationMCPToolset(
    connection_params=sse_params,
    async_mode=False,  
    wait=True,         
)

class HEA_assistant_Agent(CalculationMCPLlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            model = llm_config.gpt_4o,
            name=HEA_assistant_AgentName,
            description=HEA_assistant_AgentDescription,
            instruction=HEA_assistant_AgentInstruction,
            tools=[toolset], 
        )

def init_HEA_assistant_agent(llm_config) -> BaseAgent:
    return HEA_assistant_Agent(llm_config)

