from agents.matmaster_agent.constant import CURRENT_ENV

OPENLAM_DATABASE_AGENT_NAME = 'openlam_agent'

if CURRENT_ENV in ['test', 'uat']:
    OPENLAM_URL = 'http://cmaz1395916.bohrium.tech:50003/sse'
    # OPENLAM_URL = 'http://jjxr1366132.bohrium.tech:50003/sse'
else:
    OPENLAM_URL = 'http://fzwq1394978.bohrium.tech:50003/sse'
    # OPENLAM_URL = 'https://mr-dice-openlam-uuid1758096918.app-space.dplink.cc/sse?token=c2c0edb9c99f454896c4965ef1a5cf28'
