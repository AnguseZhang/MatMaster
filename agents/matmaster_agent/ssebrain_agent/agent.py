from typing import override, AsyncGenerator

from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from opik.integrations.adk import track_adk_agent_recursive

from .callback import init_ssebrain_before_agent, ssebrain_before_model, ssebrain_after_model, \
    enforce_single_tool_call
from .database_agent.agent import init_database_agent
from .deep_research_agent.agent import init_deep_research_agent
from .prompt import *
from agents.matmaster_agent.llm_config import MatMasterLlmConfig


class SSEBrainAgent(LlmAgent):
    def __init__(self, llm_config):
        prepare_state_before_agent = init_ssebrain_before_agent(llm_config)
        database_agent = init_database_agent(llm_config)
        deep_research_agent = init_deep_research_agent(llm_config)

        super().__init__(name="ssebrain_agent",
                         model=llm_config.gpt_4o,
                         description=description,
                         sub_agents=[
                             database_agent,
                             deep_research_agent,
                         ],
                         disallow_transfer_to_peers=True,
                         global_instruction=global_instruction,
                         instruction=instruction_en,
                         before_agent_callback=prepare_state_before_agent,
                         before_model_callback=[ssebrain_before_model],
                         after_model_callback=[enforce_single_tool_call, ssebrain_after_model])

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        prompt = ""
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
                        content=types.Content(parts=[types.Part(text=prompt)], role="system"))

        async for event in super()._run_async_impl(ctx):
            yield event


def init_ssebrain_agent(llm_config):
    ssebrain_agent = SSEBrainAgent(llm_config)
    # track_adk_agent_recursive(ssebrain_agent, llm_config.opik_tracer)

    return ssebrain_agent

