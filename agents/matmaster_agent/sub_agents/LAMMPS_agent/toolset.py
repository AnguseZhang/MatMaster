import copy

from agents.matmaster_agent.constant import BohriumExecutor, BohriumStorge
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import LAMMPS_AGENT_NAME
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG

LAMMPS_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
LAMMPS_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_TOOLSET_CONFIG[LAMMPS_AGENT_NAME]['image']
)
LAMMPS_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_TOOLSET_CONFIG[LAMMPS_AGENT_NAME]['machine_type'] or 'c2_m4_cpu'
)
LAMMPS_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
