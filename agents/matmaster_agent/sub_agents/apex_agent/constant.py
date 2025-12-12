from agents.matmaster_agent.constant import CURRENT_ENV

# Agent Name
ApexAgentName = 'apex_agent'

# MCP Server URL
if CURRENT_ENV in ['test', 'uat']:
    ApexServerUrl = 'http://rtvq1394775.bohrium.tech:50001/sse'
else:
    # ApexServerUrl = 'http://rtvq1394775.bohrium.tech:50001/sse'
    ApexServerUrl = 'https://apex-prime-uuid1754990126.appspace.bohrium.com/sse?token=334be07f71404e92bf7ab7eb4350f1ac'
