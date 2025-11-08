import json
import logging
from typing import AsyncGenerator, Optional, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    is_function_call,
    is_function_response,
    update_state_event,
)
from agents.matmaster_agent.utils.helper_func import extract_json_from_string

logger = logging.getLogger(__name__)


class SchemaAgent(ErrorHandleLlmAgent):
    state_key: Optional[str] = None  # Direct supervisor agent in the hierarchy

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        event_exist = False
        async for event in super()._run_events(ctx):
            event_exist = True
            for part in event.content.parts:
                if part.text:  # json 字符串转为 function_call
                    if not event.partial:
                        raw_text = part.text
                        repaired_raw_text = extract_json_from_string(raw_text)
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] repaired_raw_text = {repaired_raw_text}'
                        )
                        schema_info: dict = json.loads(repaired_raw_text)

                        if schema_info.get(
                            'arguments'
                        ):  # Fix: set_model_response sometimes return this
                            schema_info = schema_info['arguments']
                        for system_job_result_event in context_function_event(
                            ctx,
                            self.name,
                            'materials_schema',
                            schema_info,
                            ModelRole,
                        ):
                            yield system_job_result_event
                        if self.state_key:
                            yield update_state_event(
                                ctx,
                                state_delta={self.state_key: schema_info},
                                event=event,
                            )
                    # 置空 text 消息
                    part.text = None
            if is_function_call(event) or is_function_response(
                event
            ):  # 没有被移除的 function_call: set_model_response
                yield event

        if not event_exist:
            logger.warning(
                f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] No event after remove_function_call'
            )
