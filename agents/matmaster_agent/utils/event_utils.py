import copy
import inspect
import logging
import os
import traceback
import uuid
from typing import Iterable, Optional

from deepmerge import always_merger
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools import BaseTool
from google.genai.types import Content, FunctionCall, FunctionResponse, Part

from agents.matmaster_agent.base_callbacks.private_callback import _get_userId
from agents.matmaster_agent.config import USE_PHOTON
from agents.matmaster_agent.constant import CURRENT_ENV, MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.style import (
    no_found_structure_card,
    photon_consume_free_card,
    photon_consume_notify_card,
    photon_consume_success_card,
    tool_response_failed_card,
)
from agents.matmaster_agent.utils.finance import photon_consume
from agents.matmaster_agent.utils.helper_func import (
    is_algorithm_error,
    no_found_structure_error,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def update_state_event(
    ctx: InvocationContext, state_delta: dict, event: Optional[Event] = None
):
    stack = inspect.stack()
    frame = stack[1]  # stack[1] 表示调用当前函数的上一层调用
    filename = os.path.basename(frame.filename)
    lineno = frame.lineno

    origin_event_state_delta = {}
    if event and event.actions and event.actions.state_delta:
        origin_event_state_delta = event.actions.state_delta
        logger.warning(
            f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} origin_event_state_delta = {origin_event_state_delta}'
        )

    final_state_delta = always_merger.merge(state_delta, origin_event_state_delta)
    logger.info(
        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} {filename}:{lineno} final_state_delta = {final_state_delta}'
    )
    actions_with_update = EventActions(state_delta=final_state_delta)
    return Event(
        invocation_id=ctx.invocation_id,
        author=f"{filename}:{lineno}",
        actions=actions_with_update,
    )


# event check funcs
def has_part(event: Event):
    return (
        event
        and event.content
        and event.content.parts
        and len(event.content.parts)
        and event.content.parts[0]
    )


def is_text(event: Event):
    return has_part(event) and event.content.parts[0].text


def is_function_call(event: Event) -> bool:
    """检查事件是否包含函数调用"""
    return has_part(event) and any(part.function_call for part in event.content.parts)


def get_function_call_indexes(event: Event):
    return [
        index for index, part in enumerate(event.content.parts) if part.function_call
    ]


def is_function_response(event: Event):
    return has_part(event) and event.content.parts[0].function_response


# event send funcs
# 仅前端感知
def frontend_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    return Event(
        author=author,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=Content(parts=[Part(text=text)], role=role),
        partial=True,
    )


def frontend_function_call_event(
    ctx: InvocationContext,
    author: str,
    function_call_id: str,
    function_call_name: str,
    role: str,
    args: Optional[dict] = None,
):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[
                Part(
                    function_call=FunctionCall(
                        id=function_call_id,
                        name=function_call_name,
                        args=args,
                    )
                )
            ],
            role=role,
        ),
        partial=True,
    )


def frontend_function_response_event(
    ctx: InvocationContext,
    author: str,
    function_call_id: str,
    function_call_name: str,
    response: Optional[dict],
    role: str,
):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[
                Part(
                    function_response=FunctionResponse(
                        id=function_call_id,
                        name=function_call_name,
                        response=response,
                    )
                )
            ],
            role=role,
        ),
        partial=True,
    )


# 仅模型上下文感知
def context_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    return Event(
        author=author,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=Content(parts=[Part(text=text)], role=role),
        partial=False,
    )


def context_function_call_event(
    ctx: InvocationContext,
    author: str,
    function_call_id: str,
    function_call_name: str,
    role: str,
    args: Optional[dict] = None,
):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[
                Part(
                    function_call=FunctionCall(
                        id=function_call_id,
                        name=function_call_name,
                        args=args,
                    )
                )
            ],
            role=role,
        ),
        partial=False,
    )


def context_function_response_event(
    ctx: InvocationContext,
    author: str,
    function_call_id: str,
    function_call_name: str,
    response: Optional[dict],
    role: str,
):
    return Event(
        author=author,
        invocation_id=ctx.invocation_id,
        content=Content(
            parts=[
                Part(
                    function_response=FunctionResponse(
                        id=function_call_id, name=function_call_name, response=response
                    )
                )
            ],
            role=role,
        ),
        partial=False,
    )


def frontend_function_event(
    ctx: InvocationContext,
    author: str,
    function_call_name: str,
    response: Optional[dict],
    role: str,
    args: Optional[dict] = None,
):
    function_call_id = f"added_{str(uuid.uuid4()).replace('-', '')[:24]}"
    yield frontend_function_call_event(
        ctx, author, function_call_id, function_call_name, role, args
    )
    yield frontend_function_response_event(
        ctx, author, function_call_id, function_call_name, response, role
    )


def context_function_event(
    ctx: InvocationContext,
    author: str,
    function_call_name: str,
    response: Optional[dict],
    role: str,
    args: Optional[dict] = None,
):
    function_call_id = f"added_{str(uuid.uuid4()).replace('-', '')[:24]}"
    yield context_function_call_event(
        ctx, author, function_call_id, function_call_name, role, args
    )
    yield context_function_response_event(
        ctx, author, function_call_id, function_call_name, response, role
    )


def context_multipart2function_event(
    ctx: InvocationContext, author: str, event: Event, function_call_name: str
):
    for part in event.content.parts:
        if part.text:
            yield Event(author=author, invocation_id=ctx.invocation_id)
        elif part.function_call:
            logger.warning(
                f"[{MATMASTER_AGENT_NAME}]:[context_multipart2function_event] function_name = {part.function_call.name}, function_args = {part.function_call.args}"
            )
            yield context_function_call_event(
                ctx,
                author,
                function_call_id=part.function_call.id,
                function_call_name=part.function_call.name,
                role=ModelRole,
                args=part.function_call.args,
            )


# 数据库 & 前端都感知
def all_text_event(ctx: InvocationContext, author: str, text: str, role: str):
    yield frontend_text_event(ctx, author, text, role)
    yield context_text_event(ctx, author, text, role)


def all_function_event(
    ctx: InvocationContext,
    author: str,
    function_call_name: str,
    response: Optional[dict],
    role: str,
    args: Optional[dict] = None,
):
    yield from frontend_function_event(
        ctx, author, function_call_name, response, role, args
    )
    yield from context_function_event(
        ctx, author, function_call_name, response, role, args
    )


def cherry_pick_events(ctx: InvocationContext):
    events = ctx.session.events
    cherry_pick_parts = []
    for event in events:
        if event.content:
            for part in event.content.parts:
                if part.text:
                    cherry_pick_parts.append(
                        (event.content.role, part.text, event.author)
                    )

    return cherry_pick_parts


async def send_error_event(err, ctx: InvocationContext, author):
    # 更新 plan 为失败
    update_plan = copy.deepcopy(ctx.session.state['plan'])
    update_plan['steps'][ctx.session.state['plan_index']][
        'status'
    ] = PlanStepStatusEnum.FAILED

    yield update_state_event(
        ctx, state_delta={'plan': update_plan, 'error_occurred': True}
    )

    # 判断是否是异常组
    if isinstance(err, BaseExceptionGroup):
        error_details = [
            f"Exception Group caught with {len(err.exceptions)} exceptions:",
            f"Message: {str(err)}",
            '\nIndividual exceptions:',
        ]
        exceptions: Optional[Iterable[BaseException]] = err.exceptions
    else:
        error_details = [
            'Single Exception caught:',
            f"Type: {type(err).__name__}",
            f"Message: {str(err)}",
            '\nTraceback:',
            ''.join(traceback.format_tb(err.__traceback__)),
        ]
        exceptions = None  # 单一异常时不再循环子异常

    # 如果是异常组，逐个子异常处理
    if exceptions:
        for i, exc in enumerate(exceptions, 1):
            error_details.append(f"\nException #{i}:")
            error_details.append(f"Type: {type(exc).__name__}")
            error_details.append(f"Message: {str(exc)}")
            error_details.append(
                f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}"
            )

    # 合并错误信息
    detailed_error = '\n'.join(error_details)

    # 发送系统错误事件
    for event in context_function_event(
        ctx, author, 'system_detail_error', {'msg': detailed_error}, ModelRole
    ):
        yield event


async def photon_consume_event(ctx, event, author):
    current_cost = ctx.session.state['cost'].get(
        event.content.parts[0].function_response.id, None
    )
    if current_cost is not None:
        if current_cost['value']:
            user_id = _get_userId(ctx)
            photon_value = current_cost['value'] if CURRENT_ENV != 'test' else 1
            res = await photon_consume(
                user_id, sku_id=current_cost['sku_id'], event_value=photon_value
            )
            if res['code'] == 0:
                for consume_event in all_text_event(
                    ctx,
                    author,
                    f"{photon_consume_success_card(photon_value)}",
                    ModelRole,
                ):
                    yield consume_event
        else:
            yield Event(author=author)


async def display_future_consume_event(event, cost_func, ctx, author):
    for index in get_function_call_indexes(event):
        function_call_name = event.content.parts[index].function_call.name
        function_call_args = event.content.parts[index].function_call.args
        invocated_tool = BaseTool(name=function_call_name, description='')
        tool_cost, _ = await cost_func(invocated_tool, function_call_args)

        if tool_cost:
            future_consume_msg = f"{photon_consume_notify_card(tool_cost)}"
        else:
            future_consume_msg = f"{photon_consume_free_card()}"

        for photon_consume_notify_event in all_text_event(
            ctx,
            author,
            future_consume_msg,
            ModelRole,
        ):
            yield photon_consume_notify_event


def handle_tool_error(ctx, author, error_message, error_type):
    """统一处理工具执行错误"""
    # 发送错误提示事件
    yield from all_text_event(
        ctx,
        author,
        error_message,
        ModelRole,
    )

    # 更新 plan 状态为失败
    update_plan = copy.deepcopy(ctx.session.state['plan'])
    update_plan['steps'][ctx.session.state['plan_index']][
        'status'
    ] = PlanStepStatusEnum.FAILED
    yield update_state_event(ctx, state_delta={'plan': update_plan})

    # 抛出相应的异常
    raise RuntimeError(f'Tool Execution Error: {error_type}')


async def display_failed_result_or_consume(
    dict_result: dict, ctx, author: str, event: Event
):
    if is_algorithm_error(dict_result):
        for event in handle_tool_error(
            ctx, author, f"{tool_response_failed_card(i18n=i18n)}", 'Algorithm Error'
        ):
            yield event
    elif no_found_structure_error(dict_result):
        for event in handle_tool_error(
            ctx,
            author,
            f"{no_found_structure_card(i18n=i18n)}",
            'No found structure match',
        ):
            yield event
    else:
        # 更新 plan 为成功
        update_plan = copy.deepcopy(ctx.session.state['plan'])
        if not dict_result.get('job_id'):
            status = PlanStepStatusEnum.SUCCESS  # real-time
        else:
            status = PlanStepStatusEnum.SUBMITTED  # job-type
        update_plan['steps'][ctx.session.state['plan_index']]['status'] = status
        yield update_state_event(ctx, state_delta={'plan': update_plan})

        if USE_PHOTON:
            async for consume_event in photon_consume_event(ctx, event, author):
                yield consume_event


async def handle_upload_file_event(ctx: InvocationContext, author):
    prompt = ''
    if ctx.user_content and ctx.user_content.parts:
        for part in ctx.user_content.parts:
            if part.text:
                prompt += part.text
            elif part.inline_data:
                pass  # Inline data is currently not processed
            elif part.file_data:
                prompt += f", file_url = {part.file_data.file_uri}"

                # 包装成function_call，来避免在历史记录中展示
                for event in context_function_event(
                    ctx,
                    author,
                    'system_upload_file',
                    {'prompt': prompt},
                    ModelRole,
                ):
                    yield event

                yield update_state_event(ctx, state_delta={'upload_file': True})


def _get_agent_machine_type(agent_name: str) -> str:
    """
    获取 agent 的 machine_type，如果未设置则返回默认值 c2_m4_cpu

    Args:
        agent_name: Agent 名称

    Returns:
        str: machine_type
    """
    from agents.matmaster_agent.sub_agents.mapping import AGENT_MACHINE_TYPE

    # 从 mapping.py 中获取 machine_type，如果未设置则使用默认值
    return AGENT_MACHINE_TYPE.get(agent_name, 'c2_m4_cpu')


def save_parameters_to_json(
    ctx: InvocationContext, params_dict_list: list, task_groups: list = None
) -> str:
    """
    将收集到的参数保存为 JSON 文件，格式包含 nodes 和 edges（新格式）

    Args:
        ctx: InvocationContext
        params_dict_list: 参数列表，每个元素包含 tool_name, step_index, description, tool_args, missing_tool_args, agent_name
        task_groups: 任务分组（依赖关系），如果为 None 则不包含 edges

    Returns:
        str: JSON 文件路径
    """
    import json
    import os
    import uuid
    from datetime import datetime

    from agents.matmaster_agent.sub_agents.mapping import AGENT_IMAGE_ADDRESS

    # 创建输出目录
    output_dir = os.path.join(os.getcwd(), 'parameters_output')
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名（包含 session_id 和时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = ctx.session.id[:8] if ctx.session.id else 'unknown'
    filename = f'parameters_{session_id}_{timestamp}.json'
    filepath = os.path.join(output_dir, filename)

    # 获取 function_declarations 用于获取参数类型信息
    function_declarations = ctx.session.state.get('function_declarations', [])

    # 构建 nodes（每个任务一个 node）
    nodes = []
    node_id_map = {}  # step_index -> node_id 映射

    for i, params in enumerate(params_dict_list):
        step_index = params['step_index']
        tool_name = params['tool_name']
        agent_name = params.get('agent_name', '')

        # 生成 node_id (格式: node-$id1, node-$id2, ...)
        node_id = f"node-$id{i + 1}"
        node_id_map[step_index] = node_id

        # 获取该工具的 function_declaration
        tool_declaration = None
        for decl in function_declarations:
            if decl.get('name') == tool_name:
                tool_declaration = decl
                break

        # 构建 input_parameters（从 tool_args 转换）
        input_parameters = []
        tool_args = params.get('tool_args', {})
        if tool_declaration and 'parameters' in tool_declaration:
            properties = tool_declaration['parameters'].get('properties', {})
            for param_name, param_value in tool_args.items():
                # 跳过系统参数
                if param_name in ['executor', 'storage']:
                    continue

                # 获取参数类型和默认值
                param_type = 'str'  # 默认类型
                default_value = None
                if param_name in properties:
                    param_schema = properties[param_name]
                    param_type = _get_parameter_type(param_schema)
                    # 获取默认值
                    if 'default' in param_schema:
                        default_value = param_schema['default']

                input_parameters.append(
                    {
                        'name': param_name,
                        'type': param_type,
                        'value': (
                            param_value if param_value is not None else default_value
                        ),
                    }
                )
        else:
            # 如果没有 function_declaration，直接从 tool_args 构建
            for param_name, param_value in tool_args.items():
                if param_name in ['executor', 'storage']:
                    continue
                input_parameters.append(
                    {'name': param_name, 'type': 'str', 'value': param_value}
                )

        # 构建 output_parameters（先空着）
        output_parameters = []

        # 获取 machine_type 和 image
        machine_type = _get_agent_machine_type(agent_name)
        image = AGENT_IMAGE_ADDRESS.get(agent_name, '')

        # 构建节点
        node = {
            'id': node_id,
            'node_uuid': str(uuid.uuid4()),
            'node_version': '1.2',
            'label': tool_name,  # 使用 tool_name 作为 label
            'position_x': 0.0,  # 先空置
            'position_y': 0.0,  # 先空置
            'system_values': {
                'machine_type': machine_type,
                'image': image,
                'docker_image': '',  # 先空着
            },
            'input_parameters': input_parameters,
            'output_parameters': output_parameters,
        }
        nodes.append(node)

    # 构建 edges（任务之间的依赖关系）
    edges = []
    edge_id_counter = 1

    def _find_file_connections(source_node, target_node):
        """
        判断两个节点的输出输入文件对接
        返回匹配的连接列表，每个连接包含 (source_param_name, target_param_name)
        """
        connections = []
        source_tool_name = source_node.get('label', '')
        target_input_params = target_node.get('input_parameters', [])
        source_output_params = source_node.get('output_parameters', [])

        # 如果没有 output_parameters，使用默认的输出参数名
        if not source_output_params:
            # 使用 tool_name 生成默认输出参数名
            default_output_name = f'out_{source_tool_name}'
        else:
            default_output_name = source_output_params[0].get(
                'name', f'out_{source_tool_name}'
            )

        if target_input_params:
            # 简单匹配：如果参数名包含文件相关关键词，建立连接
            file_keywords = [
                'file',
                'path',
                'url',
                'input',
                'output',
                'structure',
                'data',
                'result',
            ]
            for target_param in target_input_params:
                target_name = target_param.get('name', '')
                if any(keyword in target_name.lower() for keyword in file_keywords):
                    connections.append((default_output_name, target_name))
                    break

            # 如果没有找到匹配，使用第一个输入参数
            if not connections:
                connections.append(
                    (default_output_name, target_input_params[0].get('name', 'input'))
                )
        else:
            # 如果没有输入参数，使用默认值
            connections.append((default_output_name, 'input'))

        return connections

    if task_groups:
        # 如果提供了 task_groups，根据依赖关系构建 edges
        for group in task_groups:
            if isinstance(group, list) and len(group) > 1:
                # 同一组内的任务有依赖关系
                for i in range(len(group) - 1):
                    source_idx = group[i]
                    target_idx = group[i + 1]

                    # 找到对应的节点
                    source_node = next(
                        (n for n in nodes if n['id'] == node_id_map.get(source_idx)),
                        None,
                    )
                    target_node = next(
                        (n for n in nodes if n['id'] == node_id_map.get(target_idx)),
                        None,
                    )

                    if source_node and target_node:
                        # 判断输出输入文件对接
                        connections = _find_file_connections(source_node, target_node)

                        for source_param_name, target_param_name in connections:
                            edges.append(
                                {
                                    'id': f'edge-$id{edge_id_counter}',
                                    'source_node_id': source_node['id'],
                                    'source_parameter_name': source_param_name,
                                    'target_node_id': target_node['id'],
                                    'target_parameter_name': target_param_name,
                                }
                            )
                            edge_id_counter += 1
    else:
        # 如果没有提供 task_groups，根据 step_index 顺序构建简单的依赖关系
        sorted_params = sorted(params_dict_list, key=lambda x: x['step_index'])
        for i in range(len(sorted_params) - 1):
            source_step = sorted_params[i]['step_index']
            target_step = sorted_params[i + 1]['step_index']

            source_node = next(
                (n for n in nodes if n['id'] == node_id_map.get(source_step)), None
            )
            target_node = next(
                (n for n in nodes if n['id'] == node_id_map.get(target_step)), None
            )

            if source_node and target_node:
                # 判断输出输入文件对接
                connections = _find_file_connections(source_node, target_node)

                for source_param_name, target_param_name in connections:
                    edges.append(
                        {
                            'id': f'edge-$id{edge_id_counter}',
                            'source_node_id': source_node['id'],
                            'source_parameter_name': source_param_name,
                            'target_node_id': target_node['id'],
                            'target_parameter_name': target_param_name,
                        }
                    )
                    edge_id_counter += 1

    # 生成 template_uuid
    template_uuid = str(uuid.uuid4())

    # 构建完整的 JSON 结构（新格式）
    json_data = {
        'nodes': nodes,
        'edges': edges,
        'meta': {'template_uuid': template_uuid},
    }

    # 保存为 JSON 文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    logger.info(
        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} Saved parameters to {filepath}'
    )

    return filepath


def _get_parameter_type(param_schema: dict) -> str:
    """
    从参数 schema 中提取类型字符串

    Args:
        param_schema: 参数的 JSON schema

    Returns:
        str: 类型字符串（如 'str', 'int', 'float', 'typing.Dict', 'typing.List' 等）
    """
    param_type = param_schema.get('type', 'str')

    # 处理基本类型
    type_mapping = {
        'string': 'str',
        'integer': 'int',
        'number': 'float',
        'boolean': 'bool',
        'array': 'typing.List',
        'object': 'typing.Dict',
    }

    if param_type in type_mapping:
        return type_mapping[param_type]

    # 处理 anyOf, oneOf 等复杂类型
    if 'anyOf' in param_schema or 'oneOf' in param_schema:
        return 'typing.Union'

    # 处理枚举类型
    if 'enum' in param_schema:
        return 'str'  # 枚举通常用字符串表示

    # 默认返回 str
    return 'str'
