from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.structure_generate_agent.callback import (
    regulate_savename_suffix,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.prompt import (
    StructureGenerateAgentDescription,
    StructureGenerateAgentInstruction,
)

from .constant import StructureGenerateAgentName, StructureGenerateServerUrl
from .finance import cost_func
from .toolset import StructureGenerateBohriumExecutor, StructureGenerateBohriumStorge

sse_params = SseServerParams(
    url=StructureGenerateServerUrl,
    timeout=120,
)

structure_generate_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=StructureGenerateBohriumStorge,
    executor=StructureGenerateBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class StructureGenerateAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig, name_suffix=''):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[structure_generate_toolset],
            name=StructureGenerateAgentName + name_suffix,
            before_tool_callback=regulate_savename_suffix,
            description=StructureGenerateAgentDescription,
            instruction=StructureGenerateAgentInstruction,
            dflow_flag=False,
            sync_tools=[
                'build_bulk_structure_by_template',
                'build_bulk_structure_by_wyckoff',
                'make_supercell_structure',
                'make_doped_structure',
                'make_amorphous_structure',
                'build_molecule_structures_from_smiles',
                'add_cell_for_molecules',
                'build_surface_slab',
                'build_surface_adsorbate',
                'build_surface_interface',
                'get_structure_info',
                'get_molecule_info',
            ],
            cost_func=cost_func,
        )


def init_structure_generate_agent(llm_config) -> BaseAgent:
    return StructureGenerateAgent(llm_config)
