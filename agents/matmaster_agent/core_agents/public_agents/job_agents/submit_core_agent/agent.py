import copy
import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.config import USE_PHOTON
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    SANDBOX_JOB_DETAIL_URL,
    ModelRole,
)
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_mcp_agent import (
    DisallowTransferAndContentLimitMCPAgent,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.model import BohrJobInfo, DFlowJobInfo
from agents.matmaster_agent.state import PLAN
from agents.matmaster_agent.style import tool_response_failed_card
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_multipart2function_event,
    display_failed_result_or_consume,
    display_future_consume_event,
    frontend_render_event,
    get_function_call_indexes,
    is_function_call,
    is_function_response,
    is_text,
    update_state_event,
)
from agents.matmaster_agent.utils.helper_func import (
    is_mcp_result,
    load_tool_response,
)
from agents.matmaster_agent.utils.io_oss import update_tgz_dict
from agents.matmaster_agent.utils.result_parse_utils import (
    parse_result,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class SubmitCoreMCPAgent(DisallowTransferAndContentLimitMCPAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"{ctx.session.id} state: {ctx.session.state}")
        async for event in super()._run_events(ctx):
            # Only For Sync Tool Call
            if (
                is_function_call(event)
                and ctx.session.state['sync_tools']
                and (function_indexes := get_function_call_indexes(event))
                and event.content.parts[function_indexes[0]].function_call.name
                in ctx.session.state['sync_tools']
            ):
                event.long_running_tool_ids = None  # Untag Async Job
                yield update_state_event(
                    ctx,
                    state_delta={
                        'long_running_jobs_count': ctx.session.state[
                            'long_running_jobs_count'
                        ]
                        + 1
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

            if (
                is_function_response(event)
                and ctx.session.state['sync_tools']
                and event.content.parts[0].function_response.name
                in ctx.session.state['sync_tools']
            ):
                try:
                    first_part = event.content.parts[0]
                    tool_response = first_part.function_response.response
                    if (
                        is_mcp_result(tool_response) and tool_response['result'].isError
                    ):  # Original MCPResult & Error
                        for tool_response_failed_event in all_text_event(
                            ctx,
                            self.name,
                            f"{tool_response_failed_card(i18n=i18n)}",
                            ModelRole,
                        ):
                            yield tool_response_failed_event

                        # 更新 plan 为失败
                        update_plan = copy.deepcopy(ctx.session.state['plan'])
                        update_plan['steps'][ctx.session.state['plan_index']][
                            'status'
                        ] = 'failed'
                        yield update_state_event(ctx, state_delta={'plan': update_plan})

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

                if self.enable_tgz_unpack:
                    tgz_flag, new_tool_result = await update_tgz_dict(dict_result)
                else:
                    new_tool_result = dict_result

                parsed_tool_result = await parse_result(ctx, new_tool_result)
                logger.info(
                    f'{ctx.session.id} parsed_tool_result = {parsed_tool_result}'
                )
                for _frontend_render_event in frontend_render_event(
                    ctx,
                    event,
                    self.name,
                    parsed_tool_result,
                    render_tool_response=self.render_tool_response,
                ):
                    yield _frontend_render_event
            # END

            # Only for Long Running Tools Call
            if event.long_running_tool_ids and is_function_call(event):
                yield update_state_event(
                    ctx,
                    state_delta={
                        'long_running_ids': ctx.session.state['long_running_ids']
                        + list(event.long_running_tool_ids)
                    },
                    event=event,
                )

                if USE_PHOTON:
                    # prompt user tool-call cost
                    cost_func = self.cost_func
                    async for future_consume_event in display_future_consume_event(
                        event, cost_func, ctx, self.name
                    ):
                        yield future_consume_event

            if event.content and event.content.parts:
                for part in event.content.parts:
                    if (
                        part
                        and part.function_response
                        and part.function_response.id
                        in ctx.session.state['long_running_ids']
                        and 'result' in part.function_response.response
                    ):
                        # exist tool-call, long_running_jobs_count+1
                        yield update_state_event(
                            ctx,
                            state_delta={
                                'long_running_jobs_count': ctx.session.state[
                                    'long_running_jobs_count'
                                ]
                                + 1,
                            },
                        )
                        try:
                            tool_response = part.function_response.response
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

                                # 更新 plan 为失败
                                update_plan = copy.deepcopy(ctx.session.state['plan'])
                                update_plan['steps'][ctx.session.state['plan_index']][
                                    'status'
                                ] = 'failed'
                                yield update_state_event(
                                    ctx, state_delta={'plan': update_plan}
                                )

                                raise RuntimeError('Tool Execution Failed')
                            dict_result = load_tool_response(part)
                            async for (
                                failed_or_consume_event
                            ) in display_failed_result_or_consume(
                                dict_result, ctx, self.name, event
                            ):
                                yield failed_or_consume_event
                        except BaseException:
                            yield event
                            raise

                        origin_job_id = dict_result['job_id']
                        job_name = part.function_response.name
                        job_status = dict_result['status']
                        if not ctx.session.state['dflow']:  # Non-Dflow Job
                            bohr_job_id = dict_result['extra_info']['bohr_job_id']
                            job_detail_url = f'{SANDBOX_JOB_DETAIL_URL}/{bohr_job_id}'
                            frontend_result = BohrJobInfo(
                                origin_job_id=origin_job_id,
                                job_name=job_name,
                                job_status=job_status,
                                job_id=bohr_job_id,
                                job_detail_url=job_detail_url,
                                agent_name=ctx.agent.name.replace('_submit_core', ''),
                            ).model_dump(mode='json')
                        else:  # Dflow Job (Deprecated)
                            workflow_id = dict_result['extra_info']['workflow_id']
                            workflow_uid = dict_result['extra_info']['workflow_uid']
                            workflow_url = dict_result['extra_info']['workflow_link']
                            frontend_result = DFlowJobInfo(
                                origin_job_id=origin_job_id,
                                job_name=job_name,
                                job_status=job_status,
                                workflow_id=workflow_id,
                                workflow_uid=workflow_uid,
                                workflow_url=workflow_url,
                            ).model_dump(mode='json')

                        update_long_running_jobs = copy.deepcopy(
                            ctx.session.state['long_running_jobs']
                        )
                        update_long_running_jobs[origin_job_id] = frontend_result
                        yield update_state_event(
                            ctx,
                            state_delta={
                                'long_running_jobs': update_long_running_jobs,
                                'render_job_list': True,
                                'render_job_id': ctx.session.state['render_job_id']
                                + [origin_job_id],
                            },
                        )
            # END

            # Send Normal LlmResponse to Frontend, function_call -> function_response -> Llm_response
            if is_text(event) and is_function_call(event):
                if not event.partial:
                    for multi_part_event in context_multipart2function_event(
                        ctx, self.name, event, 'matmaster_submit_core_info'
                    ):
                        yield multi_part_event
            elif is_text(event):
                if (
                    not event.partial
                    and event.content.parts[0].text
                    == 'All Function Calls Are Occurred Before, Continue'
                    and ctx.session.state[PLAN]['steps'][
                        ctx.session.state['plan_index']
                    ]['status']
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
