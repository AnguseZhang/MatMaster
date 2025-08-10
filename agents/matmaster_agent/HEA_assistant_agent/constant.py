import copy
from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
HEA_assistant_AgentName = "HEA_assistant_agent"
HEA_assistant_agent_ServerUrl = "http://yqwl1369135.bohrium.tech:50001/sse"

HEA_assistant_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
HEA_assistant_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dp/native/prod-485756/mcphub:heafinal"
HEA_assistant_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)

	
