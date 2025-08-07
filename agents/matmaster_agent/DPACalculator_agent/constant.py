import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge

DPACalulator_AGENT_NAME = "dpa_calculator_agent"
DPA_CALCULATOR_URL = "https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=fa66cc76b6724d5590a89546772963fd"
DPACalulator_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
DPACalulator_BOHRIUM_EXECUTOR["machine"]["remote_profile"]["image_address"] = \
    "registry.dp.tech/dptech/dpa-calculator:85b4fe74"
DPACalulator_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
