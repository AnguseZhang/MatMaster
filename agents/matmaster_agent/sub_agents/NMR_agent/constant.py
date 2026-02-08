import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

NMR_AGENT_NAME = 'nmr_agent'
if CURRENT_ENV in ['test', 'uat']:
    NMR_MCP_SERVER_URL = 'http://aubn1408899.bohrium.tech:50001/sse'
else:
    # NMR_MCP_SERVER_URL = 'http://aubn1408899.bohrium.tech:50001/sse'
    NMR_MCP_SERVER_URL = 'https://nmr-server-matmaster-uuid1764741165.appspace.bohrium.com/sse?token=1467bc01801642c09273966fcd04e3a6'

NMR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
