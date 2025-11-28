import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

ORGANIC_REACTION_AGENT_NAME = 'organic_reaction_agent'
if CURRENT_ENV in ['test', 'uat']:
    ORGANIC_REACTION_SERVER_URL = 'http://luts1388252.bohrium.tech:50001/sse'
else:
    ORGANIC_REACTION_SERVER_URL = 'https://1f187c8bc462403c4646ab271007edf4.app-space.dplink.cc/sse?token=aca7d1ad24ef436faa4470eaea006c12'


ORGANIC_REACTION_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ORGANIC_REACTION_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(ORGANIC_REACTION_AGENT_NAME) or 'c2_m4_cpu'
)
ORGANIC_REACTION_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(ORGANIC_REACTION_AGENT_NAME, '')
)
ORGANIC_REACTION_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
