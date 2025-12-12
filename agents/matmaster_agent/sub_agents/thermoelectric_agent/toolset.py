import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.thermoelectric_agent.constant import (
    ThermoelectricAgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

ThermoelectricBohriumExecutor = copy.deepcopy(BohriumExecutor)
ThermoelectricBohriumStorge = copy.deepcopy(BohriumStorge)

ThermoelectricBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[ThermoelectricAgentName]['image']
)
ThermoelectricBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[ThermoelectricAgentName]['machine_type'] or 'c2_m4_cpu'
)
