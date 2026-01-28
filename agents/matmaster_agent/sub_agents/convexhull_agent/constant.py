from agents.matmaster_agent.constant import CURRENT_ENV

ConvexHullAgentName = 'convexhull_agent'
if CURRENT_ENV in ['test', 'uat']:
    ConvexHullServerUrl = 'https://convexhull-test-uuid1769078392.appspace.bohrium.com/sse?token=f45ef610fbbd446eb154f024dda3540c'
else:
    ConvexHullServerUrl = 'https://convexhull-uuid1764213120.appspace.bohrium.com/sse?token=1ea4a0b8cd1e497585680680eccdae8b'
