from agents.matmaster_agent.constant import CURRENT_ENV

OPTIMADE_DATABASE_AGENT_NAME = 'optimade_agent'

if CURRENT_ENV in ['test', 'uat']:
    OPTIMADE_URL = 'http://cmaz1395916.bohrium.tech:50004/sse'
    # OPTIMADE_URL = 'http://jjxr1366132.bohrium.tech:50004/sse'
else:
    OPTIMADE_URL = 'http://fzwq1394978.bohrium.tech:50004/sse'
    # OPTIMADE_URL = 'https://material-data-retriever-uuid1754467958.app-space.dplink.cc/sse?token=16a1dd29dbb54cf9bf75748ba8df282d'
