import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

ORGANIC_REACTION_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ORGANIC_REACTION_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[ORGANIC_REACTION_AGENT_NAME]['image']
)
ORGANIC_REACTION_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[ORGANIC_REACTION_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
ORGANIC_REACTION_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
