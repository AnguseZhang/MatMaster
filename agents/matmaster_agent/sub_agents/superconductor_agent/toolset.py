import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.superconductor_agent.constant import (
    SuperconductorAgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

SuperconductorBohriumExecutor = copy.deepcopy(BohriumExecutor)
SuperconductorBohriumStorge = copy.deepcopy(BohriumStorge)

SuperconductorBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[SuperconductorAgentName]['image']
)
SuperconductorBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[SuperconductorAgentName]['machine_type'] or 'c2_m4_cpu'
)
