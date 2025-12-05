from agents.matmaster_agent.constant import CURRENT_ENV

# Agent Name
PerovskiteAgentName = 'perovskite_research_agent'


# MCP Server URL for Perovskite Research server

if CURRENT_ENV in ['test', 'uat']:
    PEROVSKITE_RESEARCH_URL = 'http://cbqz1338812.bohrium.tech:50004/mcp'
    UNIMOL_SERVER_URL = 'http://acsa1402612.bohrium.tech:50001/mcp'
    # PEROVSKITE_RESEARCH_URL='http://dhxi1369865.bohrium.tech:50004/sse'
    # 'https://perovskite-rag-uuid1753420543.app-space.dplink.cc/sse?token=8d1cb39154134328a0caa1f55df84016'
else:
    PEROVSKITE_RESEARCH_URL = 'https://56d326d8139f904b679084778f1b3285.app-space.dplink.cc/sse?token=57bc01c18d6a4f71bb156f2ac0bbf0b8'
    # PEROVSKITE_RESEARCH_URL='http://dhxi1369865.bohrium.tech:50004/sse'
    UNIMOL_SERVER_URL = 'http://acsa1402612.bohrium.tech:50001/mcp'
