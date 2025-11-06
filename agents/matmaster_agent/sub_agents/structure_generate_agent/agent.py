import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseAsyncJobAgent
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.structure_generate_agent.prompt import (
    StructureGenerateAgentDescription,
    StructureGenerateAgentInstruction,
    StructureGenerateAgentName,
)

from .constant import StructureGenerateServerUrl
from .finance import cost_func

StructureGenerateBohriumExecutor = copy.deepcopy(BohriumExecutor)
StructureGenerateBohriumStorge = copy.deepcopy(BohriumStorge)
StructureGenerateBohriumExecutor['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-788025/structure-generate-agent:small'
StructureGenerateBohriumExecutor['machine']['remote_profile'][
    'machine_type'
] = 'c8_m32_1 * NVIDIA 4090'

sse_params = SseServerParams(url=StructureGenerateServerUrl)

structure_generate_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=StructureGenerateBohriumStorge,
    executor=StructureGenerateBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class StructureGenerateAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            mcp_tools=[structure_generate_toolset],
            name=StructureGenerateAgentName,
            description=StructureGenerateAgentDescription,
            agent_instruction=StructureGenerateAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            sync_tools=[
                'build_bulk_structure_by_template',
                'build_bulk_structure_by_wyckoff',
                'make_supercell_structure',
                'make_doped_structure',
                'make_amorphous_structure',
                'build_molecule_structure_from_g2database',
                'build_molecule_structures_from_smiles',
                'add_cell_for_molecules',
                'build_surface_adsorbate',
                'build_surface_interface',
                'get_structure_info',
            ],
            cost_func=cost_func,
        )


def init_structure_generate_agent(llm_config) -> BaseAgent:
    return StructureGenerateAgent(llm_config)
