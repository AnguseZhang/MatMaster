import copy

from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    BohriumExecutor,
    BohriumStorge,
)

if CURRENT_ENV in ['test', 'uat']:
    LAMMPS_URL = 'http://qpus1389933.bohrium.tech:50004/mcp'
else:
    LAMMPS_URL = 'https://lammps-agent-uuid1763559305.appspace.bohrium.com/mcp?token=6e158d039c1f46399578cef5e286dd4a'

LAMMPS_AGENT_NAME = 'LAMMPS_agent'

LAMMPS_BOHRIUM_EXECUTOR = copy.deepcopy(BohriumExecutor)
LAMMPS_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/lammps-agent:9ae769be'
LAMMPS_BOHRIUM_EXECUTOR['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'
LAMMPS_BOHRIUM_STORAGE = copy.deepcopy(BohriumStorge)
