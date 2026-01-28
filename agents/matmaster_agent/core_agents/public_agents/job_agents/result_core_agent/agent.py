import copy
import json
import logging
import os
from typing import Any, AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.base_callbacks.private_callback import (
    _inject_ak,
    _inject_projectId,
)
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    JOB_RESULT_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
    get_BohriumExecutor,
    get_BohriumStorage,
    get_DFlowExecutor,
)
from agents.matmaster_agent.core_agents.base_agents.mcp_agent import MCPAgent
from agents.matmaster_agent.core_agents.public_agents.job_agents.result_core_agent.prompt import (
    ResultCoreAgentDescription,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.services.job import (
    get_job_detail,
    parse_and_prepare_err,
    parse_and_prepare_results,
)
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    update_state_event,
)
from agents.matmaster_agent.utils.io_oss import update_tgz_dict
from agents.matmaster_agent.utils.job_utils import mapping_status
from agents.matmaster_agent.utils.result_parse_utils import (
    csv_to_markdown_table,
    get_csv_result,
    get_echarts_result,
    get_kv_result,
    get_markdown_image_result,
    get_matrix_result,
    matrix_to_markdown_table,
    parse_result,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


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
        logger.info(f"{ctx.session.id} state: {ctx.session.state}")
        if not ctx.session.state['dflow']:
            access_key, Executor, BohriumStorge = _inject_ak(
                ctx, get_BohriumExecutor(), get_BohriumStorage()
            )
            project_id, Executor, BohriumStorge = await _inject_projectId(
                ctx, Executor, BohriumStorge
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

            job_id = ctx.session.state['long_running_jobs'][origin_job_id]['job_id']
            query_res = await get_job_detail(job_id=job_id, access_key=access_key)
            status = mapping_status(query_res.get('data', {}).get('status', -999))
            logger.info(
                f'{ctx.session.id} origin_job_id = {origin_job_id}, executor = {Executor}, '
                f'status = {status}'
            )
            if status != 'Running':
                # 更新状态
                plan_status = 'success' if status == 'Finished' else 'failed'
                update_plan = copy.deepcopy(ctx.session.state['plan'])
                logger.info(
                    f'{ctx.session.id} plan_index = {ctx.session.state['plan_index']}'
                )
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

                # 获取任务结果
                if status == 'Failed':  # Job Failed
                    dict_result = await parse_and_prepare_err(
                        job_id=job_id, access_key=access_key
                    )
                else:  # Job Success
                    dict_result = await parse_and_prepare_results(
                        job_id=job_id, access_key=access_key
                    )
                logger.info(f"{ctx.session.id} dict_result = {dict_result}")

                if self.enable_tgz_unpack:
                    tgz_flag, new_tool_result = await update_tgz_dict(
                        dict_result, session_id=ctx.session.id
                    )
                else:
                    new_tool_result = dict_result
                parsed_tool_result = await parse_result(ctx, new_tool_result)
                logger.info(
                    f'{ctx.session.id} parsed_tool_result = {parsed_tool_result}'
                )

                update_long_running_jobs = copy.deepcopy(
                    ctx.session.state['long_running_jobs']
                )
                update_long_running_jobs[origin_job_id][
                    'job_result'
                ] = parsed_tool_result
                yield update_state_event(
                    ctx,
                    state_delta={'long_running_jobs': update_long_running_jobs},
                )

                # Only for debug
                if os.getenv('MODE', None) == 'debug':
                    ctx.session.state[FRONTEND_STATE_KEY]['biz'][
                        'origin_id'
                    ] = origin_job_id

                # 如果用户请求这个id的任务结果，渲染前端组件
                if origin_job_id == ctx.session.state[FRONTEND_STATE_KEY]['biz'].get(
                    'origin_id', None
                ):
                    job_result_comp_data = get_kv_result(
                        ctx.session.state['long_running_jobs'][origin_job_id][
                            'job_result'
                        ]
                    )
                    for event in all_text_event(
                        ctx,
                        self.name,
                        f"<bohrium-chat-msg>{json.dumps(job_result_comp_data)}</bohrium-chat-msg>",
                        ModelRole,
                    ):
                        yield event

                    # 渲染 Markdown 图片
                    markdown_image_result = get_markdown_image_result(
                        parsed_tool_result
                    )
                    if markdown_image_result:
                        for item in markdown_image_result:
                            for markdown_image_event in all_text_event(
                                ctx, self.name, item['data'], ModelRole
                            ):
                                yield markdown_image_event

                    # 渲染 Matrix 结果
                    matrix_result = get_matrix_result(parsed_tool_result)
                    if matrix_result:
                        for item in matrix_result:
                            for markdown_matrix_event in all_text_event(
                                ctx,
                                self.name,
                                matrix_to_markdown_table(item),
                                ModelRole,
                            ):
                                yield markdown_matrix_event

                    # 渲染 echarts
                    echarts_result = get_echarts_result(parsed_tool_result)
                    if echarts_result:
                        for echarts_event in context_function_event(
                            ctx,
                            self.name,
                            'matmaster_echarts',
                            None,
                            ModelRole,
                            {'echarts_url': [item['url'] for item in echarts_result]},
                        ):
                            yield echarts_event

                    # 渲染 csv
                    csv_result = get_csv_result(parsed_tool_result)
                    if csv_result:
                        for item in csv_result:
                            for csv_event in all_text_event(
                                ctx,
                                self.name,
                                await csv_to_markdown_table(item['url']),
                                ModelRole,
                            ):
                                yield csv_event

                    # Only for debug
                    if os.getenv('MODE', None) == 'debug':
                        ctx.session.state[FRONTEND_STATE_KEY]['biz']['origin_id'] = None

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
        yield Event(author=self.name, invocation_id=ctx.invocation_id)
