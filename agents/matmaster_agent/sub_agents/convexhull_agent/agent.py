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
from agents.matmaster_agent.sub_agents.convexhull_agent.prompt import (
    ConvexHullAgentDescription,
    ConvexHullAgentInstruction,
)
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_IMAGE_ADDRESS,
    AGENT_MACHINE_TYPE,
)

from .constant import ConvexHullAgentName, ConvexHullServerUrl

ConvexHullBohriumExecutor = copy.deepcopy(BohriumExecutor)
ConvexHullBohriumStorge = copy.deepcopy(BohriumStorge)

ConvexHullBohriumExecutor['machine']['remote_profile']['image_address'] = (
    AGENT_IMAGE_ADDRESS.get(ConvexHullAgentName, '')
)
ConvexHullBohriumExecutor['machine']['remote_profile']['machine_type'] = (
    AGENT_MACHINE_TYPE.get(ConvexHullAgentName) or 'c2_m4_cpu'
)

sse_params = SseServerParams(url=ConvexHullServerUrl)

convexhull_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=ConvexHullBohriumStorge,
    executor=ConvexHullBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class ConvexHullAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[convexhull_toolset],
            name=ConvexHullAgentName,
            description=ConvexHullAgentDescription,
            instruction=ConvexHullAgentInstruction,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_convexhull_agent(llm_config) -> BaseAgent:
    return ConvexHullAgent(llm_config)
