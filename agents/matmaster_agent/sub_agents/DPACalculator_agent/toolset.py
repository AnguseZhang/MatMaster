import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

DPACalulator_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
DPACalulator_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[DPACalulator_AGENT_NAME]['image']
)
DPACalulator_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[DPACalulator_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
DPACalulator_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
