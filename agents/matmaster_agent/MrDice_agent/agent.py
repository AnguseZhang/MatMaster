from google.adk.agents import BaseAgent

from agents.matmaster_agent.base_agents.subordinate_agent import SubordinateLlmAgent
from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.MrDice_agent.bohriumpublic_agent.agent import (
    init_bohriumpublic_database_agent,
)
from agents.matmaster_agent.MrDice_agent.constant import MrDiceTargetAgentEnum
from agents.matmaster_agent.MrDice_agent.mofdb_agent.agent import (
    init_mofdb_database_agent,
)
from agents.matmaster_agent.MrDice_agent.openlam_agent.agent import (
    init_openlam_database_agent,
)
from agents.matmaster_agent.MrDice_agent.optimade_agent.agent import (
    init_optimade_database_agent,
)
from agents.matmaster_agent.MrDice_agent.prompt import (
    MrDiceAgentDescription,
    MrDiceAgentInstruction,
    MrDiceAgentName,
    MrDiceCheckTransferPrompt,
)


class MrDice_Agent(SubordinateLlmAgent):
    def __init__(self, llm_config: LLMConfig):
        optimade_agent = init_optimade_database_agent(llm_config)
        openlam_agent = init_openlam_database_agent(llm_config)
        bohriumpublic_agent = init_bohriumpublic_database_agent(llm_config)
        mofdb_agent = init_mofdb_database_agent(llm_config)
        super().__init__(
            model=llm_config.default_litellm_model,
            name=MrDiceAgentName,
            description=MrDiceAgentDescription,
            instruction=MrDiceAgentInstruction,
            sub_agents=[
                optimade_agent,
                openlam_agent,
                bohriumpublic_agent,
                mofdb_agent,
            ],
            supervisor_agent=MATMASTER_AGENT_NAME,
            after_model_callback=[
                check_transfer(
                    prompt=MrDiceCheckTransferPrompt,
                    target_agent_enum=MrDiceTargetAgentEnum,
                )
            ],
        )


def init_MrDice_agent(llm_config) -> BaseAgent:
    return MrDice_Agent(llm_config)
