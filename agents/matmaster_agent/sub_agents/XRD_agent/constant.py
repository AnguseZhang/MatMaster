import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

XRD_AGENT_NAME = 'xrd_agent'
if CURRENT_ENV in ['test', 'uat']:
    XRD_MCP_SERVER_URL = 'http://root@pkfz1410356.bohrium.tech:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'
else:
    XRD_MCP_SERVER_URL = 'http://root@pkfz1410356.bohrium.tech:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'

XRD_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
