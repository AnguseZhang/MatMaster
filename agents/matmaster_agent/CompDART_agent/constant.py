import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

INVAR_AGENT_NAME = 'invar_agent'
if CURRENT_ENV in ['test', 'uat']:
    INVARMCPServerUrl = 'http://pfmx1355864.bohrium.tech:50002/sse'
else:
    INVARMCPServerUrl = 'https://dart-uuid1754393230.app-space.dplink.cc/sse?token=0480762b8539410c919723276c2c05fc'

INVAR_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
INVAR_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dpa-calculator:ddbc2642'
INVAR_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'
INVAR_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
