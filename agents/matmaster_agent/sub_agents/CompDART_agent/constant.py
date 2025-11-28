import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

COMPDART_AGENT_NAME = 'compdart_agent'
if CURRENT_ENV in ['test', 'uat']:
    COMPDART_MCPServerUrl = 'http://pfmx1355864.bohrium.tech:50002/sse'
else:
    COMPDART_MCPServerUrl = 'https://dart-uuid1754393230.app-space.dplink.cc/sse?token=0480762b8539410c919723276c2c05fc'

COMPDART_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(COMPDART_AGENT_NAME, '')
)
COMPDART_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(COMPDART_AGENT_NAME) or 'c2_m4_cpu'
)
COMPDART_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
