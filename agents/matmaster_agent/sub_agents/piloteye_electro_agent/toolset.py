import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

PILOTEYE_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
PILOTEYE_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[PILOTEYE_ELECTRO_AGENT_NAME]['image']
)
PILOTEYE_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[PILOTEYE_ELECTRO_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
PILOTEYE_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
