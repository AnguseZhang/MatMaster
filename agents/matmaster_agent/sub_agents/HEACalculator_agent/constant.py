from agents.matmaster_agent.constant import CURRENT_ENV

HEACALCULATOR_AGENT_NAME = 'hea_calculator_agent'
if CURRENT_ENV in ['test', 'uat']:
    HEACALCULATOR_SERVER_URL = 'http://root@fewk1368842.bohrium.tech:50001/sse'
else:
    HEACALCULATOR_SERVER_URL = 'https://hea-calculator-uuid1754481039.app-space.dplink.cc/sse?token=37b90649f12c4b2e90db6bd9f2b3e9da'
# "http://root@mohx1369230.bohrium.tech:50001/sse"
# "http://root@fewk1368842.bohrium.tech:50001/sse"
