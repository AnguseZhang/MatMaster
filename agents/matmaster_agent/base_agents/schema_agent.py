import json
import logging
import re
from typing import AsyncGenerator, Optional, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferMixin,
)
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
            schema_info = None
            for part in event.content.parts:
                if part.text:  # json 字符串转为 function_call
                    if not event.partial:
                        raw_text = part.text
                        repaired_raw_text = extract_json_from_string(raw_text)
                        repaired_raw_text = re.sub(
                            r',(\s*[}\]])', r'\1', repaired_raw_text
                        )  # 移除尾随逗号
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] repaired_raw_text = {repaired_raw_text}'
                        )
                        schema_info = json.loads(repaired_raw_text)

                        if schema_info.get(
                            'arguments'
                        ):  # Fix: set_model_response sometimes return this
                            schema_info = schema_info['arguments']
                        for system_job_result_event in context_function_event(
                            ctx,
                            self.name,
                            f'{self.name.replace('_agent', '')}_schema',
                            schema_info,
                            ModelRole,
                        ):
                            yield system_job_result_event
                    # 置空 text 消息
                    part.text = None
                elif part.function_call:  # 从 function_call 中提取参数
                    if not event.partial:
                        function_name = part.function_call.name
                        function_args = part.function_call.args
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] Extracting schema from function_call: '
                            f'name={function_name}, args={function_args}'
                        )
                        # 如果 function_call 的名称匹配预期的 schema，使用 args 作为 schema_info
                        # 否则，尝试从 args 中提取 tool_name 和 tool_args
                        if isinstance(function_args, dict):
                            schema_info = function_args.copy()
                            # 如果 args 中包含 tool_name，确保它被正确设置
                            if 'tool_name' not in schema_info and function_name:
                                # 尝试从 function_name 推断 tool_name
                                schema_info['tool_name'] = function_name
                        else:
                            schema_info = {
                                'tool_name': function_name,
                                'tool_args': function_args,
                            }
            if is_function_call(event) or is_function_response(
                event
            ):  # 没有被移除的 function_call: set_model_response
                yield event

            # 如果有 schema_info，保存到 state
            if schema_info and self.state_key and not event.partial:
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] Saving schema_info to state[{self.state_key}]: {schema_info}'
                )
                yield update_state_event(
                    ctx,
                    state_delta={self.state_key: schema_info},
                    event=event,
                )

        if not event_exist:
            logger.warning(
                f'[{MATMASTER_AGENT_NAME}]:[{ctx.session.id}] No event after remove_function_call'
            )


class DisallowTransferSchemaAgent(DisallowTransferMixin, SchemaAgent):
    pass
