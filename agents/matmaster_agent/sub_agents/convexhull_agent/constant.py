from agents.matmaster_agent.constant import CURRENT_ENV

ConvexHullAgentName = 'convexhull_agent'
if CURRENT_ENV in ['test', 'uat']:
    ConvexHullServerUrl = 'http://root@mllo1368252.bohrium.tech:50004/sse'
else:
    ConvexHullServerUrl = 'https://convexhull-uuid1764213120.appspace.bohrium.com/sse?token=1ea4a0b8cd1e497585680680eccdae8b'
