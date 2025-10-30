from agents.matmaster_agent.constant import CURRENT_ENV

MOFDB_DATABASE_AGENT_NAME = 'mofdb_agent'

if CURRENT_ENV in ['test', 'uat']:
    MOFDB_URL = 'http://cmaz1395916.bohrium.tech:50002/sse'
    # MOFDB_URL = 'http://jjxr1366132.bohrium.tech:50002/sse'
else:
    MOFDB_URL = 'http://fzwq1394978.bohrium.tech:50002/sse'
    # MOFDB_URL = 'https://mr-dice-mofdb-uuid1758704787.app-space.dplink.cc/sse?token=c15a46f6440d41b086aca38446d959bf'
