import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.flow_agents.constant import MATMASTER_FLOW
from agents.matmaster_agent.flow_agents.expand_agent.constant import EXPAND_AGENT
from agents.matmaster_agent.flow_agents.intent_agent.constant import INTENT_AGENT
from agents.matmaster_agent.flow_agents.plan_confirm_agent.constant import (
    PLAN_CONFIRM_AGENT,
)
from agents.matmaster_agent.flow_agents.scene_agent.constant import SCENE_AGENT
from agents.matmaster_agent.flow_agents.utils import is_content_has_keywords
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def filter_plan_info_llm_contents(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    contents = []
    for content in llm_request.contents[::-1]:
        if is_content_has_keywords(
            content,
            [
                PLAN_CONFIRM_AGENT,
                SCENE_AGENT,
                INTENT_AGENT,
                EXPAND_AGENT.replace('_agent', '_schema'),
                MATMASTER_FLOW,
            ],
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
