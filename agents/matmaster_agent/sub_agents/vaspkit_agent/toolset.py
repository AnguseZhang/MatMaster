import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG
from agents.matmaster_agent.sub_agents.vaspkit_agent.constant import VASPKIT_AGENT_NAME

VASPKIT_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
VASPKIT_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[VASPKIT_AGENT_NAME]['image']
)
VASPKIT_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[VASPKIT_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
VASPKIT_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
