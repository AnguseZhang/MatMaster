import json
import logging
import os
import re
from typing import Any, List, Optional, Union

import jsonpickle
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmResponse
from google.adk.tools import ToolContext
from google.genai.types import FunctionCall, Part
from mcp.types import CallToolResult
from yaml.scanner import ScannerError

from agents.matmaster_agent.constant import FRONTEND_STATE_KEY, MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def get_session_state(ctx: Union[InvocationContext, ToolContext]):
    return ctx.session.state if isinstance(ctx, InvocationContext) else ctx.state


def get_user_id(ctx: CallbackContext):
    frontend_state = ctx.state.get(FRONTEND_STATE_KEY)
    return frontend_state.get('adk_user_id') or os.getenv('BOHRIUM_USER_ID') or '1'


def update_llm_response(
    llm_response: LlmResponse,
    current_function_calls: List[dict],
    before_function_calls: List[dict],
):
    new_indices = get_new_function_call_indices(
        current_function_calls, before_function_calls
    )
    if not len(new_indices):  # 空列表
        llm_response.content.parts = [
            Part(text='All Function Calls Are Occurred Before, Continue')
        ]
    else:
        llm_response.content.parts = [
            Part(
                function_call=FunctionCall(
                    id=current_function_calls[new_indices[0]]['id'],
                    args=current_function_calls[new_indices[0]]['args'],
                    name=current_function_calls[new_indices[0]]['name'],
                )
            )
        ]
    logger.info(f"llm_response = {llm_response}")

    return llm_response


def is_json(json_str):
    try:
        json.loads(json_str)
    except BaseException:
        return False
    return True


def is_mcp_result(tool_response: Optional[dict[str, Any]]):
    return tool_response.get('result', None) is not None and isinstance(
        tool_response['result'], CallToolResult
    )


def result_has_code(dict_result) -> bool:
    return dict_result.get('code') is not None


def is_algorithm_error(dict_result) -> bool:
    return result_has_code(dict_result) and dict_result['code'] not in (0, -9999)


def no_found_structure_error(dict_result) -> bool:
    return result_has_code(dict_result) and dict_result['code'] == -9999


def wallet_no_fee_error(dict_result) -> bool:
    return result_has_code(dict_result) and dict_result['code'] == 140202


def load_tool_response(part: Part):
    tool_response = part.function_response.response
    if is_mcp_result(tool_response):
        raw_result = tool_response['result'].content[0].text
        try:
            dict_result = jsonpickle.loads(raw_result)
        except ScannerError as err:
            raise type(err)(f"[jsonpickle ScannerError] raw_result = `{raw_result}`")
    else:
        dict_result = tool_response

    if dict_result.get('status', None) == 'error' and dict_result.get('error_type'):
        raise eval(dict_result['error_type'])(dict_result['error'])

    return dict_result


def is_same_function_call(
    current_function_call: dict, expected_function_call: dict
) -> bool:
    if current_function_call['function_name'] == expected_function_call[
        'function_name'
    ] and json.dumps(
        current_function_call['function_args'], sort_keys=True
    ) == json.dumps(
        expected_function_call['function_args'], sort_keys=True
    ):
        return True

    return False


def function_calls_to_str(function_calls: List[dict]) -> str:
    """将 function_calls 列表转换为可打印的字符串格式。

    Args:
        function_calls: 函数调用列表，每个元素应有 `name` 和 `args` 属性。

    Returns:
        str: 格式化后的字符串，每行一个函数调用，格式为 `name(args)`。
    """
    if not function_calls:
        return '[]'

    lines = []
    for call in function_calls:
        # 确保 args 是字典或可 JSON 序列化的对象
        args_str = json.dumps(call['args'], indent=2) if call.get('args') else '{}'
        line = f"{call['name']}[{call['id']}]({args_str})"
        lines.append(line)

    return '\n'.join(lines)


def get_unique_function_call(function_calls: List[dict]):
    seen = set()
    unique = []
    for call in function_calls:
        key = (call['name'], json.dumps(call['args'], sort_keys=True))
        if key not in seen:
            seen.add(key)
            unique.append(call)
    return unique


def get_new_function_call_indices(
    current_function_calls: List[dict], before_function_calls: List[dict]
) -> List[int]:
    """返回 current_function_calls 中不在 before_function_calls 的索引列表。

    Args:
        current_function_calls: 当前函数调用列表
        before_function_calls: 之前的函数调用列表

    Returns:
        List[int]: 新出现的函数调用的索引列表
    """
    new_indices = []

    # 提前计算 before_function_calls 的唯一标识集合，提高效率
    before_keys = set()
    for call in before_function_calls:
        key = (call['name'], json.dumps(call['args'], sort_keys=True))
        before_keys.add(key)

    # 遍历 current_function_calls，检查是否在 before 集合中
    for idx, call in enumerate(current_function_calls):
        current_key = (call['name'], json.dumps(call['args'], sort_keys=True))
        if current_key not in before_keys:
            new_indices.append(idx)

    return new_indices


def get_current_step_function_call(current_function_calls, ctx):
    current_step_tool = ctx.state['plan']['steps'][ctx.state['plan_index']]['tools'][
        ctx.state['tool_index']
    ]
    current_step_tool_name, current_step_satus = (
        current_step_tool['tool_name'],
        current_step_tool['status'],
    )

    update_current_function_calls = [
        item
        for item in current_function_calls
        if item['name'] == current_step_tool_name
        and current_step_satus == PlanStepStatusEnum.PROCESS
    ]

    # if not update_current_function_calls:
    #     logger.warning(
    #         f'{ctx.session.id} current_function_calls empty, manual build one'
    #     )
    #     update_current_function_calls = [{'name': current_step_tool_name, 'args': {}}]

    return update_current_function_calls


def check_None_wrapper(func):
    def wrapper(*args, **kwargs):
        result = func(
            *args, **kwargs
        )  # 注意这里应该是 *args, **kwargs 而不是 args, kwargs
        if result is None:
            raise ValueError(
                f"'{func.__name__.replace('_get_', '')}' was not found, please provide it!"
            )
        return result  # 通常装饰器应该返回原函数的结果

    return wrapper


def extract_json_from_string(json_string) -> str:
    """
    从包含JSON数据的字符串中提取JSON部分并转换为Python字典

    Args:
        json_string (str): 包含JSON数据的字符串，可能包含```json和```标记

    Returns:
        dict: 提取出的JSON数据对应的Python字典
    """
    # 使用正则表达式匹配```json和```之间的内容
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, json_string, re.DOTALL)

    if match:
        # 提取JSON字符串
        json_content = match.group(1)
        # 转换为Python字典
        return json_content
    else:
        return json_string
