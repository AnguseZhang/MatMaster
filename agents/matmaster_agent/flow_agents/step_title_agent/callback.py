import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai.types import Content, Part

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def filter_llm_contents(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    contents = []
    for content in llm_request.contents[::-1]:
        parts = []
        for part in content.parts:
            if (
                part.text
                and '[matmaster_supervisor_agent] `materials_plan_function_call`'
                in part.text
            ):
                parts.append(part)
                break  # 只保留最近一个
        if parts:
            contents.insert(0, Content(role=content.role, parts=parts))
            break  # 只保留最近一个

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
