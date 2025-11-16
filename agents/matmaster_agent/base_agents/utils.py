from deepmerge import always_merger


def update_tool_call_info_with_function_declarations(
    tool_call_info, function_declarations
):
    current_function_declaration = [
        item
        for item in function_declarations
        if item['name'] == tool_call_info['tool_name']
    ]
    required_params = current_function_declaration[0]['parameters']['required']

    for param in required_params:
        if (
            param in tool_call_info['tool_args'].keys()
            or param in tool_call_info['missing_tool_args']
        ):
            continue
        else:
            tool_call_info['missing_tool_args'].append(param)

    return tool_call_info, current_function_declaration


def update_tool_call_info_with_recommend_params(tool_call_info, recommend_params):
    tool_call_info['tool_args'] = always_merger.merge(
        tool_call_info['tool_args'], recommend_params
    )
    for arg in tool_call_info['missing_tool_args']:
        if arg in tool_call_info['tool_args'].keys():
            tool_call_info['missing_tool_args'].remove(arg)

    return tool_call_info
