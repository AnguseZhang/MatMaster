import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.convexhull_agent.constant import (
    ConvexHullAgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

ConvexHullBohriumExecutor = copy.deepcopy(BohriumExecutor)
ConvexHullBohriumStorge = copy.deepcopy(BohriumStorge)

ConvexHullBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[ConvexHullAgentName]['image']
)
ConvexHullBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[ConvexHullAgentName]['machine_type'] or 'c2_m4_cpu'
)
