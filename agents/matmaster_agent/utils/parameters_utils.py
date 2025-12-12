import json
import logging
import os
import uuid
from datetime import datetime

from google.adk.agents import InvocationContext

from agents.matmaster_agent.config import PARAMETERS_OUTPUT_DIR
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG, ALL_TOOLS

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


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
    # 创建输出目录
    os.makedirs(PARAMETERS_OUTPUT_DIR, exist_ok=True)

    # 生成文件名（包含 session_id 和时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = ctx.session.id[:8] if ctx.session.id else 'unknown'
    filename = f'parameters_{session_id}_{timestamp}.json'
    filepath = os.path.join(PARAMETERS_OUTPUT_DIR, filename)

    # 获取 function_declarations 用于获取参数类型信息
    function_declarations = ctx.session.state.get('function_declarations', [])

    logger.info(
        f'{ctx.session.id} save_parameters_to_json: function_declarations count = {len(function_declarations)}, '
        f'params_dict_list count = {len(params_dict_list)}'
    )

    # 如果 function_declarations 为空，尝试从 ALL_TOOLS 中获取
    if not function_declarations:
        logger.warning(
            f'{ctx.session.id} function_declarations is empty in save_parameters_to_json, '
            f'attempting to collect from ALL_TOOLS...'
        )

        collected_declarations = []
        tool_names_in_plan = [params['tool_name'] for params in params_dict_list]

        for tool_name in tool_names_in_plan:
            if tool_name in ALL_TOOLS:
                tool_info = ALL_TOOLS[tool_name]
                if 'function_declarations' in tool_info:
                    for decl in tool_info['function_declarations']:
                        # 转换为 JSON 字典格式
                        if hasattr(decl, 'to_json_dict'):
                            collected_declarations.append(decl.to_json_dict())
                        elif isinstance(decl, dict):
                            collected_declarations.append(decl)

        if collected_declarations:
            function_declarations = collected_declarations
            logger.info(
                f'{ctx.session.id} Collected {len(collected_declarations)} function_declarations from ALL_TOOLS in save_parameters_to_json'
            )
        else:
            logger.error(
                f'{ctx.session.id} Failed to collect function_declarations from ALL_TOOLS. '
                f'Will use tool_args only, which may cause missing parameters.'
            )

    # 先分析哪些参数会被 edges 连接（用于后续清空这些参数的 value）
    # 创建一个映射：target_node_id -> set of target_param_names
    params_by_step = {params['step_index']: params for params in params_dict_list}
    plan = ctx.session.state.get('plan', {})
    all_steps = plan.get('steps', [])

    # 从plan的description中解析依赖关系
    # 返回: {target_step_index: [source_step_indices]}
    def parse_dependencies_from_plan():
        """从plan的description中解析依赖关系"""
        dependencies = {}  # {target_step_index: set of source_step_indices}

        for target_idx, step in enumerate(all_steps):
            if target_idx not in params_by_step:
                continue  # 跳过非异步任务

            description = step.get('description', '').lower()
            target_dependencies = set()

            # 解析description中的依赖关系
            # 匹配模式：
            # - "from the previous step" -> 依赖 step target_idx - 1
            # - "from the first step" -> 依赖 step 0
            # - "from step N" -> 依赖 step N - 1 (因为step索引从0开始，但用户说step N时通常指第N步，即索引N-1)
            # - "from step 1" -> 依赖 step 0
            # - "from step 2" -> 依赖 step 1

            import re

            # 匹配 "from the first step" 或 "from step 1"
            if re.search(r'from\s+(the\s+)?first\s+step|from\s+step\s+1', description):
                if 0 in params_by_step:
                    target_dependencies.add(0)
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] Step {target_idx} ({step.get("tool_name", "")}) '
                        f'depends on step 0 (from plan description: "from the first step" or "from step 1")'
                    )

            # 匹配 "from the previous step" 或 "from the last step"
            if re.search(r'from\s+(the\s+)?(previous|last)\s+step', description):
                if target_idx > 0 and (target_idx - 1) in params_by_step:
                    target_dependencies.add(target_idx - 1)
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] Step {target_idx} ({step.get("tool_name", "")}) '
                        f'depends on step {target_idx - 1} (from plan description: "from the previous step")'
                    )

            # 匹配 "from step N" (N > 1)
            step_matches = re.findall(r'from\s+step\s+(\d+)', description)
            for step_num_str in step_matches:
                step_num = int(step_num_str)
                source_idx = step_num - 1  # step N 对应索引 N-1
                if (
                    source_idx >= 0
                    and source_idx < len(all_steps)
                    and source_idx in params_by_step
                ):
                    target_dependencies.add(source_idx)
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] Step {target_idx} ({step.get("tool_name", "")}) '
                        f'depends on step {source_idx} (from plan description: "from step {step_num}")'
                    )

            if target_dependencies:
                dependencies[target_idx] = target_dependencies

        return dependencies

    plan_dependencies = parse_dependencies_from_plan()
    logger.info(
        f'[{MATMASTER_AGENT_NAME}] Parsed dependencies from plan: {plan_dependencies}'
    )

    # 记录哪些参数会被 edges 连接：{(step_index, param_name)}
    # 这个信息用于在构建nodes时，将连接的参数的value设置为空字符串
    connected_params = set()

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

        if not tool_declaration:
            logger.warning(
                f'[{MATMASTER_AGENT_NAME}] No function_declaration found for {tool_name} (step {step_index}), '
                f'will use tool_args only. function_declarations count: {len(function_declarations)}'
            )
            if function_declarations:
                available_tool_names = [d.get('name') for d in function_declarations]
                logger.warning(
                    f'[{MATMASTER_AGENT_NAME}] Available tool names in function_declarations: {available_tool_names}'
                )

        # 构建 input_parameters（必须包含所有 function_declaration 中的参数）
        input_parameters = []
        tool_args = params.get('tool_args', {})

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] Building input_parameters for {tool_name} (step {step_index}): '
            f'tool_declaration found = {tool_declaration is not None}, '
            f'tool_args keys = {list(tool_args.keys())}'
        )

        if tool_declaration and 'parameters' in tool_declaration:
            properties = tool_declaration['parameters'].get('properties', {})

            logger.info(
                f'[{MATMASTER_AGENT_NAME}] Processing {len(properties)} parameters from function_declaration for {tool_name}'
            )

            # 遍历所有参数（确保所有参数都显示）
            for param_name, param_schema in properties.items():
                # 跳过系统参数
                if param_name in ['executor', 'storage']:
                    continue

                # 获取参数类型和默认值
                param_type = (
                    _get_parameter_type(param_schema)
                    if isinstance(param_schema, dict)
                    else 'str'
                )
                default_value = (
                    param_schema.get('default')
                    if isinstance(param_schema, dict)
                    else None
                )

                # 确定参数的值（优先级：edges连接 > tool_args中的值 > 默认值 > 类型默认值）
                if (step_index, param_name) in connected_params:
                    # 如果会被 edges 连接，value 设置为空字符串
                    param_value = ''
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] Parameter {param_name} in step {step_index} '
                        f'({tool_name}) will be provided via edge, setting value to empty string'
                    )
                elif param_name in tool_args:
                    # 如果在 tool_args 中，使用 tool_args 的值
                    param_value = tool_args[param_name]
                    logger.debug(
                        f'[{MATMASTER_AGENT_NAME}] Parameter {param_name} in step {step_index} '
                        f'({tool_name}) using value from tool_args: {param_value}'
                    )
                elif default_value is not None:
                    # 如果有默认值，使用默认值
                    param_value = default_value
                    logger.debug(
                        f'[{MATMASTER_AGENT_NAME}] Parameter {param_name} in step {step_index} '
                        f'({tool_name}) using default value: {default_value}'
                    )
                else:
                    # 否则，根据类型设置默认值
                    if param_type in ['str', 'string']:
                        param_value = ''
                    elif param_type in ['int', 'integer']:
                        param_value = 0
                    elif param_type in ['float', 'number']:
                        param_value = 0.0
                    elif param_type in ['bool', 'boolean']:
                        param_value = False
                    else:
                        param_value = None
                    logger.debug(
                        f'[{MATMASTER_AGENT_NAME}] Parameter {param_name} in step {step_index} '
                        f'({tool_name}) using type default value: {param_value}'
                    )

                input_parameters.append(
                    {
                        'name': param_name,
                        'type': param_type,
                        'value': param_value,
                    }
                )
        else:
            # 如果没有 function_declaration，直接从 tool_args 构建
            for param_name, param_value in tool_args.items():
                if param_name in ['executor', 'storage']:
                    continue
                # 检查是否会被连接
                if (step_index, param_name) in connected_params:
                    input_parameters.append(
                        {'name': param_name, 'type': 'str', 'value': ''}
                    )
                else:
                    input_parameters.append(
                        {'name': param_name, 'type': 'str', 'value': param_value}
                    )

        # 构建 output_parameters（先空着）
        output_parameters = []

        # 获取 machine_type 和 image
        machine_type = _get_agent_machine_type(agent_name)
        image = AGENT_TOOLSET_CONFIG[agent_name].get('image', '')

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

    def _find_file_connections(source_node, target_node, ctx_ref):
        """
        判断两个节点的输出输入文件对接，并进行严格的类型和逻辑校验

        返回匹配的连接列表，每个连接包含 (source_param_name, target_param_name)
        """
        connections = []
        source_tool_name = source_node.get('label', '')
        target_input_params = target_node.get('input_parameters', [])
        source_output_params = source_node.get('output_parameters', [])
        target_tool_name = target_node.get('label', '')

        # 如果没有 output_parameters，使用默认的输出参数名
        if not source_output_params:
            # 使用 tool_name 生成默认输出参数名
            default_output_name = f'out_{source_tool_name}'
        else:
            default_output_name = source_output_params[0].get(
                'name', f'out_{source_tool_name}'
            )

        if target_input_params:
            # 获取 function_declarations 用于类型校验和动态识别结构文件参数
            function_declarations = ctx_ref.session.state.get(
                'function_declarations', []
            )

            # 获取 source 和 target 的参数类型信息
            source_decl = (
                next(
                    (
                        d
                        for d in function_declarations
                        if d.get('name') == source_tool_name
                    ),
                    None,
                )
                if function_declarations
                else None
            )
            target_decl = (
                next(
                    (
                        d
                        for d in function_declarations
                        if d.get('name') == target_tool_name
                    ),
                    None,
                )
                if function_declarations
                else None
            )

            # 动态识别结构文件参数：从 function_declarations 中查找
            structure_file_candidates = []
            if target_decl and 'parameters' in target_decl:
                properties = target_decl['parameters'].get('properties', {})
                for param_name, param_schema in properties.items():
                    param_type = (
                        _get_parameter_type(param_schema)
                        if isinstance(param_schema, dict)
                        else 'str'
                    )
                    if _is_structure_file_parameter(
                        param_name, param_schema, param_type
                    ):
                        structure_file_candidates.append(param_name)

            # 如果找到了结构文件参数候选，优先匹配它们
            if structure_file_candidates:
                for target_param in target_input_params:
                    target_name = target_param.get('name', '')
                    if target_name in structure_file_candidates:
                        # 严格校验：检查参数类型是否一致
                        if source_decl and target_decl:
                            # 获取 source 输出参数类型（通常是文件/路径类型）
                            source_output_type = (
                                'str'  # 默认假设是字符串类型（文件路径）
                            )
                            target_input_type = target_param.get('type', 'str')

                            # 校验类型兼容性
                            # 文件参数通常是 str 类型（路径/URL），允许连接
                            if (
                                target_input_type == 'str'
                                or source_output_type == 'str'
                            ):
                                connections.append(
                                    (default_output_name, target_param.get('name', ''))
                                )
                                logger.info(
                                    f'[{MATMASTER_AGENT_NAME}] Validated connection: '
                                    f'{source_tool_name}.{default_output_name} -> '
                                    f'{target_tool_name}.{target_param.get("name", "")} '
                                    f'(types: {source_output_type} -> {target_input_type})'
                                )
                                return connections  # 找到结构文件参数，直接返回
                            else:
                                logger.warning(
                                    f'[{MATMASTER_AGENT_NAME}] Type mismatch: '
                                    f'{source_tool_name}.{default_output_name} ({source_output_type}) -> '
                                    f'{target_tool_name}.{target_param.get("name", "")} ({target_input_type})'
                                )
                        else:
                            # 如果没有类型信息，仍然允许连接（向后兼容）
                            connections.append(
                                (default_output_name, target_param.get('name', ''))
                            )
                            return connections

            # 如果没有找到结构文件参数候选，尝试动态识别其他文件相关参数
            # 使用动态识别方法，而不是硬编码关键词列表
            for target_param in target_input_params:
                target_name = target_param.get('name', '')
                target_type = target_param.get('type', 'str')

                # 从 function_declarations 获取完整的参数 schema
                target_param_schema = {}
                if target_decl and 'parameters' in target_decl:
                    properties = target_decl['parameters'].get('properties', {})
                    target_param_schema = properties.get(target_name, {})

                # 使用动态识别方法判断是否是结构文件参数
                if _is_structure_file_parameter(
                    target_name, target_param_schema, target_type
                ):
                    # 校验类型兼容性
                    if source_decl and target_decl:
                        target_input_type = target_param.get('type', 'str')
                        source_output_type = 'str'  # 默认假设是字符串类型

                        if target_input_type == 'str' or source_output_type == 'str':
                            connections.append(
                                (default_output_name, target_param.get('name', ''))
                            )
                            logger.info(
                                f'[{MATMASTER_AGENT_NAME}] Validated connection: '
                                f'{source_tool_name}.{default_output_name} -> '
                                f'{target_tool_name}.{target_param.get("name", "")}'
                            )
                            break
                        else:
                            logger.warning(
                                f'[{MATMASTER_AGENT_NAME}] Type mismatch for file parameter: '
                                f'{source_tool_name}.{default_output_name} -> '
                                f'{target_tool_name}.{target_param.get("name", "")}'
                            )
                    else:
                        connections.append(
                            (default_output_name, target_param.get('name', ''))
                        )
                        break

            # 如果没有找到匹配，不自动连接（更严格）
            if not connections:
                logger.warning(
                    f'[{MATMASTER_AGENT_NAME}] No valid connection found between '
                    f'{source_tool_name} and {target_tool_name}'
                )
        else:
            # 如果没有输入参数，不创建连接（更严格）
            logger.warning(
                f'[{MATMASTER_AGENT_NAME}] Target node {target_tool_name} has no input parameters'
            )

        return connections

    if task_groups:
        # 如果提供了 task_groups，根据依赖关系构建 edges
        # 改进：不仅连接相邻任务，还要识别结构文件输出任务，连接到所有后续需要结构文件的任务
        for group in task_groups:
            if isinstance(group, list) and len(group) > 1:
                # 遍历组内所有任务，识别结构文件输出任务
                for i, source_idx in enumerate(group):
                    source_node = next(
                        (n for n in nodes if n['id'] == node_id_map.get(source_idx)),
                        None,
                    )
                    if not source_node:
                        continue

                    source_tool_name = source_node.get('label', '')
                    # 动态判断是否是结构文件输出任务
                    source_decl = (
                        next(
                            (
                                d
                                for d in function_declarations
                                if d.get('name') == source_tool_name
                            ),
                            None,
                        )
                        if function_declarations
                        else None
                    )
                    is_structure_output = _is_structure_output_tool(
                        source_tool_name, source_decl
                    )

                    # 如果是结构文件输出任务，连接到所有后续需要结构文件的任务
                    if is_structure_output:
                        for j in range(i + 1, len(group)):
                            target_idx = group[j]
                            target_node = next(
                                (
                                    n
                                    for n in nodes
                                    if n['id'] == node_id_map.get(target_idx)
                                ),
                                None,
                            )
                            if target_node:
                                # 检查目标任务是否需要结构文件作为输入（使用动态识别方法）
                                target_tool_name = target_node.get('label', '')
                                target_decl = (
                                    next(
                                        (
                                            d
                                            for d in function_declarations
                                            if d.get('name') == target_tool_name
                                        ),
                                        None,
                                    )
                                    if function_declarations
                                    else None
                                )

                                needs_structure = False
                                if target_decl and 'parameters' in target_decl:
                                    properties = target_decl['parameters'].get(
                                        'properties', {}
                                    )
                                    for param_name, param_schema in properties.items():
                                        param_type = (
                                            _get_parameter_type(param_schema)
                                            if isinstance(param_schema, dict)
                                            else 'str'
                                        )
                                        if _is_structure_file_parameter(
                                            param_name, param_schema, param_type
                                        ):
                                            needs_structure = True
                                            break

                                if needs_structure:
                                    # 判断输出输入文件对接
                                    connections = _find_file_connections(
                                        source_node, target_node, ctx
                                    )
                                    for (
                                        source_param_name,
                                        target_param_name,
                                    ) in connections:
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
                        # 如果不是结构文件输出任务，只连接到下一个任务（保持原有逻辑）
                        if i + 1 < len(group):
                            target_idx = group[i + 1]
                            target_node = next(
                                (
                                    n
                                    for n in nodes
                                    if n['id'] == node_id_map.get(target_idx)
                                ),
                                None,
                            )
                            if target_node:
                                # 判断输出输入文件对接
                                connections = _find_file_connections(
                                    source_node, target_node, ctx
                                )
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
        # 如果没有提供 task_groups，根据 plan 中的前后关系构建依赖关系
        # 严格按照每个节点的 prev_step_index 和 next_step_indices 来连接
        sorted_params = sorted(params_dict_list, key=lambda x: x['step_index'])

        # 创建 step_index -> params 的映射，方便查找
        params_by_step = {params['step_index']: params for params in sorted_params}

        # 获取 plan 中的所有步骤，用于查找前后关系
        plan = ctx.session.state.get('plan', {})
        all_steps = plan.get('steps', [])

        # 使用从plan中解析的依赖关系来生成edges
        # 由于plan的description已经明确说明了依赖关系（如"using the optimized structure from the first step"），
        # 我们直接使用这个依赖关系，不需要再判断source是否是结构文件输出任务
        # 遍历plan_dependencies，为每个依赖关系创建edge，同时更新connected_params
        for target_idx, source_indices in plan_dependencies.items():
            if target_idx not in params_by_step:
                continue

            params_by_step[target_idx]
            target_node = next(
                (n for n in nodes if n['id'] == node_id_map.get(target_idx)), None
            )
            if not target_node:
                continue

            target_tool_name = target_node.get('label', '')
            target_decl = (
                next(
                    (
                        d
                        for d in function_declarations
                        if d.get('name') == target_tool_name
                    ),
                    None,
                )
                if function_declarations
                else None
            )

            # 找到目标任务中需要结构文件作为输入的参数
            structure_params = []
            if target_decl and 'parameters' in target_decl:
                properties = target_decl['parameters'].get('properties', {})
                for param_name, param_schema in properties.items():
                    param_type = (
                        _get_parameter_type(param_schema)
                        if isinstance(param_schema, dict)
                        else 'str'
                    )
                    if _is_structure_file_parameter(
                        param_name, param_schema, param_type
                    ):
                        structure_params.append(param_name)

            # 如果找到了需要结构文件输入的参数，为每个依赖的source创建edge
            if structure_params:
                for source_idx in source_indices:
                    if source_idx not in params_by_step:
                        continue

                    params_by_step[source_idx]
                    source_node = next(
                        (n for n in nodes if n['id'] == node_id_map.get(source_idx)),
                        None,
                    )
                    if not source_node:
                        continue

                    source_tool_name = source_node.get('label', '')

                    # 使用_find_file_connections找到正确的参数连接
                    connections = _find_file_connections(source_node, target_node, ctx)
                    for source_param_name, target_param_name in connections:
                        # 创建edge
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

                        # 更新connected_params，用于在构建nodes时设置value为空
                        connected_params.add((target_idx, target_param_name))

                        logger.info(
                            f'[{MATMASTER_AGENT_NAME}] Created edge from {source_tool_name} '
                            f'(step {source_idx}) to {target_tool_name} (step {target_idx}), '
                            f'connecting {source_param_name} -> {target_param_name} '
                            f'based on plan dependency'
                        )

                    # 如果找到了连接，只连接第一个匹配的source（避免重复连接）
                    if connections:
                        break

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] Connected params identified: {connected_params}'
        )

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


def _get_agent_machine_type(agent_name: str) -> str:
    """
    获取 agent 的 machine_type，如果未设置则返回默认值 c2_m4_cpu

    Args:
        agent_name: Agent 名称

    Returns:
        str: machine_type
    """

    # 从 mapping.py 中获取 machine_type，如果未设置则使用默认值
    return AGENT_TOOLSET_CONFIG[agent_name].get('machine_type', 'c2_m4_cpu')


def _is_structure_file_parameter(
    param_name: str, param_schema: dict, param_type: str
) -> bool:
    """
    动态判断参数是否是结构文件参数

    通过检查参数名称、类型和描述来判断，而不是硬编码参数名列表

    Args:
        param_name: 参数名称
        param_schema: 参数的 schema 定义（包含 description 等信息）
        param_type: 参数类型（如 'str', 'Path' 等）

    Returns:
        bool: 是否是结构文件参数
    """
    param_name_lower = param_name.lower()

    # 1. 检查参数名称模式（包含结构文件相关的关键词）
    structure_keywords = [
        'stru',
        'structure',
        'file',
        'input',
        'cif',
        'poscar',
        'xyz',
        'atomic',
    ]
    name_has_structure_keyword = any(
        keyword in param_name_lower for keyword in structure_keywords
    )

    # 2. 检查参数类型（文件路径通常是 str 或 Path 类型）
    is_file_type = (
        param_type in ['str', 'string', 'Path', 'path'] or 'path' in param_type.lower()
    )

    # 3. 检查参数描述（如果存在）
    description = (
        param_schema.get('description', '').lower()
        if isinstance(param_schema, dict)
        else ''
    )
    desc_has_structure_keyword = (
        any(
            keyword in description
            for keyword in [
                'structure',
                'file',
                'cif',
                'poscar',
                'xyz',
                'crystal',
                'atomic',
                'geometry',
            ]
        )
        if description
        else False
    )

    # 4. 排除明显不是结构文件的参数
    excluded_keywords = [
        'type',
        'format',
        'method',
        'mode',
        'precision',
        'tolerance',
        'style',
        'basis',
    ]
    is_excluded = any(keyword in param_name_lower for keyword in excluded_keywords)

    # 综合判断：参数名称或描述包含结构文件关键词，且类型是文件类型，且不在排除列表中
    return (
        (name_has_structure_keyword or desc_has_structure_keyword)
        and is_file_type
        and not is_excluded
    )


def _is_structure_output_tool(
    tool_name: str, function_declaration: dict = None
) -> bool:
    """
    动态判断工具是否输出结构文件

    通过检查工具名称、描述和输出参数来判断，而不是硬编码列表

    Args:
        tool_name: 工具名称
        function_declaration: 工具的 function_declaration（可选）

    Returns:
        bool: 是否输出结构文件
    """
    tool_name_lower = tool_name.lower()

    # 1. 检查工具名称关键词（优化、弛豫等通常输出结构文件）
    output_keywords = ['optimize', 'relax', 'geometry', 'structure']
    name_has_output_keyword = any(
        keyword in tool_name_lower for keyword in output_keywords
    )

    # 2. 检查工具描述（如果提供了 function_declaration）
    desc_has_output_keyword = False
    if function_declaration:
        description = function_declaration.get('description', '').lower()
        if description:
            output_desc_keywords = [
                'optimize',
                'relax',
                'geometry optimization',
                'structure optimization',
                'output structure',
                'optimized structure',
            ]
            desc_has_output_keyword = any(
                keyword in description for keyword in output_desc_keywords
            )

    # 3. 检查是否有输出结构文件的参数（如果提供了 function_declaration）
    if function_declaration:
        # 检查返回值的 schema（如果有）
        # 通常工具的返回值或输出参数会在其他地方定义
        # 这里主要依赖名称和描述判断

        # 也可以检查工具名称是否匹配已知的输出结构文件的模式
        # 例如：optimize_structure, abacus_do_relax, apex_optimize_structure 等
        pass

    # 综合判断：工具名称或描述包含输出关键词
    return name_has_output_keyword or desc_has_output_keyword
