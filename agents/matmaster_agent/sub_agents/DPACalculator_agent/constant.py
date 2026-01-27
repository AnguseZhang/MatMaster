import copy

from agents.matmaster_agent.constant import CURRENT_ENV, BohriumExecutor, BohriumStorge

DPACalulator_AGENT_NAME = 'dpa_calculator_agent'
if CURRENT_ENV == 'test':
    DPAMCPServerUrl = 'http://qpus1389933.bohrium.tech:50001/mcp'
elif CURRENT_ENV == 'uat':
    DPAMCPServerUrl = 'https://dpa-calculator-uat-2-uuid1767842102.appspace.uat.bohrium.com/mcp?token=7b67a2e7778d4eb3b2c255d2f975d585'
else:
    # DPAMCPServerUrl = 'http://pfmx1355864.bohrium.tech:50001/sse' # TODO: update backup prod url to mcp
    DPAMCPServerUrl = 'https://dpa-uuid1750659890.appspace.bohrium.com/mcp?token=b2b94c52d10141e992514f9d17bcca23'
DPACalulator_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
DPACalulator_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dpa-calculator:a86b37cc'
DPACalulator_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'
DPACalulator_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
