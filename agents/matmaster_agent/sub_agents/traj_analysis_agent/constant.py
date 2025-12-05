from agents.matmaster_agent.constant import CURRENT_ENV

TrajAnalysisAgentName = 'traj_analysis_agent'

if CURRENT_ENV in ['test', 'uat']:
    TrajAnalysisMCPServerUrl = 'http://pfmx1355864.bohrium.tech:50004/sse'
else:
    TrajAnalysisMCPServerUrl = "https://traj-analysis-mcp-uuid1753018121.appspace.bohrium.com/sse?token=f7cb423b96044d09a5096e2591a26c0c"
