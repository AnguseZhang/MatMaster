import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.flow_agents.constant import (
    MATMASTER_FLOW,
    MATMASTER_FLOW_PLANS,
    MATMASTER_GENERATE_NPS,
    UNIVERSAL_CONTEXT_FILTER_KEYWORDS,
)
from agents.matmaster_agent.flow_agents.plan_info_agent.constant import PLAN_INFO_AGENT
from agents.matmaster_agent.flow_agents.plan_make_agent.constant import PLAN_MAKE_AGENT
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.context_utils import is_content_has_keywords

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def filter_summary_llm_contents(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    contents = []
    for content in llm_request.contents[::-1]:
        if is_content_has_keywords(
            content,
            UNIVERSAL_CONTEXT_FILTER_KEYWORDS
            + [PLAN_MAKE_AGENT, PLAN_INFO_AGENT]
            + [MATMASTER_FLOW, MATMASTER_FLOW_PLANS, MATMASTER_GENERATE_NPS],
        ):
            continue
        else:
            contents.insert(0, content)

    logger.info(
        f'{callback_context.session.id} {callback_context.agent_name} contents = {contents}'
    )

    if not contents:
        contents = [
            Content(
                role=ModelRole,
                parts=[Part(text='Default Text')],
            )
        ]

    llm_request.contents = contents
