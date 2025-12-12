import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.constant import (
    HEA_assistant_AgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

HEA_assistant_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
HEA_assistant_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[HEA_assistant_AgentName]['image']
)
HEA_assistant_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[HEA_assistant_AgentName]['machine_type'] or 'c2_m4_cpu'
)
HEA_assistant_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
