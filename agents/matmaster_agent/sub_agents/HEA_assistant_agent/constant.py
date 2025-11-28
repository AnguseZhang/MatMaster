import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

HEA_assistant_AgentName = 'HEA_assistant_agent'
HEA_assistant_agent_ServerUrl = 'http://yqwl1369135.bohrium.tech:50001/sse'

HEA_assistant_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
HEA_assistant_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(HEA_assistant_AgentName, '')
)
HEA_assistant_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(HEA_assistant_AgentName) or 'c2_m4_cpu'
)
HEA_assistant_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
