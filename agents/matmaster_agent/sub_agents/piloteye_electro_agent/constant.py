from agents.matmaster_agent.constant import CURRENT_ENV

PILOTEYE_ELECTRO_AGENT_NAME = 'piloteye_electro_agent'

if CURRENT_ENV in ['test']:
    PILOTEYE_SERVER_URL = 'http://nlig1368433.bohrium.tech:50002/sse'
elif CURRENT_ENV in ['uat']:
    PILOTEYE_SERVER_URL = 'http://nlig1368433.bohrium.tech:50003/sse'
else:
    PILOTEYE_SERVER_URL = 'http://nlig1368433.bohrium.tech:50001/sse'
