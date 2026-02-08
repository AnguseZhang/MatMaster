import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, UserRole
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def only_select_user_request(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    llm_request.contents = [
        Content(
            role=UserRole,
            parts=[Part(text=callback_context.user_content.parts[0].text)],
        )
    ]
