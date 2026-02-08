import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.flow_agents.constant import (
    THINKING_CONTEXT_FILTER_KEYWORDS,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.context_utils import is_content_has_keywords

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def filter_thinking_llm_contents(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    contents = []
    for content in llm_request.contents[::-1]:
        if is_content_has_keywords(
            content,
            THINKING_CONTEXT_FILTER_KEYWORDS,
        ):
            continue
        contents.insert(0, content)

    logger.info(
        f'{callback_context.session.id} {callback_context.agent_name} contents = {len(contents)}'
    )

    if not contents:
        contents = [
            Content(
                role=ModelRole,
                parts=[Part(text='Default Text')],
            )
        ]

    llm_request.contents = contents
