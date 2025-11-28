import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

# Agent Name
ApexAgentName = 'apex_agent'

# MCP Server URL
if CURRENT_ENV in ['test', 'uat']:
    ApexServerUrl = 'http://rtvq1394775.bohrium.tech:50001/sse'
else:
    # ApexServerUrl = 'http://rtvq1394775.bohrium.tech:50001/sse'
    ApexServerUrl = 'https://apex-prime-uuid1754990126.appspace.bohrium.com/sse?token=334be07f71404e92bf7ab7eb4350f1ac'
# APEX专用的Bohrium执行器配置
ApexBohriumExecutor = copy.deepcopy(BohriumExecutor)
ApexBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(ApexAgentName, '')
)
ApexBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(ApexAgentName) or 'c2_m4_cpu'
)

# APEX专用的Bohrium存储配置
ApexBohriumStorage = copy.deepcopy(BohriumStorge)
