import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge

PILOTEYE_ELECTRO_AGENT_NAME = "piloteye_electro_agent"
PILOTEYE_SERVER_URL = "http://nlig1368433.bohrium.tech:50001/sse"
PILOTEYE_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
PILOTEYE_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-13375/piloteye:mcpv03"
PILOTEYE_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
