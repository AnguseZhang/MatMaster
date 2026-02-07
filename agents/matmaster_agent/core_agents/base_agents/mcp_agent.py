import copy
import logging
from typing import Any, AsyncGenerator, Optional, cast

from google.adk.agents import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import model_validator

from agents.matmaster_agent.base_callbacks.private_callback import (
    catch_after_tool_callback_error,
    catch_before_tool_callback_error,
    check_before_tool_callback_effect,
    check_user_phonon_balance,
    default_after_model_callback,
    default_after_tool_callback,
    default_before_model_callback,
    default_before_tool_callback,
    default_cost_func,
    filter_function_calls,
    inject_ak_projectId,
    inject_current_env,
    inject_userId_sessionId,
    inject_username_ticket,
    remove_job_link,
    tgz_oss_to_oss_list,
    update_tool_args,
)
from agents.matmaster_agent.config import USE_PHOTON
from agents.matmaster_agent.constant import (
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    MATMASTER_AGENT_NAME,
    TMP_FRONTEND_STATE_KEY,
    ModelRole,
)
from agents.matmaster_agent.core_agents.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.core_agents.base_agents.error_agent import (
    ErrorHandleLlmAgent,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.memory.inject_memory_callback import (
    inject_memory_before_model,
)
from agents.matmaster_agent.memory.store_tool_result_callback import (
    store_tool_result_in_memory,
)
from agents.matmaster_agent.model import CostFuncType
from agents.matmaster_agent.state import CURRENT_STEP, CURRENT_STEP_RESULT
from agents.matmaster_agent.style import tool_response_failed_card
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_multipart2function_event,
    display_failed_result_or_consume,
    display_future_consume_event,
    frontend_render_event,
    is_function_call,
    is_function_response,
    is_text,
    update_state_event,
)
from agents.matmaster_agent.utils.helper_func import (
    is_mcp_result,
    load_tool_response,
)
from agents.matmaster_agent.utils.result_parse_utils import (
    parse_result,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class MCPInitMixin(BaseMixin):
    loading: bool = False  # Whether the agent display loading state
    render_tool_response: bool = True  # Whether render tool response in frontend
    enable_tgz_unpack: bool = True  # Whether unpack tgz files for tool_results
    cost_func: Optional[CostFuncType] = None
    enforce_single_function_call: bool = True  # 是否只允许单个 function_call


def mcp_callback_model_validator(data: Any):
    if not isinstance(data, dict):
        return data

    if data.get('after_model_callback') is None:
        data['after_model_callback'] = default_after_model_callback

    if data.get('before_model_callback') is None:
        data['before_model_callback'] = default_before_model_callback
    data['before_model_callback'] = inject_memory_before_model(
        data['before_model_callback']
    )

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

    pipeline = inject_ak_projectId(data['before_tool_callback'])
    pipeline = inject_userId_sessionId(pipeline)

    if USE_PHOTON:
        pipeline = check_user_phonon_balance(pipeline, data['cost_func'])

    # pipeline = check_job_create(pipeline)
    pipeline = inject_username_ticket(pipeline)
    pipeline = inject_current_env(pipeline)

    data['before_tool_callback'] = catch_before_tool_callback_error(pipeline)

    data['after_tool_callback'] = store_tool_result_in_memory(
        check_before_tool_callback_effect(
            catch_after_tool_callback_error(
                remove_job_link(
                    tgz_oss_to_oss_list(
                        data['after_tool_callback'], data['enable_tgz_unpack']
                    )
                )
            )
        )
    )

    return data


class MCPCallbackMixin(BaseMixin):
    @model_validator(mode='before')
    @classmethod
    def decorate_callbacks(cls, data: Any) -> Any:
        return mcp_callback_model_validator(data)


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
                            raise RuntimeError(
                                f'Tool Execution Failed: {tool_response["result"].content[0].text}'
                            )
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

                    parsed_tool_result = await parse_result(ctx, dict_result)
                    post_execution_step = copy.deepcopy(ctx.session.state[CURRENT_STEP])
                    post_execution_step[CURRENT_STEP_RESULT] = parsed_tool_result
                    yield update_state_event(
                        ctx, state_delta={CURRENT_STEP: post_execution_step}
                    )
                    for _frontend_render_event in frontend_render_event(
                        ctx,
                        event,
                        self.name,
                        parsed_tool_result,
                        render_tool_response=self.render_tool_response,
                    ):
                        yield _frontend_render_event
                # Send Normal LlmResponse to Frontend, function_call -> function_response -> Llm_response
                if is_text(event) and is_function_call(event):
                    if not event.partial:
                        for multi_part_event in context_multipart2function_event(
                            ctx, self.name, event, 'matmaster_sync_mcp_event'
                        ):
                            yield multi_part_event
                elif is_text(event):
                    if (
                        not event.partial
                        and event.content.parts[0].text
                        == 'All Function Calls Are Occurred Before, Continue'
                        and ctx.session.state[CURRENT_STEP]['status']
                        == PlanStepStatusEnum.PROCESS
                    ):
                        for _info_event in all_text_event(
                            ctx, self.name, '工具参数无变化，本次跳过执行', ModelRole
                        ):
                            yield _info_event
                        update_plan = copy.deepcopy(ctx.session.state['plan'])
                        update_plan['steps'][ctx.session.state['plan_index']][
                            'status'
                        ] = PlanStepStatusEnum.FAILED
                        yield update_state_event(ctx, state_delta={'plan': update_plan})
                else:
                    yield event


class MCPAgent(MCPInitMixin, MCPCallbackMixin, ErrorHandleLlmAgent):
    pass
