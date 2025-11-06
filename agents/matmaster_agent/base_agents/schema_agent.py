import json
import logging
from json import JSONDecodeError
from typing import AsyncGenerator, Optional, override

import litellm
from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.llm_config import TOOL_SCHEMA_MODEL
from agents.matmaster_agent.llm_node.prompt import repair_schema_prompt
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    is_function_call,
    is_function_response,
    update_state_event,
)

logger = logging.getLogger(__name__)


class SchemaAgent(ErrorHandleLlmAgent):
    state_key: Optional[str] = None  # Direct supervisor agent in the hierarchy

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            for part in event.content.parts:
                if part.text:
                    if not event.partial:
                        raw_text = part.text
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] raw_text = {raw_text}'
                        )
                        try:
                            schema_info: dict = json.loads(raw_text)
                        except JSONDecodeError:
                            try:
                                prompt = repair_schema_prompt().format(
                                    raw_text=raw_text
                                )
                                response = litellm.completion(
                                    model=TOOL_SCHEMA_MODEL,
                                    messages=[{'role': 'user', 'content': prompt}],
                                    response_format=self.output_schema,
                                )
                                repaired_raw_text = response.choices[0].message.content
                                logger.info(
                                    f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] response = {repaired_raw_text}'
                                )
                                schema_info: dict = json.loads(repaired_raw_text)
                            except BaseException:
                                raise

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
            if is_function_call(event) or is_function_response(event):
                yield event
