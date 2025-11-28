import copy

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

if CURRENT_ENV in ['test', 'uat']:
    LAMMPS_URL = 'http://qpus1389933.bohrium.tech:50004/sse'
else:
    LAMMPS_URL = 'https://lammps-agent-uuid1763559305.appspace.bohrium.com/sse?token=6e158d039c1f46399578cef5e286dd4a'

LAMMPS_AGENT_NAME = 'LAMMPS_agent'

LAMMPS_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
LAMMPS_BOHRIUM_EXECUTOR['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(LAMMPS_AGENT_NAME, '')
)
LAMMPS_BOHRIUM_EXECUTOR['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(LAMMPS_AGENT_NAME) or 'c2_m4_cpu'
)
LAMMPS_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
