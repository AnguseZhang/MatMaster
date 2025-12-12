from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.vaspkit_agent.constant import (
    VASPKIT_AGENT_NAME,
    VASPKIT_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.vaspkit_agent.prompt import (
    VASPKITAgentDescription,
    VASPKITAgentInstruction,
)
from agents.matmaster_agent.sub_agents.vaspkit_agent.toolset import (
    VASPKIT_BOHRIUM_STORAGE,
)

vaspkit_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=VASPKIT_MCP_SERVER_URL),
    storage=VASPKIT_BOHRIUM_STORAGE,
    executor=LOCAL_EXECUTOR,
    logging_callback=matmodeler_logging_handler,
)


class VASPKITAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=VASPKIT_AGENT_NAME,
            description=VASPKITAgentDescription,
            instruction=VASPKITAgentInstruction,
            tools=[vaspkit_toolset],
            render_tool_response=True,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_vaspkit_agent(llm_config) -> BaseAgent:
    return VASPKITAgent(llm_config)
