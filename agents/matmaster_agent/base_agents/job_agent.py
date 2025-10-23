import copy
import json
import logging
import os
from typing import AsyncGenerator, Optional, override

import jsonpickle
import litellm
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import Field

from agents.matmaster_agent.base_agents.callback import (
    _inject_ak,
    _inject_projectId,
    catch_after_tool_callback_error,
    catch_before_tool_callback_error,
    check_before_tool_callback_effect,
    check_job_create,
    default_after_model_callback,
    default_after_tool_callback,
    default_before_tool_callback,
    inject_current_env,
    inject_userId_sessionId,
    inject_username_ticket,
    remove_function_call,
    remove_job_link,
    tgz_oss_to_oss_list,
)
from agents.matmaster_agent.base_agents.io_agent import HandleFileUploadLlmAgent
from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    JOB_LIST_KEY,
    JOB_RESULT_KEY,
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    MATMASTER_AGENT_NAME,
    SANDBOX_JOB_DETAIL_URL,
    TMP_FRONTEND_STATE_KEY,
    ModelRole,
    get_BohriumExecutor,
    get_BohriumStorage,
    get_DFlowExecutor,
)
from agents.matmaster_agent.model import BohrJobInfo, DFlowJobInfo, ParamsCheckComplete
from agents.matmaster_agent.prompt import (
    ResultCoreAgentDescription,
    SubmitRenderAgentDescription,
    gen_params_check_completed_agent_instruction,
    gen_params_check_info_agent_instruction,
    gen_result_agent_description,
    gen_result_core_agent_instruction,
    gen_submit_agent_description,
    gen_submit_core_agent_description,
    gen_submit_core_agent_instruction,
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    cherry_pick_events,
    context_function_event,
    context_multipart2function_event,
    context_text_event,
    frontend_text_event,
    get_function_call_indexes,
    is_function_call,
    is_function_response,
    is_text,
    send_error_event,
    update_state_event,
)
from agents.matmaster_agent.utils.frontend import get_frontend_job_result_data
from agents.matmaster_agent.utils.helper_func import (
    get_session_state,
    load_tool_response,
    parse_result,
)
from agents.matmaster_agent.utils.io_oss import update_tgz_dict

logger = logging.getLogger(__name__)


class CalculationMCPLlmAgent(HandleFileUploadLlmAgent):
    """An LLM agent specialized for calculation tasks with built-in error handling and project ID management.

    Extends the HandleFileUploadLlmAgent with additional features:
    - Automatic error handling for tool calls
    - Project ID retrieval before tool execution
    - OpikTracer integration for comprehensive operation tracing

    Note: User-provided callbacks will execute before the built-in OpikTracer callbacks.

    Attributes:
        Inherits all attributes from LlmAgent.
    """

    loading: bool = Field(
        False, description='Whether the agent display loading state', exclude=True
    )
    render_tool_response: bool = Field(
        False, description='Whether render tool response in frontend', exclude=True
    )
    supervisor_agent: Optional[str] = Field(
        None, description='Which one is the supervisor_agent'
    )
    enable_tgz_unpack: bool = Field(
        True, description='Whether unpack tgz files for tool_results'
    )

    def __init__(
        self,
        model,
        name,
        instruction='',
        description='',
        sub_agents=None,
        global_instruction='',
        tools=None,
        output_key=None,
        before_agent_callback=None,
        before_model_callback=None,
        before_tool_callback=default_before_tool_callback,
        after_tool_callback=default_after_tool_callback,
        after_model_callback=default_after_model_callback,
        after_agent_callback=None,
        loading=False,
        render_tool_response=False,
        disallow_transfer_to_parent=False,
        supervisor_agent=None,
        enable_tgz_unpack=True,
    ):
        """Initialize a CalculationLlmAgent with enhanced tool call capabilities.

        Args:
            model: The language model instance to be used by the agent
            name: Unique identifier for the agent
            instruction: Primary instruction guiding the agent's behavior
            description: Optional detailed description of the agent (default: '')
            sub_agents: List of subordinate agents (default: None)
            global_instruction: Instruction applied across all agent operations (default: '')
            tools: Tools available to the agent (default: None)
            output_key: Key for identifying the agent's output (default: None)
            before_agent_callback: Callback executed before agent runs (default: None)
            before_model_callback: Callback executed before model inference (default: None)
            before_tool_callback: Callback executed before tool execution
                                (default: default_before_tool_callback)
            after_tool_callback: Callback executed after tool execution (default: None)
            after_model_callback: Callback executed after model inference (default: None)
            after_agent_callback: Callback executed after agent completes (default: None)

        Implementation Notes:
            1. Wraps the before_tool_callback with:
               - Error handling (catch_tool_call_error)
               - Project ID retrieval (get_ak_projectId)
            2. Maintains callback execution order: user callbacks → OpikTracer callbacks
            3. Designed specifically for calculation-intensive MCP workflows
        """

        # Todo: support List[before_tool_callback]
        before_tool_callback = catch_before_tool_callback_error(
            check_job_create(
                inject_current_env(
                    inject_username_ticket(
                        inject_userId_sessionId(before_tool_callback)
                    )
                )
            )
        )
        after_tool_callback = check_before_tool_callback_effect(
            catch_after_tool_callback_error(
                remove_job_link(
                    tgz_oss_to_oss_list(after_tool_callback, enable_tgz_unpack)
                )
            )
        )

        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction,
            global_instruction=global_instruction,
            sub_agents=sub_agents or [],
            tools=tools or [],
            output_key=output_key,
            before_agent_callback=before_agent_callback,
            before_model_callback=before_model_callback,
            before_tool_callback=before_tool_callback,
            after_tool_callback=after_tool_callback,
            after_model_callback=after_model_callback,
            after_agent_callback=after_agent_callback,
            disallow_transfer_to_parent=disallow_transfer_to_parent,
            supervisor_agent=supervisor_agent,
            enable_tgz_unpack=enable_tgz_unpack,
        )

        self.loading = loading
        self.render_tool_response = render_tool_response
        self.supervisor_agent = supervisor_agent
        self.enable_tgz_unpack = enable_tgz_unpack

    # Execution Order: user_question -> chembrain_llm -> event -> user_agree_transfer -> retrosyn_llm (param) -> event
    #                  -> user_agree_param -> retrosyn_llm (function_call) -> event -> tool_call
    #                  -> retrosyn_llm (function_response) -> event
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            async for event in super()._run_async_impl(ctx):
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
                    if not isinstance(self, SubmitCoreCalculationMCPLlmAgent):
                        try:
                            dict_result = load_tool_response(event)
                        except BaseException:
                            yield event
                            raise

                        job_result = await parse_result(dict_result)
                        job_result_comp_data = get_frontend_job_result_data(job_result)

                        # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                        for system_job_result_event in context_function_event(
                            ctx,
                            self.name,
                            'system_job_result',
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

                # Send Normal LlmResponse to Frontend, function_call -> function_response -> Llm_response
                if isinstance(self, SubmitCoreCalculationMCPLlmAgent):
                    yield event
                elif is_text(event):
                    if not event.partial:
                        for multi_part_event in context_multipart2function_event(
                            ctx, self.name, event, 'system_calculation_mcp_agent'
                        ):
                            yield multi_part_event
                else:
                    yield event

            # If specified supervisor_agent, transfer back
            if self.supervisor_agent:
                for function_event in context_function_event(
                    ctx,
                    self.name,
                    'transfer_to_agent',
                    None,
                    ModelRole,
                    {'agent_name': self.supervisor_agent},
                ):
                    yield function_event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event


class ResultCalculationMCPLlmAgent(CalculationMCPLlmAgent):
    def __init__(self, enable_tgz_unpack, **kwargs):
        super().__init__(
            description=ResultCoreAgentDescription,
            enable_tgz_unpack=enable_tgz_unpack,
            **kwargs,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )
        try:
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
                # 如果该任务结果已经在上下文中 && 用户没有请求这个任务结果，则不再重复查询
                if ctx.session.state['long_running_jobs'][origin_job_id][
                    'job_in_ctx'
                ] and origin_job_id != ctx.session.state[FRONTEND_STATE_KEY]['biz'].get(
                    'origin_id', None
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
                    logger.error(
                        f'[{MATMASTER_AGENT_NAME}] {query_res.content[0].text}'
                    )
                    raise RuntimeError(query_res.content[0].text)
                status = query_res.content[0].text
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}]:[{self.name}] origin_job_id = {origin_job_id}, executor = {Executor}, '
                    f'status = {status}'
                )
                if status != 'Running':
                    update_long_running_jobs = copy.deepcopy(
                        ctx.session.state['long_running_jobs']
                    )
                    update_long_running_jobs[origin_job_id]['job_status'] = status
                    yield update_state_event(
                        ctx,
                        state_delta={'long_running_jobs': update_long_running_jobs},
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
                            tgz_flag, new_tool_result = await update_tgz_dict(
                                dict_result
                            )
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
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event


class ParamsCheckCompletedAgent(LlmAgent):
    pass


class ParamsCheckInfoAgent(LlmAgent):
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            async for event in super()._run_async_impl(ctx):
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
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event


class ToolCallInfoAgent(LlmAgent):
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            async for event in super()._run_async_impl(ctx):
                # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
                if not event.partial:
                    try:
                        tool_call_info = json.loads(event.content.parts[0].text)
                    except BaseException:
                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}]:[{self.name}] raw_text = {event.content.parts[0].text}'
                        )
                        raise
                    for system_job_result_event in context_function_event(
                        ctx,
                        self.name,
                        'system_tool_call_info',
                        tool_call_info,
                        ModelRole,
                    ):
                        yield system_job_result_event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event


class SubmitCoreCalculationMCPLlmAgent(CalculationMCPLlmAgent):
    def __init__(self, enable_tgz_unpack, **kwargs):
        super().__init__(enable_tgz_unpack=enable_tgz_unpack, **kwargs)

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )

        try:
            async for event in super()._run_async_impl(ctx):
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
                    )

                if (
                    is_function_response(event)
                    and ctx.session.state['sync_tools']
                    and event.content.parts[0].function_response.name
                    in ctx.session.state['sync_tools']
                ):
                    try:
                        dict_result = load_tool_response(event)
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
                if event.long_running_tool_ids:
                    yield update_state_event(
                        ctx,
                        state_delta={
                            'long_running_ids': ctx.session.state['long_running_ids']
                            + list(event.long_running_tool_ids)
                        },
                    )

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if (
                            part
                            and part.function_response
                            and part.function_response.id
                            in ctx.session.state['long_running_ids']
                            and 'result' in part.function_response.response
                        ):
                            if not part.function_response.response['result'].isError:
                                raw_result = part.function_response.response['result']
                                results = json.loads(raw_result.content[0].text)
                                logger.info(
                                    f"[{MATMASTER_AGENT_NAME}]:[{self.name}] results = {results}"
                                )
                                origin_job_id = results['job_id']
                                job_name = part.function_response.name
                                job_status = results['status']
                                if not ctx.session.state['dflow']:
                                    bohr_job_id = results['extra_info']['bohr_job_id']
                                    job_detail_url = (
                                        f'{SANDBOX_JOB_DETAIL_URL}/{bohr_job_id}'
                                    )
                                    frontend_result = BohrJobInfo(
                                        origin_job_id=origin_job_id,
                                        job_name=job_name,
                                        job_status=job_status,
                                        job_id=bohr_job_id,
                                        job_detail_url=job_detail_url,
                                        agent_name=ctx.agent.parent_agent.parent_agent.name,
                                    ).model_dump(mode='json')
                                else:
                                    workflow_id = results['extra_info']['workflow_id']
                                    workflow_uid = results['extra_info']['workflow_uid']
                                    workflow_url = results['extra_info'][
                                        'workflow_link'
                                    ]
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
                                update_long_running_jobs[origin_job_id] = (
                                    frontend_result
                                )
                                yield update_state_event(
                                    ctx,
                                    state_delta={
                                        'long_running_jobs': update_long_running_jobs,
                                        'render_job_list': True,
                                        'render_job_id': ctx.session.state[
                                            'render_job_id'
                                        ]
                                        + [origin_job_id],
                                        'long_running_jobs_count': ctx.session.state[
                                            'long_running_jobs_count'
                                        ]
                                        + 1,
                                    },
                                )
                            else:
                                # 提交报错同样+1，避免幻觉 card
                                yield update_state_event(
                                    ctx,
                                    state_delta={
                                        'long_running_jobs_count': ctx.session.state[
                                            'long_running_jobs_count'
                                        ]
                                        + 1,
                                    },
                                )
                # END

                # Send Normal LlmResponse to Frontend, function_call -> function_response -> Llm_response
                if is_text(event):
                    if not event.partial:
                        for multi_part_event in context_multipart2function_event(
                            ctx, self.name, event, 'system_submit_core_info'
                        ):
                            yield multi_part_event
                else:
                    yield event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event


class SubmitRenderAgent(LlmAgent):
    def __init__(self, **kwargs):
        super().__init__(description=SubmitRenderAgentDescription, **kwargs)

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )
        try:
            async for event in super()._run_async_impl(ctx):
                if is_text(event) and ctx.session.state['render_job_list']:
                    for cur_render_job_id in ctx.session.state['render_job_id']:
                        # Render Frontend Job-List Component
                        job_list_comp_data = {
                            'eventType': 1,
                            'eventData': {
                                'contentType': 1,
                                'renderType': '@bohrium-chat/matmodeler/task-message',
                                'content': {
                                    JOB_LIST_KEY: ctx.session.state[
                                        'long_running_jobs'
                                    ][cur_render_job_id]
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
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event


class SubmitValidatorAgent(LlmAgent):
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if ctx.session.state['error_occurred']:
            return

        if (
            ctx.session.state['long_running_jobs_count']
            > ctx.session.state['long_running_jobs_count_ori']
        ):
            submit_validator_msg = 'The Job has indeed been submitted.'
            yield update_state_event(
                ctx,
                state_delta={
                    'long_running_jobs_count_ori': ctx.session.state[
                        'long_running_jobs_count'
                    ]
                },
            )
        else:
            submit_validator_msg = (
                'System is experiencing task submission hallucination; '
                'I recommend retrying with the original parameters.'
            )

            current_agent = ctx.agent.parent_agent.parent_agent.name
            if ctx.session.state['hallucination_agent'] != current_agent:
                yield update_state_event(
                    ctx,
                    state_delta={
                        'hallucination': True,
                        'hallucination_agent': ctx.agent.parent_agent.parent_agent.name,
                    },
                )
            else:
                yield update_state_event(
                    ctx,
                    state_delta={
                        'hallucination_agent': None,
                    },
                )
        logger.info(
            f'[{MATMASTER_AGENT_NAME}]:[{self.name}] state = {ctx.session.state}'
        )

        for function_event in context_function_event(
            ctx,
            self.name,
            'system_submit_validator',
            {'msg': submit_validator_msg},
            ModelRole,
        ):
            yield function_event


class BaseAsyncJobAgent(LlmAgent):
    submit_agent: SequentialAgent
    result_agent: SequentialAgent
    params_check_info_agent: LlmAgent
    tool_call_info_agent: LlmAgent
    dflow_flag: bool = Field(
        False, description='Whether the agent is dflow related', exclude=True
    )
    supervisor_agent: str
    sync_tools: Optional[list] = Field(
        None, description='These tools will sync run on the server'
    )
    enable_tgz_unpack: bool = Field(
        True, description='Whether unpack tgz files for tool_results'
    )

    def __init__(
        self,
        model,
        agent_name: str,
        agent_description: str,
        agent_instruction: str,
        mcp_tools: list,
        dflow_flag: bool,
        supervisor_agent: str,
        sync_tools: Optional[list] = None,
        enable_tgz_unpack: bool = True,
    ):
        agent_prefix = agent_name.replace('_agent', '')

        # 创建提交核心代理
        submit_core_agent = SubmitCoreCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_submit_core_agent",
            description=gen_submit_core_agent_description(agent_prefix),
            instruction=gen_submit_core_agent_instruction(agent_prefix),
            tools=mcp_tools,
            disallow_transfer_to_parent=True,
            enable_tgz_unpack=enable_tgz_unpack,
        )

        # 创建提交渲染代理
        submit_render_agent = SubmitRenderAgent(
            model=model, name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = SubmitValidatorAgent(
            model=model, name=f"{agent_prefix}_submit_validator_agent"
        )

        # 创建提交序列代理
        submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=gen_submit_agent_description(agent_prefix),
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent],
        )

        # 创建结果核心代理
        result_core_agent = ResultCalculationMCPLlmAgent(
            model=model,
            name=f"{agent_prefix}_result_core_agent",
            tools=mcp_tools,
            instruction=gen_result_core_agent_instruction(agent_prefix),
            enable_tgz_unpack=enable_tgz_unpack,
        )

        # 创建结果序列代理
        result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description=gen_result_agent_description(),
            sub_agents=[result_core_agent],
        )

        params_check_info_agent = ParamsCheckInfoAgent(
            model=model,
            name=f"{agent_prefix}_params_check_info_agent",
            instruction=gen_params_check_info_agent_instruction(),
            tools=mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            after_model_callback=remove_function_call,
        )

        tool_call_info_agent = ToolCallInfoAgent(
            model=model,
            name=f"{agent_prefix}_tool_call_info_agent",
            instruction=gen_tool_call_info_instruction(),
            tools=mcp_tools,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            after_model_callback=remove_function_call,
        )

        # 初始化父类
        super().__init__(
            name=agent_name,
            model=model,
            description=agent_description,
            submit_agent=submit_agent,
            result_agent=result_agent,
            params_check_info_agent=params_check_info_agent,
            tool_call_info_agent=tool_call_info_agent,
            dflow_flag=dflow_flag,
            sub_agents=[
                submit_agent,
                result_agent,
                params_check_info_agent,
                tool_call_info_agent,
            ],
            supervisor_agent=supervisor_agent,
            sync_tools=sync_tools,
            enable_tgz_unpack=enable_tgz_unpack,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        session_state = get_session_state(ctx)
        yield update_state_event(
            ctx, state_delta={'dflow': self.dflow_flag, 'sync_tools': self.sync_tools}
        )

        async for result_event in self.result_agent.run_async(ctx):
            yield result_event

        if session_state.get('origin_job_id', None) is not None or (
            session_state[FRONTEND_STATE_KEY]['biz'].get('origin_id', None) is not None
            and list(session_state['long_running_jobs'].keys())
            and session_state[FRONTEND_STATE_KEY]['biz']['origin_id']
            in list(session_state['long_running_jobs'].keys())
        ):  # Only Query Job Result
            pass
        else:
            cherry_pick_parts = cherry_pick_events(ctx)[-5:]
            context_messages = '\n'.join(
                [
                    f'<{item[0].title()}> said: \n{item[1]}\n'
                    for item in cherry_pick_parts
                ]
            )
            logger.info(
                f"[{MATMASTER_AGENT_NAME}]:[{self.name}] context_messages = {context_messages}"
            )

            prompt = gen_params_check_completed_agent_instruction().format(
                context_messages=context_messages
            )
            response = litellm.completion(
                model='azure/gpt-4o',
                messages=[{'role': 'user', 'content': prompt}],
                response_format=ParamsCheckComplete,
            )
            params_check_completed_json: dict = json.loads(
                response.choices[0].message.content
            )
            logger.info(
                f"[{MATMASTER_AGENT_NAME}]:[{self.name}] params_check_completed_json = {params_check_completed_json}"
            )
            params_check_completed = params_check_completed_json['flag']
            params_check_reason = params_check_completed_json['reason']
            params_check_msg = params_check_completed_json['analyzed_messages']

            # 包装成function_call，来避免在历史记录中展示；同时模型可以在上下文中感知
            for params_check_reason_event in context_function_event(
                ctx,
                self.name,
                'system_params_check_result',
                {
                    'complete': params_check_completed,
                    'reason': params_check_reason,
                    'analyzed_messages': params_check_msg,
                },
                ModelRole,
            ):
                yield params_check_reason_event

            if not params_check_completed:
                # Call ParamsCheckInfoAgent to generate params needing check
                async for (
                    params_check_info_event
                ) in self.params_check_info_agent.run_async(ctx):
                    yield params_check_info_event
            else:
                async for tool_call_info_event in self.tool_call_info_agent.run_async(
                    ctx
                ):
                    yield tool_call_info_event
                async for submit_event in self.submit_agent.run_async(ctx):
                    yield submit_event

        for function_event in context_function_event(
            ctx,
            self.name,
            'transfer_to_agent',
            None,
            ModelRole,
            {'agent_name': self.supervisor_agent},
        ):
            yield function_event
