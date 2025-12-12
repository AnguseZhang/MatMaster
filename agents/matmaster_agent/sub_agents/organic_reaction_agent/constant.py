from agents.matmaster_agent.constant import CURRENT_ENV

ORGANIC_REACTION_AGENT_NAME = 'organic_reaction_agent'
if CURRENT_ENV in ['test', 'uat']:
    ORGANIC_REACTION_SERVER_URL = 'http://luts1388252.bohrium.tech:50001/sse'
else:
    ORGANIC_REACTION_SERVER_URL = 'https://1f187c8bc462403c4646ab271007edf4.app-space.dplink.cc/sse?token=aca7d1ad24ef436faa4470eaea006c12'
