from agents.matmaster_agent.constant import CURRENT_ENV

VisualizerAgentName = 'visualizer_agent'

if CURRENT_ENV in ['test', 'uat']:
    VisualizerServerUrl = 'http://qpus1389933.bohrium.tech:50005/sse'
else:
    VisualizerServerUrl = 'https://visualization-agent-uuid1762946293.app-space.dplink.cc/sse?token=989b88f272fc4ef8a3106360265c3b96'
