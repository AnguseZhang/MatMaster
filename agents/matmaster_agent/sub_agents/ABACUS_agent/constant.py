from agents.matmaster_agent.constant import (
    CURRENT_ENV,
)

ABACUS_AGENT_NAME = 'ABACUS_calculation_agent'

if CURRENT_ENV in ['test', 'uat']:
    ABACUS_CALCULATOR_URL = 'http://toyl1410396.bohrium.tech:50004/sse'
else:
    # ABACUS_CALCULATOR_URL = 'https://abacus-agent-tools-uuid1751014104.app-space.dplink.cc/sse?token=7cae849e8a324f2892225e070443c45b'
    ABACUS_CALCULATOR_URL = 'http://toyl1410396.bohrium.tech:50001/sse'
