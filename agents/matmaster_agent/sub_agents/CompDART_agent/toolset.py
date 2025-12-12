import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

COMPDART_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[COMPDART_AGENT_NAME]['image']
)
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[COMPDART_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
COMPDART_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
