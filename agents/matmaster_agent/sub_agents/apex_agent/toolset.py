import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexAgentName
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)
ApexBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[ApexAgentName]['image']
)
ApexBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[ApexAgentName]['machine_type'] or 'c2_m4_cpu'
)

# APEX专用的Bohrium存储配置
ApexBohriumStorage = copy.deepcopy(BohriumStorge)
