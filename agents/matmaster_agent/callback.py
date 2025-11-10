import inspect
import json
import logging
import uuid
from datetime import datetime
from typing import Optional

import litellm
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types
from google.genai.types import FunctionCall, Part

from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATERIALS_ACCESS_KEY,
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.model import UserContent
from agents.matmaster_agent.prompt import get_user_content_lang
from agents.matmaster_agent.style import get_job_complete_card, hallucination_card
from agents.matmaster_agent.utils.job_utils import (
    get_job_status,
    get_running_jobs_detail,
    has_job_running,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# before_agent_callback
async def matmaster_prepare_state(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    session_id = callback_context.session.id
    logger.info(
        f'[{MATMASTER_AGENT_NAME}] {session_id} state = {callback_context.state.to_dict()}'
    )
    callback_context.state['current_time'] = datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S'
    )
    callback_context.state['error_occurred'] = False
    callback_context.state['origin_job_id'] = None
    callback_context.state['special_llm_response'] = False

    callback_context.state[FRONTEND_STATE_KEY] = callback_context.state.get(
        FRONTEND_STATE_KEY, {}
    )
    callback_context.state[FRONTEND_STATE_KEY]['biz'] = callback_context.state[
        FRONTEND_STATE_KEY
    ].get('biz', {})
    callback_context.state['long_running_ids'] = callback_context.state.get(
        'long_running_ids', []
    )
    callback_context.state['long_running_jobs'] = callback_context.state.get(
        'long_running_jobs', {}
    )
    callback_context.state['long_running_jobs_count'] = callback_context.state.get(
        'long_running_jobs_count', 0
    )
    callback_context.state['long_running_jobs_count_ori'] = callback_context.state.get(
        'long_running_jobs_count_ori', 0
    )
    callback_context.state['render_job_list'] = callback_context.state.get(
        'render_job_list', False
    )
    callback_context.state['render_job_id'] = callback_context.state.get(
        'render_job_id', []
    )
    callback_context.state['dflow'] = callback_context.state.get('dflow', False)
    callback_context.state['ak'] = callback_context.state.get('ak', None)
    callback_context.state['project_id'] = callback_context.state.get(
        'project_id', None
    )
    callback_context.state['sync_tools'] = callback_context.state.get(
        'sync_tools', None
    )
    callback_context.state['invocation_id_with_tool_call'] = callback_context.state.get(
        'invocation_id_with_tool_call', None
    )
    callback_context.state['last_llm_response_partial'] = callback_context.state.get(
        'last_llm_response_partial', None
    )
    callback_context.state['new_query_job_status'] = callback_context.state.get(
        'new_query_job_status', {}
    )
    callback_context.state['cost'] = callback_context.state.get('cost', {})
    callback_context.state['hallucination'] = callback_context.state.get(
        'hallucination', False
    )
    callback_context.state['hallucination_agent'] = callback_context.state.get(
        'hallucination_agent', None
    )
    callback_context.state['tools_count'] = callback_context.state.get('tools_count', 0)
    callback_context.state['tools_count_ori'] = callback_context.state.get(
        'tools_count_ori', 0
    )
    callback_context.state['tool_hallucination'] = callback_context.state.get(
        'tool_hallucination', False
    )
    callback_context.state['tool_hallucination_agent'] = callback_context.state.get(
        'tool_hallucination_agent', None
    )
    callback_context.state['plan'] = callback_context.state.get('plan', None)
    callback_context.state['plan_index'] = callback_context.state.get(
        'plan_index', None
    )
    callback_context.state['tool_call_info'] = callback_context.state.get(
        'tool_call_info', []
    )
    callback_context.state['update_tool_args'] = callback_context.state.get(
        'update_tool_args', {}
    )


async def matmaster_set_lang(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    user_content = callback_context.user_content.parts[0].text
    prompt = get_user_content_lang().format(user_content=user_content)
    response = litellm.completion(
        model='azure/gpt-4o',
        messages=[{'role': 'user', 'content': prompt}],
        response_format=UserContent,
    )
    result: dict = json.loads(response.choices[0].message.content)
    logger.info(
        f"[{MATMASTER_AGENT_NAME}]:[{inspect.currentframe().f_code.co_name}] result = {result}"
    )
    language = str(result.get('language', 'zh'))
    callback_context.state['target_language'] = language
    if callback_context.state['target_language'] in [
        'Chinese',
        'zh-CN',
        '简体中文',
        'Chinese (Simplified)',
    ]:
        i18n.language = 'zh'
    else:
        i18n.language = 'en'


# after_model_callback
async def matmaster_check_job_status(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    场景梳理如下：
    - 上一条为None，当前为True：说明是第一条消息
    - 上一条为True，当前为True：说明同一条消息流式输出中
    - 上一条为True，当前为False：说明流式消息输出即将结束
    - 上一条为False，当前为True：说明新的一条消息开始了
    """
    if callback_context.state['error_occurred']:
        return

    if (jobs_dict := callback_context.state['long_running_jobs']) and has_job_running(
        jobs_dict
    ):  # 确认当前有在运行中的任务
        running_job_ids = get_running_jobs_detail(jobs_dict)  # 从 state 里面拿
        reset = False
        for origin_job_id, job_id, agent_name in running_job_ids:
            if not callback_context.state['last_llm_response_partial']:
                logger.info(
                    f'[{MATMASTER_AGENT_NAME}]:[matmaster_check_job_status] new LlmResponse, prepare call API'
                )
                job_status = await get_job_status(
                    job_id, access_key=MATERIALS_ACCESS_KEY
                )  # 查询任务的最新状态
                callback_context.state['new_query_job_status'][
                    'origin_job_id'
                ] = job_status
            else:
                job_status = callback_context.state['new_query_job_status'][
                    'origin_job_id'
                ]  # 从 state 里取
            logger.info(
                f"[{MATMASTER_AGENT_NAME}]:[matmaster_check_job_status] last_llm_response_partial = "
                f"{callback_context.state['last_llm_response_partial']}, "
                f"job_id = {job_id}, job_status = {job_status}"
            )
            if job_status in ['Failed', 'Finished']:
                if llm_response.partial:  # 原来消息的流式版本置空 None
                    llm_response.content = None
                    break
                if not reset:
                    # 标记开始处理原来消息的非流式版本
                    callback_context.state['special_llm_response'] = True
                    llm_response.content.parts = []
                    reset = True
                function_call_id = f"call_{str(uuid.uuid4()).replace('-', '')[:24]}"
                callback_context.state['origin_job_id'] = origin_job_id
                llm_response.content.parts.append(
                    Part(text=get_job_complete_card(i18n=i18n, job_id=job_id))
                )
                llm_response.content.parts.append(
                    Part(
                        function_call=FunctionCall(
                            id=function_call_id,
                            name='transfer_to_agent',
                            args={'agent_name': agent_name},
                        )
                    )
                )
        callback_context.state['last_llm_response_partial'] = llm_response.partial
        # return llm_response

    callback_context.state['last_llm_response_partial'] = llm_response.partial
    return


async def matmaster_hallucination_retry(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    hallucination_flag = callback_context.state['hallucination']
    hallucination_agent = callback_context.state['hallucination_agent']

    if not callback_context.state['hallucination']:
        return

    logger.info(
        f'[{MATMASTER_AGENT_NAME}] hallucination_flag={hallucination_flag}, hallucination_agent={hallucination_agent}, i18n.language = {i18n.language}'
    )

    if llm_response.partial:  # 原来消息的流式版本置空 None
        llm_response.content = None
        return

    # 标记开始处理原来消息的非流式版本
    callback_context.state['special_llm_response'] = True
    llm_response.content.parts = []

    llm_response.content.parts.append(Part(text=hallucination_card(i18n=i18n)))
    function_call_id = f"added_{str(uuid.uuid4()).replace('-', '')[:24]}"
    llm_response.content.parts.append(
        Part(
            function_call=FunctionCall(
                id=function_call_id,
                name='transfer_to_agent',
                args={'agent_name': callback_context.state['hallucination_agent']},
            )
        )
    )
    callback_context.state['hallucination'] = False

    return llm_response
