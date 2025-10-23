import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.job_agent import BaseAsyncJobAgent
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.finetune_dpa_agent.prompt import (
    FinetuneDPAAgentDescription,
    FinetuneDPAAgentInstruction,
    FinetuneDPAAgentName,
)
from agents.matmaster_agent.logger import matmodeler_logging_handler

from .constant import FinetuneDPAServerUrl

FinetuneDPABohriumExecutor = copy.deepcopy(BohriumExecutor)
FinetuneDPABohriumStorge = copy.deepcopy(BohriumStorge)
FinetuneDPABohriumExecutor['machine']['remote_profile'][
    'image_address'
] = 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:14'
FinetuneDPABohriumExecutor['machine']['remote_profile'][
    'machine_type'
] = 'c16_m64_1 * NVIDIA 4090'

sse_params = SseServerParams(url=FinetuneDPAServerUrl)

toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=FinetuneDPABohriumStorge,
    executor=FinetuneDPABohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class FinetuneDPAAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.gpt_5_chat,
            mcp_tools=[toolset],
            agent_name=FinetuneDPAAgentName,
            agent_description=FinetuneDPAAgentDescription,
            agent_instruction=FinetuneDPAAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_finetune_dpa_agent(llm_config) -> BaseAgent:
    return FinetuneDPAAgent(llm_config)
