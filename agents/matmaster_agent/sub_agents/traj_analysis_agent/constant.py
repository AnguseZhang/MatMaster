from agents.matmaster_agent.constant import CURRENT_ENV

TrajAnalysisAgentName = 'traj_analysis_agent'

if CURRENT_ENV in ['test', 'uat']:
    TrajAnalysisMCPServerUrl = 'http://pfmx1355864.bohrium.tech:50004/sse'
else:
    TrajAnalysisMCPServerUrl = 'https://traj-analysis-mcp-uuid1753018121.app-space.dplink.cc/sse?token=e93e98d3c408478d9ff113b809de690c'
