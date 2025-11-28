import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

VASPKIT_AGENT_NAME = 'vaspkit_agent'
if CURRENT_ENV in ['test', 'uat']:
    VASPKIT_MCP_SERVER_URL = 'http://ehoz1408594.bohrium.tech:50001/sse'
else:
    VASPKIT_MCP_SERVER_URL = 'http://ehoz1408594.bohrium.tech:50001/sse'
    # VASPKIT_MCP_SERVER_URL = 'https://vaspkit-tool-uuid1751897568.appspace.bohrium.com/sse?token=190bfac86d9c4f08997ded346ef1a315'

VASPKIT_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
VASPKIT_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(VASPKIT_AGENT_NAME, '')
)

VASPKIT_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(VASPKIT_AGENT_NAME) or 'c2_m4_cpu'
)
VASPKIT_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
