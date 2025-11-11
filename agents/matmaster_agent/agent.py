import logging

from google.adk.agents import LlmAgent
from opik.integrations.adk import track_adk_agent_recursive

from agents.matmaster_agent.callback import matmaster_prepare_state, matmaster_set_lang
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.agent import MatMasterFlowAgent
from agents.matmaster_agent.llm_config import (
    MatMasterLlmConfig,
)

logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(
    logging.ERROR
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def init_matmaster_agent() -> LlmAgent:
    matmaster_agent = MatMasterFlowAgent(
        name=MATMASTER_AGENT_NAME,
        model=MatMasterLlmConfig.default_litellm_model,
        before_agent_callback=[
            matmaster_prepare_state,
            matmaster_set_lang,
        ],
    )
    track_adk_agent_recursive(matmaster_agent, MatMasterLlmConfig.opik_tracer)

    return matmaster_agent


# Global instance of the agent
root_agent = init_matmaster_agent()
