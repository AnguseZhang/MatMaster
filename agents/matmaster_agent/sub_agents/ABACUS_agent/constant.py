import copy

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    BohriumExecutor,
    BohriumStorge,
)

if CURRENT_ENV in ['test', 'uat']:
    ABACUS_CALCULATOR_URL = 'http://toyl1410396.bohrium.tech:50004/sse'
else:
    # ABACUS_CALCULATOR_URL = 'https://abacus-agent-tools-uuid1751014104.app-space.dplink.cc/sse?token=7cae849e8a324f2892225e070443c45b'
    ABACUS_CALCULATOR_URL = 'http://toyl1410396.bohrium.tech:50001/sse'
ABACUS_AGENT_NAME = 'ABACUS_calculation_agent'
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-22618/abacusagenttools-matmaster-new-tool:v0.2.3'
ABACUS_CALCULATOR_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c32_m128_cpu'
ABACUS_CALCULATOR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
