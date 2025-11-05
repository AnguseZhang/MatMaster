from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_CLASS_MAPPING,
    ALL_AGENT_TOOLS_DICT,
)


def get_agent_class_and_name(tool_name):
    target_agent_name = ''
    for key, value in ALL_AGENT_TOOLS_DICT.items():
        if tool_name in value:
            target_agent_name = key
            break

    return target_agent_name, AGENT_CLASS_MAPPING[f'{target_agent_name}']
