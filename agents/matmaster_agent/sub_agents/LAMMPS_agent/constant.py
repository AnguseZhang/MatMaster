from agents.matmaster_agent.constant import (
    CURRENT_ENV,
)

if CURRENT_ENV in ['test', 'uat']:
    LAMMPS_URL = 'http://qpus1389933.bohrium.tech:50004/sse'
else:
    LAMMPS_URL = 'https://lammps-agent-uuid1763559305.appspace.bohrium.com/sse?token=6e158d039c1f46399578cef5e286dd4a'

LAMMPS_AGENT_NAME = 'LAMMPS_agent'
