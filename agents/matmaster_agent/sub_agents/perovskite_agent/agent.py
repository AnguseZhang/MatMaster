import logging
import os

import dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseSyncAgent
from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.llm_config import LLMConfig

from .constant import PEROVSKITE_PLOT_URL, PerovskiteAgentName
from .prompt import PerovskiteAgentDescription, PerovskiteAgentInstruction

logging.basicConfig(level=logging.INFO)


logging.info(f"Perovskite Agent URL: {PEROVSKITE_PLOT_URL}")


dotenv.load_dotenv()


logging.info(f"Environment name: {os.getenv('OPIK_PROJECT_NAME')}")
BOHRIUM_PROJECT_ID = os.getenv('BOHRIUM_PROJECT_ID')
logging.info(f"Bohrium Project ID: {BOHRIUM_PROJECT_ID}")

print(f"Perovskite Agent URL: {PEROVSKITE_PLOT_URL}")
print(f"Environment name: {os.getenv('OPIK_PROJECT_NAME')}")
print(f"Bohrium Project ID: {BOHRIUM_PROJECT_ID}")

perovskite_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=PEROVSKITE_PLOT_URL),
    storage=BohriumStorge,
)


def init_perovskite_agent(llm_config: LLMConfig):
    """Initialize Perovskite Solar Cell Data Analysis Agent using CalculationMCPLlmAgent."""
    # Choose model per flag with sensible fallbacks
    model = llm_config.default_litellm_model

    return BaseSyncAgent(
        model=model,
        name=PerovskiteAgentName,
        description=PerovskiteAgentDescription,
        instruction=PerovskiteAgentInstruction,
        tools=[perovskite_toolset],
    )
