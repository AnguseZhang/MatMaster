import json
import logging
from typing import Any, AsyncGenerator, Optional, cast

from google.adk.agents import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import model_validator

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_callbacks.private_callback import (
    catch_after_tool_callback_error,
    catch_before_tool_callback_error,
    check_before_tool_callback_effect,
    check_job_create,
    check_user_phonon_balance,
    default_after_model_callback,
    default_after_tool_callback,
    default_before_tool_callback,
    default_cost_func,
    filter_function_calls,
    inject_current_env,
    inject_userId_sessionId,
    inject_username_ticket,
    remove_job_link,
    tgz_oss_to_oss_list,
    update_tool_args,
)
from agents.matmaster_agent.constant import (
    JOB_RESULT_KEY,
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    MATMASTER_AGENT_NAME,
    TMP_FRONTEND_STATE_KEY,
    ModelRole,
)
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.model import CostFuncType
from agents.matmaster_agent.setting import USE_PHOTON
from agents.matmaster_agent.style import tool_response_failed_card
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    context_multipart2function_event,
    display_failed_result_or_consume,
    display_future_consume_event,
    is_function_call,
    is_function_response,
    is_text,
    update_state_event,
)
from agents.matmaster_agent.utils.frontend import get_frontend_job_result_data
from agents.matmaster_agent.utils.helper_func import (
    get_markdown_image_result,
    is_mcp_result,
    load_tool_response,
    parse_result,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MCPInitMixin(BaseMixin):
    loading: bool = False  # Whether the agent display loading state
    render_tool_response: bool = False  # Whether render tool response in frontend
    enable_tgz_unpack: bool = True  # Whether unpack tgz files for tool_results
    cost_func: Optional[CostFuncType] = None
    enforce_single_function_call: bool = True  # 是否只允许单个 function_call


class MCPCallbackMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get('after_model_callback') is None:
            data['after_model_callback'] = default_after_model_callback

        if data.get('before_tool_callback') is None:
            data['before_tool_callback'] = default_before_tool_callback

        if data.get('after_tool_callback') is None:
            data['after_tool_callback'] = default_after_tool_callback

        if data.get('cost_func') is None:
            data['cost_func'] = default_cost_func

        if data.get('enable_tgz_unpack') is None:
            data['enable_tgz_unpack'] = True

        if data.get('enforce_single_function_call') is None:
            data['enforce_single_function_call'] = True

        data['after_model_callback'] = update_tool_args(
            filter_function_calls(
                data['after_model_callback'],
                enforce_single_function_call=data['enforce_single_function_call'],
            )
        )

        pipeline = inject_userId_sessionId(data['before_tool_callback'])

        if USE_PHOTON:
            pipeline = check_user_phonon_balance(pipeline, data['cost_func'])

        pipeline = check_job_create(pipeline)
        pipeline = inject_username_ticket(pipeline)
        pipeline = inject_current_env(pipeline)

        data['before_tool_callback'] = catch_before_tool_callback_error(pipeline)

        data['after_tool_callback'] = check_before_tool_callback_effect(
            catch_after_tool_callback_error(
                remove_job_link(
                    tgz_oss_to_oss_list(
                        data['after_tool_callback'], data['enable_tgz_unpack']
                    )
                )
            )
        )

        return data


class MCPRunEventsMixin(BaseMixin):
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        parent = super()
        if hasattr(parent, '_run_events'):
            _run_events = cast(Any, parent)._run_events
            async for event in _run_events(ctx):
                if is_function_call(event):
                    if self.loading:
                        loading_title_msg = (
                            f"正在调用 {event.content.parts[0].function_call.name}..."
                        )
                        loading_desc_msg = '结果生成中，请稍等片刻...'
                        logger.info(loading_title_msg)
                        yield Event(
                            author=self.name,
                            actions=EventActions(
                                state_delta={
                                    TMP_FRONTEND_STATE_KEY: {
                                        LOADING_STATE_KEY: LOADING_START,
                                        LOADING_TITLE: loading_title_msg,
                                        LOADING_DESC: loading_desc_msg,
                                    }
                                }
                            ),
                        )
                    # update state: `tools_count`, `invocation_id_with_tool_call`
                    yield update_state_event(
                        ctx,
                        state_delta={
                            'tools_count': ctx.session.state['tools_count'] + 1,
                        },
                        event=event,
                    )
                    if USE_PHOTON:
                        # prompt user photon cost
                        cost_func = self.cost_func
                        async for future_consume_event in display_future_consume_event(
                            event, cost_func, ctx, self.name
                        ):
                            yield future_consume_event
                elif is_function_response(event):
                    # Loading Event
                    if self.loading:
                        logger.info(
                            f"{event.content.parts[0].function_response.name} 调用结束"
                        )
                        yield Event(
                            author=self.name,
                            actions=EventActions(
                                state_delta={
                                    TMP_FRONTEND_STATE_KEY: {
                                        LOADING_STATE_KEY: LOADING_END
                                    }
                                }
                            ),
                        )

                    # Parse Tool Response
                    try:
                        first_part = event.content.parts[0]
                        tool_response = first_part.function_response.response
                        if (
                            is_mcp_result(tool_response)
                            and tool_response['result'].isError
                        ):  # Original MCPResult & Error
                            for tool_response_failed_event in all_text_event(
                                ctx,
                                self.name,
                                f"{tool_response_failed_card(i18n=i18n)}",
                                ModelRole,
                            ):
                                yield tool_response_failed_event
                            raise RuntimeError('Tool Execution Failed')
                        dict_result = load_tool_response(first_part)
                        async for (
                            failed_or_consume_event
                        ) in display_failed_result_or_consume(
                            dict_result, ctx, self.name, event
                        ):
                            yield failed_or_consume_event
                    except BaseException:
                        yield event
                        raise

                    job_result = await parse_result(dict_result)
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} job_result = {job_result}'
                    )
                    markdown_image_result = get_markdown_image_result(job_result)
                    job_result_comp_data = get_frontend_job_result_data(job_result)

                    # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                    for system_job_result_event in context_function_event(
                        ctx,
                        self.name,
                        'matmaster_job_result',
                        {JOB_RESULT_KEY: job_result},
                        ModelRole,
                    ):
                        yield system_job_result_event

                    # Render Tool Response Event
                    if self.render_tool_response:
                        for result_event in all_text_event(
                            ctx,
                            self.name,
                            f"<bohrium-chat-msg>{json.dumps(job_result_comp_data)}</bohrium-chat-msg>",
                            ModelRole,
                        ):
                            yield result_event

                    if markdown_image_result:
                        for item in markdown_image_result:
                            for markdown_image_event in all_text_event(
                                ctx, self.name, item['data'], ModelRole
                            ):
                                yield markdown_image_event

                if is_text(event):
                    if not event.partial:
                        for multi_part_event in context_multipart2function_event(
                            ctx, self.name, event, 'matmaster_sync_mcp_event'
                        ):
                            yield multi_part_event
                else:
                    yield event


class MCPAgent(MCPInitMixin, MCPCallbackMixin, ErrorHandleLlmAgent):
    pass
