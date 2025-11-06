from google.adk.agents import BaseAgent

from agents.matmaster_agent.base_agents.subordinate_agent import SubordinateLlmAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.task_orchestrator_agent.constant import (
    TASK_ORCHESTRATOR_AGENT_DESCRIPTION,
    TASK_ORCHESTRATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.task_orchestrator_agent.prompt import (
    TASK_ORCHESTRATOR_AGENT_INSTRUCTION,
)


class TaskOrchestratorAgent(SubordinateLlmAgent):
    """An agent that orchestrates complex workflows from brief user prompts."""

    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=TASK_ORCHESTRATOR_AGENT_NAME,
            description=TASK_ORCHESTRATOR_AGENT_DESCRIPTION,
            instruction=TASK_ORCHESTRATOR_AGENT_INSTRUCTION,
            supervisor_agent=MATMASTER_AGENT_NAME,
        )


def init_task_orchestrator_agent(llm_config) -> BaseAgent:
    """Initialize the task orchestrator agent."""
    return TaskOrchestratorAgent(llm_config)
