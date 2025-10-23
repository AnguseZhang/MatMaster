from agents.matmaster_agent.constant import CURRENT_ENV

FinetuneDPAAgentName = 'finetune_dpa_agent'

if CURRENT_ENV in ['test', 'uat']:
    FinetuneDPAServerUrl = 'http://root@mllo1368252.bohrium.tech:50003/sse'
else:
    FinetuneDPAServerUrl = 'https://thermoelectricmcp000-uuid1750905361.app-space.dplink.cc/sse?token=096592e0f567437cbf35ffeb6d33a2a6'
