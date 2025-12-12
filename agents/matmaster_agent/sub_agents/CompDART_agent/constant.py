from agents.matmaster_agent.constant import CURRENT_ENV

COMPDART_AGENT_NAME = 'compdart_agent'
if CURRENT_ENV in ['test', 'uat']:
    COMPDART_MCPServerUrl = 'http://pfmx1355864.bohrium.tech:50002/sse'
else:
    COMPDART_MCPServerUrl = 'https://dart-uuid1754393230.app-space.dplink.cc/sse?token=0480762b8539410c919723276c2c05fc'
