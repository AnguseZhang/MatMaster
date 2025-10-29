from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseAsyncJobAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
    ORGANIC_REACTION_BOHRIUM_EXECUTOR,
    ORGANIC_REACTION_BOHRIUM_STORAGE,
    ORGANIC_REACTION_SERVER_URL,
)
from agents.matmaster_agent.organic_reaction_agent.prompt import (
    description,
    instruction_en,
)

autoTS = CalculationMCPToolset(
    connection_params=SseServerParams(url=ORGANIC_REACTION_SERVER_URL),
    executor=ORGANIC_REACTION_BOHRIUM_EXECUTOR,
    storage=ORGANIC_REACTION_BOHRIUM_STORAGE,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)

tools = [autoTS]


class OragnicReactionAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=ORGANIC_REACTION_AGENT_NAME,
            model=llm_config.default_litellm_model,
            description=description,
            agent_instruction=instruction_en,
            mcp_tools=tools,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_organic_reaction_agent(llm_config) -> LlmAgent:
    return OragnicReactionAgent(llm_config)
