import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.constant import (
    FinetuneDPAAgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

FinetuneDPABohriumExecutor = copy.deepcopy(BohriumExecutor)
FinetuneDPABohriumStorge = copy.deepcopy(BohriumStorge)

FinetuneDPABohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[FinetuneDPAAgentName]['image']
)
FinetuneDPABohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[FinetuneDPAAgentName]['machine_type'] or 'c2_m4_cpu'
)
