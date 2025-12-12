import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

ABACUS_CALCULATOR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[ABACUS_AGENT_NAME]['image']
)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[ABACUS_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
ABACUS_CALCULATOR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
