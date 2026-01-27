from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
    StreamableHTTPServerParams,
)

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.public_agents.sync_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserServerUrl,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.callback import (
    after_tool_callback,
    before_tool_callback,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
    SCIENCE_NAVIGATOR_MCP_SERVER_URL,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.prompt import (
    SCIENCE_NAVIGATOR_AGENT_DESCRIPTION,
    SCIENCE_NAVIGATOR_AGENT_INSTRUCTION,
)

sn_tools = [
    # "create-research-session",
    # "ask-followup-question"
    'search-papers-enhanced',
    'web-search',
]
web_parser_tools = [
    'extract_info_from_webpage',
]

science_navigator_toolset = McpToolset(
    connection_params=SseServerParams(
        url=SCIENCE_NAVIGATOR_MCP_SERVER_URL,
        timeout=360,
    ),
    tool_filter=sn_tools,
)
web_parser_toolset = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url=DocumentParserServerUrl,
        timeout=360,
    ),
    tool_filter=web_parser_tools,
)


class ScienceNavigatorAgent(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=SCIENCE_NAVIGATOR_AGENT_NAME,
            tools=[science_navigator_toolset, web_parser_toolset],
            model=llm_config.default_litellm_model,
            doc_summary=True,
            description=SCIENCE_NAVIGATOR_AGENT_DESCRIPTION,
            instruction=SCIENCE_NAVIGATOR_AGENT_INSTRUCTION,
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_tool_callback=after_tool_callback,
            before_tool_callback=before_tool_callback,
            render_tool_response=False,
        )


def init_science_navigator_agent(llm_config) -> BaseAgent:
    return ScienceNavigatorAgent(llm_config)
