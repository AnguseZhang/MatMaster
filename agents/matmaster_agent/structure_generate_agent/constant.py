from agents.matmaster_agent.constant import CURRENT_ENV

StructureGenerateAgentName = 'structure_generate_agent'

if CURRENT_ENV in ['test', 'uat']:
    StructureGenerateServerUrl = 'http://cned1392970.bohrium.tech:50001/sse'
else:
    StructureGenerateServerUrl = 'https://cystalformer-uuid1754551471.app-space.dplink.cc/sse?token=1750cd294e6c4270946ae37107a725ff'
