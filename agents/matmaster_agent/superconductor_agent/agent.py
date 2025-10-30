import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.superconductor_agent.prompt import (
    SuperconductorAgentDescription,
    SuperconductorAgentInstruction,
    SuperconductorAgentName,
)

from ..base_agents.public_agent import BaseAsyncJobAgent
from .constant import SuperconductorServerUrl

SuperconductorBohriumExecutor = copy.deepcopy(BohriumExecutor)
SuperconductorBohriumStorge = copy.deepcopy(BohriumStorge)
SuperconductorBohriumExecutor['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:13'
SuperconductorBohriumExecutor['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'

sse_params = SseServerParams(url=SuperconductorServerUrl)

toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=SuperconductorBohriumStorge,
    executor=SuperconductorBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class SuperconductorAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            mcp_tools=[toolset],
            name=SuperconductorAgentName,
            description=SuperconductorAgentDescription,
            agent_instruction=SuperconductorAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_superconductor_agent(llm_config) -> BaseAgent:
    return SuperconductorAgent(llm_config)
