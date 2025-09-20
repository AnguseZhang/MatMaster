import copy
import json
from typing import Any, Dict

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.tool_context import ToolContext
from mcp.types import CallToolResult

from agents.matmaster_agent.base_agents.job_agent import (
    BaseAsyncJobAgent,
    CalculationMCPLlmAgent,
    ResultCalculationMCPLlmAgent,
    SubmitCoreCalculationMCPLlmAgent,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.utils.helper_func import is_json
from agents.matmaster_agent.constant import BohriumStorge

from .constant import (
    DocumentParserServerUrl,
    DocumentParserAgentName,
)
from .prompt import (
    DocumentParserAgentDescription,
    DocumentParserAgentInstruction,
)
from .callback import validate_document_url, document_parser_before_tool, document_parser_after_tool


sse_params = SseServerParams(url=DocumentParserServerUrl)
toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=BohriumStorge
)


class DocumentParserAgent(CalculationMCPLlmAgent):

    def __init__(self, llm_config):

        super().__init__(
            model=llm_config.gpt_5_chat,
            name=DocumentParserAgentName,
            description=DocumentParserAgentDescription,
            instruction=DocumentParserAgentInstruction,
            tools=[toolset],
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_model_callback=validate_document_url,
            before_tool_callback=document_parser_before_tool,
            after_tool_callback=document_parser_after_tool
        )

def init_document_parser_agent(llm_config) -> BaseAgent:
    """Initialize Document Parser Agent"""
    return DocumentParserAgent(llm_config)
