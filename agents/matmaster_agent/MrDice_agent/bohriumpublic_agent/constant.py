from agents.matmaster_agent.constant import CURRENT_ENV

BOHRIUMPUBLIC_DATABASE_AGENT_NAME = 'bohriumpublic_agent'

if CURRENT_ENV in ['test', 'uat']:
    BOHRIUMPUBLIC_URL = 'http://fzwq1394978.bohrium.tech:50001/sse'
    # BOHRIUMPUBLIC_URL = 'http://jjxr1366132.bohrium.tech:50001/sse'
else:
    BOHRIUMPUBLIC_URL = 'https://mr-dice-bohriumpublic-uuid1758096978.app-space.dplink.cc/sse?token=f395e31f5d5d48bc9d1d7018989e12bd'
