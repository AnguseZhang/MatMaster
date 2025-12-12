from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import (
    LAMMPS_AGENT_NAME,
    LAMMPS_URL,
)
from agents.matmaster_agent.sub_agents.LAMMPS_agent.toolset import (
    LAMMPS_BOHRIUM_EXECUTOR,
    LAMMPS_BOHRIUM_STORAGE,
)

lammps_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=LAMMPS_URL),
    executor=LAMMPS_BOHRIUM_EXECUTOR,
    storage=LAMMPS_BOHRIUM_STORAGE,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class LAMMPSAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[lammps_toolset],
            name=LAMMPS_AGENT_NAME,
            description='An agent specialized in running LAMMPS simulations',
            instruction="""
You are an expert in molecular dynamics simulations using LAMMPS.

You have three main tools at your disposal:
1. `convert_lammps_structural_format`: Converts structure files to LAMMPS format (conf.lmp)
2. `run_lammps`: Executes LAMMPS simulations
3. `orchestrate_lammps_input`: Generates LAMMPS input files based on natural language descriptions

When uploading input files, ensure the correct file suffixes:

1. Structure files typically use extensions like .cif, .vasp, .poscar, .conf, .lmp, etc.
2. Potential files commonly use extensions like .eam, .eam.alloy (for EAM potential), .pb, .pth (for DeePMD), .sw, .xml (for Tersoff), .json (for machine learning potentials), etc.

""",
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            sync_tools=[
                'orchestrate_lammps_input',
                'convert_lammps_structural_format',
            ],
        )


def init_lammps_agent(llm_config) -> BaseAgent:
    return LAMMPSAgent(llm_config)
