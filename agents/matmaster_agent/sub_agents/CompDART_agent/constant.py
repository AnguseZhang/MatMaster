import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

COMPDART_AGENT_NAME = 'compdart_agent'
if CURRENT_ENV in ['test', 'uat']:
    COMPDART_MCPServerUrl = 'http://pfmx1355864.bohrium.tech:50002/mcp'
else:
    COMPDART_MCPServerUrl = 'https://dart-uuid1754393230.appspace.bohrium.com/mcp?token=b3a955c99823427683843616328023d8'

COMPDART_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dpa-calculator:10fe4948'
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'
COMPDART_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
