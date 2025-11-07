from agents.matmaster_agent.llm_config import LLMConfig

from ...base_agents.error_agent import ErrorHandleLlmAgent
from .callback import (
    chembrain_after_model,
    chembrain_before_model,
    enforce_single_tool_call,
    init_chembrain_before_agent,
)
from .constant import CHEMBRAIN_AGENT_NAME
from .database_agent.agent import init_database_agent
from .deep_research_agent.agent import init_deep_research_agent
from .prompt import description, global_instruction, instruction_cch_v1
from .retrosyn_agent.agent import init_retrosyn_agent
from .smiles_conversion_agent.agent import init_smiles_conversion_agent
from .unielf_agent.agent import init_unielf_agent


class ChemBrainAgent(ErrorHandleLlmAgent):
    def __init__(self, llm_config: LLMConfig):
        prepare_state_before_agent = init_chembrain_before_agent(llm_config)
        database_agent = init_database_agent(llm_config)
        deep_research_agent = init_deep_research_agent(llm_config)
        smiles_conversion_agent = init_smiles_conversion_agent(llm_config)
        unielf_agent = init_unielf_agent(llm_config)
        retrosyn_agent = init_retrosyn_agent(llm_config)

        super().__init__(
            name=CHEMBRAIN_AGENT_NAME,
            model=llm_config.default_litellm_model,
            description=description,
            sub_agents=[
                database_agent,
                deep_research_agent,
                unielf_agent,
                smiles_conversion_agent,
                retrosyn_agent,
            ],
            disallow_transfer_to_peers=True,
            global_instruction=global_instruction,
            instruction=instruction_cch_v1,
            before_agent_callback=prepare_state_before_agent,
            before_model_callback=[chembrain_before_model],
            after_model_callback=[enforce_single_tool_call, chembrain_after_model],
        )


def init_chembrain_agent(llm_config):
    chembrain_agent = ChemBrainAgent(llm_config)

    return chembrain_agent
