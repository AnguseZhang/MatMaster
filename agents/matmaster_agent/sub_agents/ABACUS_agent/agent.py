from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler
from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import (
    ABACUS_CALCULATOR_URL,
)
from agents.matmaster_agent.sub_agents.ABACUS_agent.prompt import (
    ABACUS_AGENT_DESCRIPTION,
    ABACUS_AGENT_INSTRUCTION,
    ABACUS_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ABACUS_agent.toolset import (
    ABACUS_CALCULATOR_BOHRIUM_EXECUTOR,
    ABACUS_CALCULATOR_BOHRIUM_STORAGE,
)

abacus_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(
        url=ABACUS_CALCULATOR_URL,
        sse_read_timeout=3600,
    ),
    executor=ABACUS_CALCULATOR_BOHRIUM_EXECUTOR,
    storage=ABACUS_CALCULATOR_BOHRIUM_STORAGE,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class ABACUSCalculatorAgent(BaseAsyncJobAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            tools=[abacus_toolset],
            name=ABACUS_AGENT_NAME,
            description=ABACUS_AGENT_DESCRIPTION,
            instruction=ABACUS_AGENT_INSTRUCTION,
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            sync_tools=[
                'abacus_prepare',
                'abacus_modify_input',
                'abacus_modify_stru',
                'abacus_collect_data',
            ],
        )


def init_abacus_calculation_agent(llm_config) -> BaseAgent:
    return ABACUSCalculatorAgent(llm_config)
