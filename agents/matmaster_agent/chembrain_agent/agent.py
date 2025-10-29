from typing import AsyncGenerator, override

from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from agents.matmaster_agent.llm_config import LLMConfig

from .callback import (
    chembrain_after_model,
    chembrain_before_model,
    enforce_single_tool_call,
    init_chembrain_before_agent,
)
from .database_agent.agent import init_database_agent
from .deep_research_agent.agent import init_deep_research_agent
from .prompt import description, global_instruction, instruction_cch_v1
from .retrosyn_agent.agent import init_retrosyn_agent
from .smiles_conversion_agent.agent import init_smiles_conversion_agent
from .unielf_agent.agent import init_unielf_agent


class ChemBrainAgent(LlmAgent):
    def __init__(self, llm_config: LLMConfig):
        prepare_state_before_agent = init_chembrain_before_agent(llm_config)
        database_agent = init_database_agent(llm_config)
        deep_research_agent = init_deep_research_agent(llm_config)
        smiles_conversion_agent = init_smiles_conversion_agent(llm_config)
        unielf_agent = init_unielf_agent(llm_config)
        retrosyn_agent = init_retrosyn_agent(llm_config)

        super().__init__(
            name='chembrain_agent',
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

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        prompt = ''
        if ctx.user_content and ctx.user_content.parts:
            for part in ctx.user_content.parts:
                if part.text:
                    prompt += part.text
                elif part.inline_data:
                    pass
                elif part.file_data:
                    prompt += f", file_url = {part.file_data.file_uri}"
                    yield Event(
                        invocation_id=ctx.invocation_id,
                        author=self.name,
                        branch=ctx.branch,
                        content=types.Content(
                            parts=[types.Part(text=prompt)], role='system'
                        ),
                    )

        async for event in super()._run_async_impl(ctx):
            yield event


def init_chembrain_agent(llm_config):
    chembrain_agent = ChemBrainAgent(llm_config)
    # track_adk_agent_recursive(chembrain_agent, llm_config.opik_tracer)

    return chembrain_agent


# Example usage
# root_agent = init_chembrain_agent(MatMasterLlmConfig)
