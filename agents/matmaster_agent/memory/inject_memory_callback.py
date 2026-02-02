"""
Before-model callback: inject short-term working memory into LLM request for tool-parameter filling.

Used by MCP/tool-calling agents so the model sees session memory when deciding tool args.
"""

import logging
from functools import wraps
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import BeforeModelCallback
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.memory.reader import format_short_term_memory
from agents.matmaster_agent.state import PLAN, STEP_DESCRIPTION

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def _query_from_request_and_state(callback_context: CallbackContext, llm_request: LlmRequest) -> str:
    """Build query string for memory retrieval from request contents and session state."""
    # Prefer current step description (tool step) so retrieval is relevant to the tool being filled
    state = getattr(callback_context, 'state', None)
    if state:
        plan = state.get(PLAN) or {}
        steps = plan.get('steps', [])
        plan_index = state.get('plan_index', 0)
        if 0 <= plan_index < len(steps):
            desc = steps[plan_index].get(STEP_DESCRIPTION) or steps[plan_index].get('step_description', '')
            if desc:
                return desc.strip()
    # Fallback: last text from contents
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            for part in getattr(content, 'parts', []) or []:
                if getattr(part, 'text', None):
                    return (part.text or '').strip()[:500]
    return ''


async def inject_memory_before_model_impl(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Prepend short-term memory block to llm_request.contents if any."""
    session_id = getattr(callback_context.session, 'id', None) if getattr(callback_context, 'session', None) else None
    if not session_id:
        return
    query = _query_from_request_and_state(callback_context, llm_request)
    block = format_short_term_memory(query_text=query or 'tool parameters', session_id=session_id)
    if not block or not block.strip():
        return
    # Prepend as a user message so the model sees it when filling tool args
    memory_content = Content(role='user', parts=[Part(text=block)])
    llm_request.contents = [memory_content] + list(llm_request.contents)
    logger.info(
        'inject_memory session_id=%s agent=%s query_len=%d block_len=%d',
        session_id,
        callback_context.agent_name,
        len(query),
        len(block),
    )


def inject_memory_before_model(func: BeforeModelCallback) -> BeforeModelCallback:
    """Chain inject_memory before the given before_model_callback (for MCP/tool agents)."""
    @wraps(func)
    async def wrapper(
        callback_context: CallbackContext, llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        await inject_memory_before_model_impl(callback_context, llm_request)
        return await func(callback_context, llm_request)
    return wrapper
