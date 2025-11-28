import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

PILOTEYE_ELECTRO_AGENT_NAME = 'piloteye_electro_agent'

if CURRENT_ENV in ['test']:
    PILOTEYE_SERVER_URL = 'http://nlig1368433.bohrium.tech:50002/sse'
elif CURRENT_ENV in ['uat']:
    PILOTEYE_SERVER_URL = 'http://nlig1368433.bohrium.tech:50003/sse'
else:
    PILOTEYE_SERVER_URL = 'http://nlig1368433.bohrium.tech:50001/sse'

PILOTEYE_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
PILOTEYE_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(PILOTEYE_ELECTRO_AGENT_NAME, '')
)
PILOTEYE_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(PILOTEYE_ELECTRO_AGENT_NAME) or 'c2_m4_cpu'
)
PILOTEYE_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
