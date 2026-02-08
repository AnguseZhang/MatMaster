"""
After-tool callback: store selected tool results into session memory for long-term use.

Used for tools like get_structure_info so structure/file metadata is retrievable
for later plans and parameter decisions.
"""

import json
import logging
from functools import wraps
from typing import Any, Optional, Union

from google.adk.tools import BaseTool, ToolContext
from mcp.types import CallToolResult

from agents.matmaster_agent.constant import FRONTEND_STATE_KEY, MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.memory.constant import MEMORY_TOOLS_STORE_RESULTS
from agents.matmaster_agent.services.memory import memory_write

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)

# Max chars to store per tool result; kept generous for literature/expert-intuition use.
MAX_STORED_RESULT_CHARS = 12000
MAX_ARGS_CHARS = 800


def _session_id_from_tool_context(tool_context: ToolContext) -> Optional[str]:
    state = getattr(tool_context, 'state', None)
    if state:
        sid = state.get(FRONTEND_STATE_KEY, {}).get('sessionId')
        if sid:
            return sid
    if getattr(tool_context, '_invocation_context', None) and getattr(
        tool_context._invocation_context, 'session', None
    ):
        return getattr(tool_context._invocation_context.session, 'id', None)
    return None


def _format_tool_result_summary(
    tool: BaseTool,
    args: dict,
    tool_response: Union[dict, CallToolResult],
) -> str:
    """Build a short summary string for storage."""
    args_str = json.dumps(args, ensure_ascii=False)[:MAX_ARGS_CHARS]
    if isinstance(tool_response, CallToolResult):
        if not tool_response.content or not getattr(
            tool_response.content[0], 'text', None
        ):
            result_str = '(empty)'
        else:
            result_str = (tool_response.content[0].text or '')[:MAX_STORED_RESULT_CHARS]
    else:
        result_str = json.dumps(tool_response, ensure_ascii=False)[
            :MAX_STORED_RESULT_CHARS
        ]
    return f"Tool {tool.name} | args: {args_str} | result: {result_str}"


def store_tool_result_in_memory(func: Any) -> Any:
    """Wrap after_tool_callback: after inner runs, store selected tool results to memory service."""

    @wraps(func)
    async def wrapper(
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
        tool_response: Union[dict, CallToolResult],
    ) -> Optional[dict]:
        inner_result = await func(tool, args, tool_context, tool_response)
        if tool.name not in MEMORY_TOOLS_STORE_RESULTS:
            return inner_result
        session_id = _session_id_from_tool_context(tool_context)
        if not session_id:
            logger.debug('store_tool_result_in_memory: no session_id, skip')
            return inner_result
        summary = _format_tool_result_summary(tool, args, tool_response)
        await memory_write(
            session_id=session_id,
            text=summary,
            metadata={'tool': tool.name, 'source': 'tool_result'},
        )
        logger.info(
            'store_tool_result_in_memory session_id=%s tool=%s stored',
            session_id,
            tool.name,
        )
        return inner_result

    return wrapper
