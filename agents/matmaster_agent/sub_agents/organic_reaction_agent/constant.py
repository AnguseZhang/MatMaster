import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

ORGANIC_REACTION_AGENT_NAME = 'organic_reaction_agent'
if CURRENT_ENV in ['test', 'uat']:
    ORGANIC_REACTION_SERVER_URL = 'http://luts1388252.bohrium.tech:50001/sse'
else:
    ORGANIC_REACTION_SERVER_URL = 'https://1f187c8bc462403c4646ab271007edf4.app-space.dplink.cc/sse?token=aca7d1ad24ef436faa4470eaea006c12'


ORGANIC_REACTION_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
ORGANIC_REACTION_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c32_m128_cpu'
ORGANIC_REACTION_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-13364/autots:0.1.0'
ORGANIC_REACTION_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
