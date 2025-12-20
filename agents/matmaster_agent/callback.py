import inspect
import json
import logging
from datetime import datetime
from typing import Optional

import litellm
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.genai.types import Part

from agents.matmaster_agent.constant import (
    FRONTEND_STATE_KEY,
    MATMASTER_AGENT_NAME,
)
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.model import UserContent
from agents.matmaster_agent.prompt import get_user_content_lang
from agents.matmaster_agent.services.quota import check_quota_service, use_quota_service
from agents.matmaster_agent.state import ERROR_DETAIL, PLAN, TOOL_INDEX, UPLOAD_FILE
from agents.matmaster_agent.utils.helper_func import get_user_id

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
    # 记录用户错误详情
    callback_context.state[ERROR_DETAIL] = callback_context.state.get(ERROR_DETAIL, '')
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
        'invocation_id_with_tool_call', {}
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
    callback_context.state[PLAN] = callback_context.state.get(PLAN, {})
    callback_context.state['plan_index'] = callback_context.state.get(
        'plan_index', None
    )
    # 当前 step 调用的第几个 tool
    callback_context.state[TOOL_INDEX] = callback_context.state.get(TOOL_INDEX, None)
    callback_context.state['tool_call_info'] = callback_context.state.get(
        'tool_call_info', {}
    )
    # 用户是否确认计划方案
    callback_context.state['plan_confirm'] = callback_context.state.get(
        'plan_confirm', {}
    )
    # 用户意图
    callback_context.state['intent'] = callback_context.state.get('intent', {})
    # 函数签名 From Server
    callback_context.state['function_declarations'] = callback_context.state.get(
        'function_declarations', {}
    )
    # 单次计划涉及的所有场景
    callback_context.state['scenes'] = callback_context.state.get('scenes', [])
    # 单次计划涉及的所有场景
    callback_context.state[UPLOAD_FILE] = False
    # 用户免费使用次数
    callback_context.state['quota_remaining'] = callback_context.state.get(
        'quota_remaining', None
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
    try:
        result: dict = json.loads(response.choices[0].message.content)
    except BaseException:
        result = {}
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


async def matmaster_check_quota(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    user_id = get_user_id(callback_context)
    response = await check_quota_service(user_id=user_id)
    logger.info(f'{callback_context.session.id} check_quota_response = {response}')
    if not response['data'].get('remaining') or not response['data']['remaining']:
        callback_context.state['quota_remaining'] = 0
    else:
        callback_context.state['quota_remaining'] = response['data']['remaining']


async def matmaster_use_quota(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    user_id = get_user_id(callback_context)
    response = await use_quota_service(user_id=user_id)
    logger.info(f'{callback_context.session.id} use_quota_service = {response}')
    if response['code']:
        return types.Content(parts=[Part(text=response['msg'])])
