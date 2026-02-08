from agents.matmaster_agent.constant import CURRENT_ENV

STRUCTURE_SEARCH_AGENT_NAME = 'structure_search_agent'

if CURRENT_ENV in ['test', 'uat']:
    STRUCTURE_SEARCH_URL = 'http://chvz1424099.bohrium.tech:50001/sse'
else:
    STRUCTURE_SEARCH_URL = 'http://chvz1424099.bohrium.tech:50002/sse'
