from agents.matmaster_agent.constant import CURRENT_ENV

DPACalulator_AGENT_NAME = 'dpa_calculator_agent'
if CURRENT_ENV == 'test':
    DPAMCPServerUrl = 'http://qpus1389933.bohrium.tech:50001/sse'
elif CURRENT_ENV == 'uat':
    DPAMCPServerUrl = 'https://1415fe9fea0fa1e45dddcff5682239a0.appspace.uat.bohrium.com/sse?token=f812b4cc79ef47b4b2a1bb81c415367d'
else:
    # DPAMCPServerUrl = 'http://pfmx1355864.bohrium.tech:50001/sse'
    DPAMCPServerUrl = 'https://dpa-uuid1750659890.appspace.bohrium.com/sse?token=b2b94c52d10141e992514f9d17bcca23'
