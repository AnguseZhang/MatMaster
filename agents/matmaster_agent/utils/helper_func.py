import copy
import json
import logging
from typing import Any, List, Optional, Union

import jsonpickle
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmResponse
from google.adk.tools import ToolContext
from google.genai.types import Part
from mcp.types import CallToolResult
from yaml.scanner import ScannerError

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.model import AGENT_TOOLS_MAPPING, JobResult, JobResultType

logger = logging.getLogger(__name__)


def get_session_state(ctx: Union[InvocationContext, ToolContext]):
    return ctx.session.state if isinstance(ctx, InvocationContext) else ctx.state


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
    elif len(new_indices) == len(current_function_calls):
        pass
    else:
        llm_response.content.parts = [
            part
            for index, part in enumerate(copy.deepcopy(llm_response.content.parts))
            if index in new_indices
        ]
    logger.info(
        f"[{MATMASTER_AGENT_NAME}]:[update_llm_response] new_indices = {new_indices}"
    )

    return llm_response


def is_json(json_str):
    try:
        json.loads(json_str)
    except BaseException:
        return False
    return True


async def is_float_sequence(data) -> bool:
    return isinstance(data, (tuple, list)) and all(isinstance(x, float) for x in data)


async def is_str_sequence(data) -> bool:
    return isinstance(data, (tuple, list)) and all(isinstance(x, str) for x in data)


async def is_matmodeler_file(filename: str) -> bool:
    return (
        filename.endswith(
            (
                '.cif',
                '.poscar',
                '.contcar',
                '.vasp',
                '.xyz',
                '.mol',
                '.mol2',
                '.sdf',
                '.dump',
                '.lammpstrj',
            )
        )
        or filename.startswith('lammpstrj')
        or 'POSCAR' in filename
        or 'CONTCAR' in filename
        or filename == 'STRU'
    )


async def is_image_file(filename: str) -> bool:
    return filename.endswith(('.png', '.jpg', '.jpeg'))


def flatten_dict(d, parent_key='', sep='_'):
    """
    将多层嵌套的字典拉平为一级字典

    参数:
        d: 要拉平的字典
        parent_key: 父级键名(递归时使用)
        sep: 嵌套键之间的分隔符

    返回:
        拉平后的一级字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 处理列表中的字典项
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(
                        flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    )
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


def is_mcp_result(tool_response: Optional[dict[str, Any]]):
    return tool_response.get('result', None) is not None and isinstance(
        tool_response['result'], CallToolResult
    )


def is_algorithm_error(dict_result) -> bool:
    return dict_result.get('code') is not None and dict_result['code'] != 0


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

    if dict_result.get('status', None) == 'error':
        raise eval(dict_result['error_type'])(dict_result['error'])

    return dict_result


async def parse_result(result: dict) -> List[dict]:
    """
    Parse and flatten a nested dictionary result into a list of standardized JobResult objects.

    Processes a dictionary (potentially nested) and converts it into serialized JobResult objects.
    Handles various data types including numbers, strings, sequences, and file URLs.
    For image URLs, automatically generates both file reference and markdown representation.

    Args:
        result (dict): Input dictionary to parse. May contain:
                      - Nested dictionaries (automatically flattened)
                      - Primitive values (int, float, str)
                      - Sequences (of numbers or strings)
                      - URLs (regular files or MatModeler files)

    Returns:
        list: Serialized JobResult objects with appropriate types:
              - Value: For primitive types and sequences
              - MatModelerFile/RegularFile: For recognized file URLs
              - Additional markdown representation for image files
              - Error messages for unsupported types

    Example:
        >>> parse_result({"value": 42, "structure": "http://example.com/structure.cif", "phonon": "http://example.com/phonon.png"})

        >>> [
        >>>    {"name": "value", "data": 42, "type": "Value"},
        >>>    {"name": "structure", "data": "structure.cif", "type": "MatModelerFile", "url": "http://example.com/structure.cif"},
        >>>    {"name": "phonon", "data": "phonon.png", "type": "RegularFile", "url": "http://example.com/phonon.png"}
        >>>    {"name": "markdown_image_phonon", "data": "![phonon.png](http://example.com/phonon.png)", "type": "Value"}
        >>> ]
    """
    parsed_result = []
    new_result = {}
    for k, v in result.items():
        if type(v) is dict:
            new_result.update(**flatten_dict(v))
        else:
            new_result[k] = v

    for k, v in new_result.items():
        if type(v) in [int, float]:
            parsed_result.append(
                JobResult(name=k, data=v, type=JobResultType.Value).model_dump(
                    mode='json'
                )
            )
        elif type(v) is str:
            if not v.startswith('http'):
                parsed_result.append(
                    JobResult(name=k, data=v, type=JobResultType.Value).model_dump(
                        mode='json'
                    )
                )
            else:
                filename = v.split('/')[-1]
                if await is_matmodeler_file(filename):
                    parsed_result.append(
                        JobResult(
                            name=k,
                            data=filename,
                            type=JobResultType.MatModelerFile,
                            url=v,
                        ).model_dump(mode='json')
                    )
                else:
                    parsed_result.append(
                        JobResult(
                            name=k, data=filename, type=JobResultType.RegularFile, url=v
                        ).model_dump(mode='json')
                    )
                if await is_image_file(filename):
                    # Extra Add Markdown Image
                    parsed_result.append(
                        JobResult(
                            name=f"markdown_image_{k}",
                            data=f"![{filename}]({v})",
                            type=JobResultType.Value,
                        ).model_dump(mode='json')
                    )
        elif await is_float_sequence(v):
            parsed_result.append(
                JobResult(
                    name=k,
                    data=f"{tuple([float(item) for item in v])}",
                    type=JobResultType.Value,
                ).model_dump(mode='json')
            )
        elif await is_str_sequence(v):
            parsed_result.append(
                JobResult(
                    name=k,
                    data=f"{tuple([str(item) for item in v])}",
                    type=JobResultType.Value,
                ).model_dump(mode='json')
            )
        else:
            parsed_result.append(
                {
                    'status': 'error',
                    'msg': f"{k}({type(v)}) is not supported parse, v={v}",
                }
            )
    return parsed_result


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
        line = f"{call['name']}({args_str})"
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


def get_target_agent(tool_name, sub_agents: List[BaseAgent]):
    target_agent = ''
    for key, value in AGENT_TOOLS_MAPPING.items():
        if tool_name in value:
            target_agent = key
            break

    for sub_agent in sub_agents:
        if sub_agent.name == target_agent:
            return sub_agent
