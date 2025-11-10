import copy
import json
import logging
import os
import traceback
from functools import wraps
from typing import Optional, Union

from deepdiff import DeepDiff
from dp.agent.adapter.adk import CalculationMCPTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import AfterToolCallback, BeforeToolCallback
from google.adk.models import LlmResponse
from google.adk.tools import BaseTool, ToolContext
from mcp.types import CallToolResult, TextContent

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    FRONTEND_STATE_KEY,
    LOCAL_EXECUTOR,
    MATERIALS_ACCESS_KEY,
    MATMASTER_AGENT_NAME,
    SKU_MAPPING,
    Transfer2Agent,
)
from agents.matmaster_agent.model import CostFuncType
from agents.matmaster_agent.utils.auth import ak_to_ticket, ak_to_username
from agents.matmaster_agent.utils.finance import get_user_photon_balance
from agents.matmaster_agent.utils.helper_func import (
    check_None_wrapper,
    function_calls_to_str,
    get_session_state,
    get_unique_function_call,
    update_llm_response,
)
from agents.matmaster_agent.utils.io_oss import update_tgz_dict
from agents.matmaster_agent.utils.job_utils import check_job_create_service
from agents.matmaster_agent.utils.tool_response_utils import check_valid_tool_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# after_model_callback
async def default_after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    # 检查响应是否有效
    if not (
        llm_response
        and llm_response.content
        and llm_response.content.parts
        and len(llm_response.content.parts)
    ):
        return None

    # 获取所有函数调用
    current_function_calls = [
        {'name': part.function_call.name, 'args': part.function_call.args}
        for part in llm_response.content.parts
        if part.function_call
    ]

    # 如果没有函数调用，直接返回
    if not current_function_calls:
        return None

    if (
        callback_context.state.get('invocation_id_with_tool_call', None) is None
        or callback_context.invocation_id
        != list(callback_context.state['invocation_id_with_tool_call'].keys())[-1]
    ):  # 首次调用 function_call 或新一轮对话
        if len(current_function_calls) == 1:
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] {callback_context.session.id} Single Function Call In New Turn'
            )
            logger.info(
                f"[{MATMASTER_AGENT_NAME}] {callback_context.session.id} current_function_calls = {function_calls_to_str(current_function_calls)}"
            )

            if not callback_context.state.get('invocation_id_with_tool_call'):
                callback_context.state['invocation_id_with_tool_call'] = {}
            callback_context.state['invocation_id_with_tool_call'] = {
                **callback_context.state['invocation_id_with_tool_call'],
                callback_context.invocation_id: current_function_calls,
            }
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] {callback_context.session.id} state = {callback_context.state.to_dict()}'
            )
        else:
            logger.warning(f'[{MATMASTER_AGENT_NAME}] Multi Function Calls In One Turn')
            logger.info(
                f"[{MATMASTER_AGENT_NAME}] current_function_calls = {function_calls_to_str(current_function_calls)}"
            )

            callback_context.state['invocation_id_with_tool_call'] = {
                **callback_context.state['invocation_id_with_tool_call'],
                callback_context.invocation_id: get_unique_function_call(
                    current_function_calls
                ),
            }

            return update_llm_response(llm_response, current_function_calls, [])
    else:  # 同一轮对话又出现了 Function Call
        logger.warning(
            f'[{MATMASTER_AGENT_NAME}] Same InvocationId with Function Calls'
        )
        before_function_calls = callback_context.state['invocation_id_with_tool_call'][
            callback_context.invocation_id
        ]
        logger.info(
            f"[{MATMASTER_AGENT_NAME}] before_function_calls = {function_calls_to_str(before_function_calls)},"
            f"[{MATMASTER_AGENT_NAME}] current_function_calls = {function_calls_to_str(current_function_calls)}"
        )

        callback_context.state['invocation_id_with_tool_call'] = {
            **callback_context.state['invocation_id_with_tool_call'],
            callback_context.invocation_id: get_unique_function_call(
                before_function_calls + current_function_calls
            ),
        }

        return update_llm_response(
            llm_response, current_function_calls, before_function_calls
        )

    return None


async def remove_function_call(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    # 检查响应是否有效
    if not (
        llm_response
        and llm_response.content
        and llm_response.content.parts
        and len(llm_response.content.parts)
    ):
        return None

    origin_parts = copy.deepcopy(llm_response.content.parts)
    llm_response.content.parts = []
    for part in origin_parts:
        if part.function_call:
            function_name = part.function_call.name
            function_args = part.function_call.args

            if function_name == 'set_model_response':
                logger.warning(
                    f'[{MATMASTER_AGENT_NAME}] Detected adk-function: `{function_name}`, continue'
                )
            else:
                logger.info(
                    f"[{MATMASTER_AGENT_NAME}] FunctionCall will be removed, name = {function_name}, args = {function_args}"
                )
                part.function_call = None

        if (
            part.text or part.function_call
        ):  # 如果原本只有一个 part，且 part.function_call 被移除了，该 if 不会走
            llm_response.content.parts.append(part)

    if not llm_response.partial:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}] final llm_response = {llm_response.content.parts}"  # 有可能是空列表
        )

    return llm_response


# before_tool_callback
async def default_before_tool_callback(tool, args, tool_context):
    return


async def default_cost_func(tool: BaseTool, args: dict) -> tuple[int, int]:
    return 0, SKU_MAPPING['matmaster']


def check_user_phonon_balance(
    func: BeforeToolCallback, cost_func: CostFuncType
) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] {tool.name}:{tool_context.function_call_id}'
        )

        if cost_func is None:
            return

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            raise TypeError(
                "Not CalculationMCPTool type, current tool can't create job!"
            )

        user_id = _get_userId(tool_context)
        cost, sku_id = await cost_func(tool, args)
        tool_context.state['cost'][tool_context.function_call_id] = {
            'value': cost,
            'sku_id': sku_id,
            'status': 'evaluate',
        }
        balance = await get_user_photon_balance(user_id)

        logger.info(
            f"[{MATMASTER_AGENT_NAME}] {tool_context.session.id} user_id={user_id}, sku_id={sku_id}, cost={cost}, balance={balance}"
        )
        if balance < cost:
            raise RuntimeError('Phonon is not enough, Please recharge.')

    return wrapper


@check_None_wrapper
def _get_ak(ctx: Union[InvocationContext, ToolContext, CallbackContext]):
    session_state = get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY]['biz'].get('ak') or os.getenv(
        'BOHRIUM_ACCESS_KEY'
    )


@check_None_wrapper
def _get_projectId(ctx: Union[InvocationContext, ToolContext]):
    session_state = get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY]['biz'].get('projectId') or os.getenv(
        'BOHRIUM_PROJECT_ID'
    )


@check_None_wrapper
def _get_userId(ctx: Union[InvocationContext, ToolContext]):
    session_state = get_session_state(ctx)
    return session_state[FRONTEND_STATE_KEY].get('adk_user_id') or os.getenv(
        'BOHRIUM_USER_ID'
    )


@check_None_wrapper
def _get_sessionId(ctx: ToolContext):
    session_state = get_session_state(ctx)
    return (
        session_state[FRONTEND_STATE_KEY].get('sessionId')
        or ctx._invocation_context.session.id
    )


def _inject_ak(ctx: Union[InvocationContext, ToolContext], executor, storage):
    access_key = _get_ak(ctx)
    if executor is not None:
        if executor['type'] == 'dispatcher':  # BohriumExecutor
            executor['machine']['remote_profile']['access_key'] = access_key
        elif executor['type'] == 'local' and executor.get(
            'dflow', False
        ):  # DFlowExecutor
            executor['env']['BOHRIUM_ACCESS_KEY'] = access_key
    if storage is not None:  # BohriumStorage
        storage['plugin']['access_key'] = access_key
    return access_key, executor, storage


def _inject_projectId(ctx: Union[InvocationContext, ToolContext], executor, storage):
    project_id = _get_projectId(ctx)
    if executor is not None:
        if executor['type'] == 'dispatcher':  # BohriumExecutor
            executor['machine']['remote_profile']['project_id'] = int(project_id)
            # Redundant set for resources/envs keys
            executor['resources'] = executor.get('resources', {})
            executor['resources']['envs'] = executor['resources'].get('envs', {})
            executor['resources']['envs']['BOHRIUM_PROJECT_ID'] = int(project_id)
        elif executor['type'] == 'local' and executor.get(
            'dflow', False
        ):  # DFlowExecutor
            executor['env']['BOHRIUM_PROJECT_ID'] = str(project_id)
    if storage is not None:  # BohriumStorage
        storage['plugin']['project_id'] = int(project_id)
    return project_id, executor, storage


def _inject_username(ctx: Union[InvocationContext, ToolContext], executor):
    username = ak_to_username(access_key=MATERIALS_ACCESS_KEY)
    if username:
        if executor is not None:
            if executor['type'] == 'dispatcher':  # BohriumExecutor
                # Redundant set for resources/envs keys
                executor['resources'] = executor.get('resources', {})
                executor['resources']['envs'] = executor['resources'].get('envs', {})
                executor['resources']['envs']['BOHRIUM_USERNAME'] = str(username)
            elif executor['type'] == 'local' and executor.get(
                'dflow', False
            ):  # DFlowExecutor
                executor['env']['BOHRIUM_USERNAME'] = str(username)
        return username, executor
    else:
        raise RuntimeError('Failed to get username')


def _inject_ticket(ctx: Union[InvocationContext, ToolContext], executor):
    ticket = ak_to_ticket(access_key=MATERIALS_ACCESS_KEY)
    if ticket:
        if executor is not None:
            if executor['type'] == 'dispatcher':  # BohriumExecutor
                # Redundant set for resources/envs keys
                executor['resources'] = executor.get('resources', {})
                executor['resources']['envs'] = executor['resources'].get('envs', {})
                executor['resources']['envs']['BOHRIUM_TICKET'] = str(ticket)
            elif executor['type'] == 'local' and executor.get(
                'dflow', False
            ):  # DFlowExecutor
                executor['env']['BOHRIUM_TICKET'] = str(ticket)
        return ticket, executor
    else:
        raise RuntimeError('Failed to get ticket')


def _inject_current_env(executor):
    if executor is not None:
        if executor['type'] == 'dispatcher':  # BohriumExecutor
            # Redundant set for resources/envs keys
            executor['resources'] = executor.get('resources', {})
            executor['resources']['envs'] = executor['resources'].get('envs', {})
            executor['resources']['envs']['CURRENT_ENV'] = str(CURRENT_ENV)
        elif executor['type'] == 'local' and executor.get(
            'dflow', False
        ):  # DFlowExecutor
            executor['env']['CURRENT_ENV'] = str(CURRENT_ENV)
    return executor


def _inject_userId(ctx: Union[InvocationContext, ToolContext], executor):
    user_id = _get_userId(ctx)
    if user_id:
        if executor is not None:
            if executor['type'] == 'dispatcher':  # BohriumExecutor
                executor['machine']['remote_profile']['real_user_id'] = int(user_id)
        return user_id, executor
    else:
        raise RuntimeError('Failed to get user_id')


def _inject_sessionId(ctx: ToolContext, executor):
    session_id = _get_sessionId(ctx)
    if session_id:
        if executor is not None:
            if executor['type'] == 'dispatcher':  # BohriumExecutor
                executor['machine']['remote_profile']['session_id'] = str(session_id)
        return session_id, executor
    else:
        raise RuntimeError('Failed to get session_id')


def inject_username_ticket(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 先执行前面的回调链
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 注入 username
        _, tool.executor = _inject_username(tool_context, tool.executor)

        # 注入 ticket
        _, tool.executor = _inject_ticket(tool_context, tool.executor)

    return wrapper


def inject_userId_sessionId(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 先执行前面的回调链
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 注入 username
        _, tool.executor = _inject_userId(tool_context, tool.executor)

        # 注入 ticket
        _, tool.executor = _inject_sessionId(tool_context, tool.executor)

    return wrapper


def inject_current_env(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 先执行前面的回调链
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 注入当前环境
        tool.executor = _inject_current_env(tool.executor)

    return wrapper


def check_job_create(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            raise TypeError(
                "Not CalculationMCPTool type, current tool can't create job!"
            )

        if tool.executor is not None:
            return await check_job_create_service()

    return wrapper


def update_tool_args(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            raise TypeError(
                "Not CalculationMCPTool type, current tool can't create job!"
            )

        tool_call_info = tool_context.state['tool_call_info']
        if not tool_call_info:
            logger.warning(
                f'[{MATMASTER_AGENT_NAME}] empty, tool_call_info = {tool_call_info}'
            )
            return

        last_tool_call_info = tool_call_info[-1]
        if last_tool_call_info['tool_name'] != tool.name:
            logger.warning(
                f'[{MATMASTER_AGENT_NAME}] not match, tool_call_info = {tool_call_info}, tool.name = {tool.name}'
            )
            return

        logger.info(f'[{MATMASTER_AGENT_NAME}] before args = {args}')
        diff = DeepDiff(args, last_tool_call_info['tool_args'])
        if diff:
            args = last_tool_call_info['tool_args']
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] args updated with differences: {diff}'
            )
            logger.info(f'[{MATMASTER_AGENT_NAME}] after args = {args}')
        else:
            logger.info(f'[{MATMASTER_AGENT_NAME}] args unchanged')

        tool_context.state['update_tool_args'] = args

    return wrapper


# 总应该在最后
def catch_before_tool_callback_error(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        try:
            # 如果 tool 为 Transfer2Agent，直接 return
            if tool.name == Transfer2Agent:
                return None

            if (before_tool_result := await func(tool, args, tool_context)) is not None:
                return before_tool_result

            # Override Sync Tool
            if tool_context.state['sync_tools']:
                for sync_tool in tool_context.state['sync_tools']:
                    if tool.name == sync_tool:
                        tool.async_mode = False
                        tool.wait = True
                        tool.executor = LOCAL_EXECUTOR

            logger.info(
                f'[{MATMASTER_AGENT_NAME}]:[catch_before_tool_callback_error] executor={tool.executor}'
            )
            logger.info(
                f'[{MATMASTER_AGENT_NAME}] update_tool_args = {tool_context.state['update_tool_args']}'
            )
            return await tool.run_async(
                args=tool_context.state['update_tool_args'], tool_context=tool_context
            )
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
            }

    return wrapper


# after_tool_callback
async def default_after_tool_callback(tool, args, tool_context, tool_response):
    return


def tgz_oss_to_oss_list(
    func: AfterToolCallback, enable_tgz_unpack: bool
) -> AfterToolCallback:
    """Decorator that processes tool responses containing tgz files from OSS.

    This decorator performs the following operations:
    1. Calls the original after-tool callback function
    2. If the original callback returns a result, uses that result
    3. For CalculationMCPTool responses containing tgz file URLs:
       - Extracts the tgz files
       - Converts the contents
       - Uploads the processed files back to OSS
       - Returns a new result with updated file URLs

    Args:
        func: The after-tool callback function to be decorated

    Returns:
        A wrapper function that processes the tool response

    Raises:
        TypeError: If the tool is not of type CalculationMCPTool

    Example:
        The decorator processes responses containing tgz file URLs like:
        {
            "result1": "https://example.com/file1.tgz",
            "result2": "normal_value"
        }
        And converts them to:
        {
            "result1": "https://example.com/file1.tgz",
            "result2": "normal_value"
            “file1_part1”: "https://new-url/file1_part1",
            "file1_part1": "https://new-url/file1_part2",
        }
    """

    @wraps(func)
    async def wrapper(
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
        tool_response: Union[dict, CallToolResult],
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (
            after_tool_result := await func(tool, args, tool_context, tool_response)
        ) is not None:
            return after_tool_result

        # 不自动解压，直接返回
        if not enable_tgz_unpack:
            return

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            raise TypeError('Not CalculationMCPTool type')

        # 检查是否为有效的 json 字典
        if not check_valid_tool_response(tool_response):
            return None

        tool_result = json.loads(tool_response.content[0].text)
        tgz_flag, new_tool_result = await update_tgz_dict(tool_result)
        if tgz_flag:
            return new_tool_result

    return wrapper


def remove_job_link(func: AfterToolCallback) -> AfterToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
        tool_response: Union[dict, CallToolResult],
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 after_tool_callback；
        # 2. 如果调用的 after_tool_callback 有返回值，以这个为准
        # 如果 tool 为 Transfer2Agent，直接 return
        if tool.name == Transfer2Agent:
            return None

        if (
            after_tool_result := await func(tool, args, tool_context, tool_response)
        ) is not None:
            return after_tool_result

        # 检查是否为有效的 json 字典
        if not check_valid_tool_response(tool_response):
            return None

        # 移除 job_link
        tool_result: dict = json.loads(tool_response.content[0].text)
        if tool_result.get('extra_info', None) is not None:
            del tool_result['extra_info']['job_link']
            tool_response.content[0] = TextContent(
                type='text', text=json.dumps(tool_result)
            )
            if (
                getattr(tool_response, 'structuredContent', None) is not None
                and tool_response.structuredContent is not None
            ):
                tool_response.structuredContent = None

            logger.info(
                f"[{MATMASTER_AGENT_NAME}]:[remove_job_link] final_tool_result = {tool_response}"
            )
            return tool_response

    return wrapper


def catch_after_tool_callback_error(func: AfterToolCallback) -> AfterToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
        tool_response: Union[dict, CallToolResult],
    ) -> Optional[dict]:
        # 两步操作：
        # 1. 调用被装饰的 after_tool_callback；
        # 2. 如果调用的 after_tool_callback 有返回值，以这个为准
        try:
            # 如果 tool 为 Transfer2Agent，直接 return
            if tool.name == Transfer2Agent:
                return None

            if (
                after_tool_result := await func(tool, args, tool_context, tool_response)
            ) is not None:
                return after_tool_result
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
            }

    return wrapper


# 总应该在最后
def check_before_tool_callback_effect(func: AfterToolCallback) -> AfterToolCallback:
    """A decorator that checks the tool response type before executing the callback function.

    This decorator wraps an AfterToolCallback function and checks if the tool_response
    is a dictionary. If it is, the wrapper returns None without calling the original
    function. Otherwise, it proceeds with the original function.

    Args:
        func: The AfterToolCallback function to be wrapped.

    Returns:
        AfterToolCallback: The wrapped function that includes the type checking logic.

    The wrapper function parameters:
        tool: The BaseTool instance that was executed.
        args: Dictionary of arguments passed to the tool.
        tool_context: The context in which the tool was executed.
        tool_response: The response from the tool, either a dict or CallToolResult.

    Returns:
        Optional[dict]: Returns None if tool_response is a dict, otherwise returns
        the result of the original callback function.
    """

    @wraps(func)
    async def wrapper(
        tool: BaseTool,
        args: dict,
        tool_context: ToolContext,
        tool_response: Union[dict, CallToolResult],
    ) -> Optional[dict]:
        # if `before_tool_callback` return dict
        if type(tool_response) is dict:
            return

        return await func(tool, args, tool_context, tool_response)

    return wrapper
