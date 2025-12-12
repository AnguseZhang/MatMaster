import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.structure_generate_agent.constant import (
    StructureGenerateAgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

StructureGenerateBohriumExecutor = copy.deepcopy(BohriumExecutor)
StructureGenerateBohriumStorge = copy.deepcopy(BohriumStorge)

StructureGenerateBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[StructureGenerateAgentName]['image']
)
StructureGenerateBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[StructureGenerateAgentName]['machine_type'] or 'c2_m4_cpu'
)
