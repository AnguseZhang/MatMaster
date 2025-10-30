from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseAsyncJobAgent
from agents.matmaster_agent.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
    COMPDART_BOHRIUM_EXECUTOR,
    COMPDART_BOHRIUM_STORAGE,
    COMPDART_MCPServerUrl,
)
from agents.matmaster_agent.CompDART_agent.prompt import (
    CompDARTAgentDescription,
    CompDARTAgentInstruction,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler

mcp_tools_compdrt = CalculationMCPToolset(
    connection_params=SseServerParams(url=COMPDART_MCPServerUrl),
    storage=COMPDART_BOHRIUM_STORAGE,
    executor=COMPDART_BOHRIUM_EXECUTOR,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class CompDARTAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=COMPDART_AGENT_NAME,
            mcp_tools=[mcp_tools_compdrt],
            model=llm_config.default_litellm_model,
            description=CompDARTAgentDescription,
            agent_instruction=CompDARTAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_compdrt_agent(llm_config) -> BaseAgent:
    return CompDARTAgent(llm_config)
