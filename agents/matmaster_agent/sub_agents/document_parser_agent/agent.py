from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import (
    BaseSyncAgentWithToolValidator,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, BohriumStorge
from agents.matmaster_agent.llm_config import LLMConfig

from .callback import validate_document_url
from .constant import DocumentParserAgentName, DocumentParserServerUrl
from .prompt import DocumentParserAgentDescription, DocumentParserAgentInstruction

sse_params = SseServerParams(url=DocumentParserServerUrl)
document_parser_toolset = CalculationMCPToolset(
    connection_params=sse_params, storage=BohriumStorge
)


class DocumentParserAgentBase(BaseSyncAgentWithToolValidator):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=DocumentParserAgentName,
            description=DocumentParserAgentDescription,
            instruction=DocumentParserAgentInstruction,
            tools=[document_parser_toolset],
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_model_callback=validate_document_url,
            render_tool_response=True,
        )


def init_document_parser_agent(llm_config) -> BaseAgent:
    """Initialize Document Parser Agent"""
    return DocumentParserAgentBase(llm_config)
