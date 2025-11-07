from datetime import datetime
from typing import AsyncGenerator, override

from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from agents.matmaster_agent.constant import (
    LOADING_END,
    LOADING_STATE_KEY,
    TMP_FRONTEND_STATE_KEY,
)

from .callback import save_response, update_invoke_message
from .constant import ReportAgentName, ReportAgentOutKey
from .prompt import description, instructions_v4_en


class ReportAgent(LlmAgent):
    def __init__(self, llm_config):
        selected_model = llm_config.gemini_2_5_pro

        super().__init__(
            name=ReportAgentName,
            model=selected_model,
            instruction=instructions_v4_en,
            description=description,
            output_key=ReportAgentOutKey,
            before_model_callback=update_invoke_message,
            after_model_callback=save_response,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in super()._run_async_impl(ctx):
            if event.content:
                print(datetime.now(), LOADING_END)
                yield Event(
                    author=self.name,
                    actions=EventActions(
                        state_delta={
                            TMP_FRONTEND_STATE_KEY: {LOADING_STATE_KEY: LOADING_END}
                        }
                    ),
                )
            yield event


def init_report_agent(llm_config):
    return ReportAgent(llm_config)
