import copy

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

if CURRENT_ENV in ['test', 'uat']:
    ABACUS_CALCULATOR_URL = 'http://toyl1410396.bohrium.tech:50004/sse'
else:
    # ABACUS_CALCULATOR_URL = 'https://abacus-agent-tools-uuid1751014104.app-space.dplink.cc/sse?token=7cae849e8a324f2892225e070443c45b'
    ABACUS_CALCULATOR_URL = 'http://toyl1410396.bohrium.tech:50001/sse'
ABACUS_AGENT_NAME = 'ABACUS_calculation_agent'
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(ABACUS_AGENT_NAME, '')
)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(ABACUS_AGENT_NAME) or 'c2_m4_cpu'
)
ABACUS_CALCULATOR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
