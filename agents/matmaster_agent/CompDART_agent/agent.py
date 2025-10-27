from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import BaseAsyncJobAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.INVAR_agent.constant import (
    INVAR_AGENT_NAME,
    INVAR_BOHRIUM_EXECUTOR,
    INVAR_BOHRIUM_STORAGE,
    INVARMCPServerUrl,
)
from agents.matmaster_agent.INVAR_agent.prompt import (
    INVARAgentDescription,
    INVARAgentInstruction,
)
from agents.matmaster_agent.logger import matmodeler_logging_handler

mcp_tools_invar = CalculationMCPToolset(
    connection_params=SseServerParams(url=INVARMCPServerUrl),
    storage=INVAR_BOHRIUM_STORAGE,
    executor=INVAR_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class INVARAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            agent_name=INVAR_AGENT_NAME,
            mcp_tools=[mcp_tools_invar],
            model=llm_config.gpt_5_chat,
            agent_description=INVARAgentDescription,
            agent_instruction=INVARAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_invar_agent(llm_config) -> BaseAgent:
    return INVARAgent(llm_config)
