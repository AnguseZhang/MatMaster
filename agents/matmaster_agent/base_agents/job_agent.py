import copy
import json
import logging
import os
from typing import Any, AsyncGenerator, override

import jsonpickle
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleBaseAgent,
    ErrorHandleLlmAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPAgent,
)
from agents.matmaster_agent.base_callbacks.private_callback import (
    _inject_ak,
    _inject_projectId,
)
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    JOB_LIST_KEY,
    JOB_RESULT_KEY,
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    MATMASTER_AGENT_NAME,
    SANDBOX_JOB_DETAIL_URL,
    ModelRole,
    get_BohriumExecutor,
    get_BohriumStorage,
    get_DFlowExecutor,
)
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.model import (
    BohrJobInfo,
    DFlowJobInfo,
)
from agents.matmaster_agent.prompt import (
    ResultCoreAgentDescription,
    SubmitRenderAgentDescription,
)
from agents.matmaster_agent.style import (
    tool_hallucination_card,
    tool_response_failed_card,
    tool_retry_failed_card,
)
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    context_multipart2function_event,
    context_text_event,
    display_failed_result_or_consume,
    display_future_consume_event,
    frontend_text_event,
    get_function_call_indexes,
    is_function_call,
    is_function_response,
    is_text,
    update_state_event,
)
from agents.matmaster_agent.utils.frontend import get_frontend_job_result_data
from agents.matmaster_agent.utils.helper_func import (
    is_mcp_result,
    load_tool_response,
    parse_result,
)
from agents.matmaster_agent.utils.io_oss import update_tgz_dict

logger = logging.getLogger(__name__)


class ResultMCPAgent(MCPAgent):
    @model_validator(mode='before')
    @classmethod
    def modify_description(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get('description') is None:
            data['description'] = ResultCoreAgentDescription

        return data

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )
        await self.tools[0].get_tools()
        if not ctx.session.state['dflow']:
            access_key, Executor, BohriumStorge = (
                MATERIALS_ACCESS_KEY,
                get_BohriumExecutor(),
                get_BohriumStorage(),
            )
            project_id, Executor, BohriumStorge = (
                MATERIALS_PROJECT_ID,
                Executor,
                BohriumStorge,
            )
        else:
            access_key, Executor, BohriumStorge = _inject_ak(
                ctx, get_DFlowExecutor(), get_BohriumStorage()
            )
            project_id, Executor, BohriumStorge = _inject_projectId(
                ctx, Executor, BohriumStorge
            )

        for origin_job_id in list(ctx.session.state['long_running_jobs'].keys()):
            # 检查是否需要跳过当前长运行任务的处理
            if ctx.session.state['long_running_jobs'][origin_job_id]['job_in_ctx']:
                # 获取前端业务状态中的原始ID
                frontend_origin_id = ctx.session.state[FRONTEND_STATE_KEY]['biz'].get(
                    'origin_id'
                )

                # 如果当前任务ID与前端状态中的原始ID不匹配，跳过处理
                if origin_job_id != frontend_origin_id:
                    continue

                # 如果当前调用ID与该任务的上次调用ID相同，跳过重复处理
                if (
                    ctx.session.state['long_running_jobs'][origin_job_id][
                        'last_invocation_id'
                    ]
                    == ctx.invocation_id
                ):
                    continue

            if self.tools[0].query_tool is None:
                yield context_text_event(
                    ctx, self.name, 'Query Tool is None, Failed', ModelRole
                )
                break

            query_res = await self.tools[0].query_tool.run_async(
                args={'job_id': origin_job_id, 'executor': Executor},
                tool_context=None,
            )
            if query_res.isError:
                logger.error(f'[{MATMASTER_AGENT_NAME}] {query_res.content[0].text}')
                raise RuntimeError(query_res.content[0].text)
            status = query_res.content[0].text
            logger.info(
                f'[{MATMASTER_AGENT_NAME}]:[{self.name}] origin_job_id = {origin_job_id}, executor = {Executor}, '
                f'status = {status}'
            )
            if status != 'Running':
                update_plan = copy.deepcopy(ctx.session.state['plan'])
                if status == 'Succeeded':
                    plan_status = 'success'
                else:
                    plan_status = 'failed'
                update_plan['steps'][ctx.session.state['plan_index']][
                    'status'
                ] = plan_status

                update_long_running_jobs = copy.deepcopy(
                    ctx.session.state['long_running_jobs']
                )
                update_long_running_jobs[origin_job_id]['job_status'] = status
                yield update_state_event(
                    ctx,
                    state_delta={
                        'long_running_jobs': update_long_running_jobs,
                        'plan': update_plan,
                    },
                )
                results_res = await self.tools[0].results_tool.run_async(
                    args={
                        'job_id': origin_job_id,
                        'executor': Executor,
                        'storage': BohriumStorge,
                    },
                    tool_context=None,
                )
                if results_res.isError:  # Job Result Retrival Failed
                    err_msg = results_res.content[0].text
                    if err_msg.startswith('Error executing tool'):
                        err_msg = err_msg[err_msg.find(':') + 2 :]
                    yield frontend_text_event(
                        ctx,
                        self.name,
                        f"Job {origin_job_id} failed: {err_msg}",
                        ModelRole,
                    )
                elif status == 'Failed':  # Job Failed
                    pass
                else:  # Job Success
                    raw_result = results_res.content[0].text
                    dict_result = jsonpickle.loads(raw_result)
                    logger.info(
                        f"[{MATMASTER_AGENT_NAME}]:[{self.name}] dict_result = {dict_result}"
                    )

                    if self.enable_tgz_unpack:
                        tgz_flag, new_tool_result = await update_tgz_dict(dict_result)
                    else:
                        new_tool_result = dict_result
                    update_long_running_jobs = copy.deepcopy(
                        ctx.session.state['long_running_jobs']
                    )
                    update_long_running_jobs[origin_job_id]['job_result'] = (
                        await parse_result(new_tool_result)
                    )
                    yield update_state_event(
                        ctx,
                        state_delta={'long_running_jobs': update_long_running_jobs},
                    )
                    job_result_comp_data = get_frontend_job_result_data(
                        ctx.session.state['long_running_jobs'][origin_job_id][
                            'job_result'
                        ]
                    )

                    # Only for debug
                    if os.getenv('MODE', None) == 'debug':
                        ctx.session.state[FRONTEND_STATE_KEY]['biz'][
                            'origin_id'
                        ] = origin_job_id

                    # 如果用户请求这个id的任务结果，渲染前端组件
                    if origin_job_id == ctx.session.state[FRONTEND_STATE_KEY][
                        'biz'
                    ].get('origin_id', None):
                        for event in all_text_event(
                            ctx,
                            self.name,
                            f"<bohrium-chat-msg>{json.dumps(job_result_comp_data)}</bohrium-chat-msg>",
                            ModelRole,
                        ):
                            yield event

                        # Only for debug
                        if os.getenv('MODE', None) == 'debug':
                            ctx.session.state[FRONTEND_STATE_KEY]['biz'][
                                'origin_id'
                            ] = None

                    # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                    for event in context_function_event(
                        ctx,
                        self.name,
                        'system_job_result',
                        {
                            JOB_RESULT_KEY: ctx.session.state['long_running_jobs'][
                                origin_job_id
                            ]['job_result']
                        },
                        ModelRole,
                    ):
                        yield event

                update_long_running_jobs = copy.deepcopy(
                    ctx.session.state['long_running_jobs']
                )
                update_long_running_jobs[origin_job_id]['job_in_ctx'] = True
                update_long_running_jobs[origin_job_id][
                    'last_invocation_id'
                ] = ctx.invocation_id
                yield update_state_event(
                    ctx,
                    state_delta={'long_running_jobs': update_long_running_jobs},
                )
            # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
            for event in context_function_event(
                ctx,
                self.name,
                'system_job_status',
                {'msg': f"Job {origin_job_id} status is {status}"},
                ModelRole,
            ):
                yield event
        yield Event(author=self.name)


class ParamsCheckInfoAgent(ErrorHandleLlmAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
            if not event.partial:
                for system_job_result_event in context_function_event(
                    ctx,
                    self.name,
                    'system_params_check',
                    {'msg': event.content.parts[0].text},
                    ModelRole,
                ):
                    yield system_job_result_event


class SubmitCoreMCPAgent(MCPAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )
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
                parsed_result = await parse_result(new_tool_result)
                job_result_comp_data = get_frontend_job_result_data(parsed_result)

                for frontend_job_result_event in all_text_event(
                    ctx,
                    self.name,
                    f"<bohrium-chat-msg>{json.dumps(job_result_comp_data)}</bohrium-chat-msg>",
                    ModelRole,
                ):
                    yield frontend_job_result_event

                # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                for db_job_result_event in context_function_event(
                    ctx,
                    self.name,
                    'system_job_result',
                    {JOB_RESULT_KEY: parsed_result},
                    ModelRole,
                ):
                    yield db_job_result_event
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
            if is_text(event):
                if not event.partial:
                    for multi_part_event in context_multipart2function_event(
                        ctx, self.name, event, 'matmaster_submit_core_info'
                    ):
                        yield multi_part_event
            else:
                yield event


class SubmitRenderAgent(ErrorHandleLlmAgent):
    @model_validator(mode='before')
    @classmethod
    def modify_description(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get('description') is None:
            data['description'] = SubmitRenderAgentDescription

        return data

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )
        async for event in super()._run_events(ctx):
            if is_text(event) and ctx.session.state['render_job_list']:
                for cur_render_job_id in ctx.session.state['render_job_id']:
                    # Render Frontend Job-List Component
                    job_list_comp_data = {
                        'eventType': 1,
                        'eventData': {
                            'contentType': 1,
                            'renderType': '@bohrium-chat/matmodeler/task-message',
                            'content': {
                                JOB_LIST_KEY: ctx.session.state['long_running_jobs'][
                                    cur_render_job_id
                                ]
                            },
                        },
                    }
                    if not ctx.session.state['dflow']:
                        # 同时发送流式消息（聊条的时候可见）和数据库消息（历史记录的时候可见）
                        for event in all_text_event(
                            ctx=ctx,
                            author=self.name,
                            text=f"<bohrium-chat-msg>{json.dumps(job_list_comp_data)}</bohrium-chat-msg>",
                            role=ModelRole,
                        ):
                            yield event

                yield update_state_event(
                    ctx, state_delta={'render_job_list': False, 'render_job_id': []}
                )


class SubmitValidatorAgent(ErrorHandleBaseAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        if ctx.session.state['error_occurred']:
            return

        if (
            ctx.session.state['long_running_jobs_count']
            > ctx.session.state['long_running_jobs_count_ori']
        ):
            yield update_state_event(
                ctx,
                state_delta={
                    'long_running_jobs_count_ori': ctx.session.state[
                        'long_running_jobs_count'
                    ],
                    'tool_hallucination': False,
                },
            )
            yield Event(author=self.name)
        else:
            if not ctx.session.state['tool_hallucination']:  # 第一次重试
                message = tool_hallucination_card(i18n=i18n)
                yield update_state_event(
                    ctx,
                    state_delta={
                        'tool_hallucination': True,
                    },
                )
            else:  # 第二次重试
                message = tool_retry_failed_card(i18n=i18n)

            for tool_hallucination_event in all_text_event(
                ctx,
                self.name,
                message,
                ModelRole,
            ):
                yield tool_hallucination_event

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} state = {ctx.session.state}'
        )
