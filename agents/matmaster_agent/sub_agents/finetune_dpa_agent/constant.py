from agents.matmaster_agent.constant import CURRENT_ENV

FinetuneDPAAgentName = 'finetune_dpa_agent'

if CURRENT_ENV in ['test', 'uat']:
    FinetuneDPAServerUrl = 'http://root@mllo1368252.bohrium.tech:50003/sse'
else:
    FinetuneDPAServerUrl = 'https://dpafinetune-uuid1761721868.app-space.dplink.cc/sse?token=336ee47a05e5407899fdeb50c9e806d0'
