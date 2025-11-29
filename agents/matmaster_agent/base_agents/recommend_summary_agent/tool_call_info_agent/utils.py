import logging

from deepmerge import always_merger

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def update_tool_call_info_with_function_declarations(
    tool_call_info, current_function_declaration
):
    if not current_function_declaration:
        logger.warning(
            f'No function declaration found for {tool_call_info.get("tool_name", "unknown")}'
        )
        return tool_call_info

    function_decl = current_function_declaration[0]
    parameters = function_decl.get('parameters', {})
    properties = parameters.get('properties', {})
    required_params = parameters.get('required', [])

    logger.info(f'required_params = {required_params}')
    logger.info(f'properties keys = {list(properties.keys())}')

    # 处理所有参数（包括必需参数和有默认值的可选参数）
    for param_name, param_schema in properties.items():
        # 跳过系统参数
        if param_name in ['executor', 'storage']:
            continue

        # 如果参数已经在 tool_args 或 missing_tool_args 中，跳过
        if (
            param_name in tool_call_info['tool_args'].keys()
            or param_name in tool_call_info['missing_tool_args']
        ):
            continue

        # 如果参数有默认值，添加到 tool_args 中
        if 'default' in param_schema:
            default_value = param_schema['default']
            tool_call_info['tool_args'][param_name] = default_value
            logger.info(
                f'Added parameter {param_name} with default value {default_value} to tool_args'
            )
        # 如果是必需参数，添加到 missing_tool_args
        elif param_name in required_params:
            tool_call_info['missing_tool_args'].append(param_name)
            logger.info(f'Added required parameter {param_name} to missing_tool_args')
        # 可选参数且没有默认值，也添加到 missing_tool_args（让 LLM 决定是否需要）
        else:
            tool_call_info['missing_tool_args'].append(param_name)
            logger.info(
                f'Added optional parameter {param_name} (no default) to missing_tool_args'
            )

    return tool_call_info


def update_tool_call_info_with_recommend_params(tool_call_info, recommend_params):
    tool_call_info['tool_args'] = always_merger.merge(
        tool_call_info['tool_args'], recommend_params
    )
    for arg in tool_call_info['missing_tool_args']:
        if arg in tool_call_info['tool_args'].keys():
            tool_call_info['missing_tool_args'].remove(arg)

    return tool_call_info
