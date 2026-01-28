import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumStorge

XRD_AGENT_NAME = 'xrd_agent'
if CURRENT_ENV == 'test':
    XRD_MCP_SERVER_URL = 'https://f0f037ca00652ac8d5509652c91f1332.appspace.bohrium.com/sse?token=cfb9892682874677953eed08e92b45fe'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'
elif CURRENT_ENV == 'uat':
    XRD_MCP_SERVER_URL = 'https://1128e9e0f1fc927bb885835e0e7a6e48.appspace.bohrium.com/sse?token=cfb9892682874677953eed08e92b45fe'
else:
    XRD_MCP_SERVER_URL = 'http://root@pkfz1410356.bohrium.tech:50001/sse'
    # NMR_MCP_SERVER_URL = 'https://nmr-uuid1751618147.app-space.dplink.cc/sse?token=beab553bf78b4c53a7490531d14492c4'

XRD_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
