import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    BohriumExecutor,
    BohriumStorge,
)
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.prompt import (
    FinetuneDPAAgentDescription,
    FinetuneDPAAgentInstruction,
)
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

from .constant import FinetuneDPAAgentName, FinetuneDPAServerUrl

FinetuneDPABohriumExecutor = copy.deepcopy(BohriumExecutor)
FinetuneDPABohriumStorge = copy.deepcopy(BohriumStorge)

FinetuneDPABohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(FinetuneDPAAgentName, '')
)
FinetuneDPABohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(FinetuneDPAAgentName) or 'c2_m4_cpu'
)

sse_params = SseServerParams(url=FinetuneDPAServerUrl)

finetune_dpa_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=FinetuneDPABohriumStorge,
    executor=FinetuneDPABohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class FinetuneDPAAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[finetune_dpa_toolset],
            name=FinetuneDPAAgentName,
            description=FinetuneDPAAgentDescription,
            instruction=FinetuneDPAAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_finetune_dpa_agent(llm_config) -> BaseAgent:
    return FinetuneDPAAgent(llm_config)
