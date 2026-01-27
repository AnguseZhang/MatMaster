import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

COMPDART_AGENT_NAME = 'compdart_agent'
if CURRENT_ENV in ['test', 'uat']:
    COMPDART_MCPServerUrl = 'http://pfmx1355864.bohrium.tech:50002/sse'
else:
    COMPDART_MCPServerUrl = 'https://dart-uuid1754393230.app-space.dplink.cc/sse?token=0480762b8539410c919723276c2c05fc'

COMPDART_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dpa-calculator:50e69ca3'
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'
COMPDART_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
