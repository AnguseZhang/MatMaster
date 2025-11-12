from agents.matmaster_agent.constant import CURRENT_ENV

VisualizerAgentName = 'visualizer_agent'

if CURRENT_ENV in ['test', 'uat']:
    VisualizerServerUrl = 'http://qpus1389933.bohrium.tech:50005/sse'
else:
    VisualizerServerUrl = 'http://qpus1389933.bohrium.tech:9999/sse'