from typing import AsyncGenerator

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import context_function_event


class HandleFileUploadMixin(BaseMixin):
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        prompt = ''
        if ctx.user_content and ctx.user_content.parts:
            for part in ctx.user_content.parts:
                if part.text:
                    prompt += part.text
                elif part.inline_data:
                    pass  # Inline data is currently not processed
                elif part.file_data:
                    prompt += f", file_url = {part.file_data.file_uri}"

                    # 包装成function_call，来避免在历史记录中展示
                    for event in context_function_event(
                        ctx,
                        self.name,
                        'system_upload_file',
                        {'prompt': prompt},
                        ModelRole,
                    ):
                        yield event

        # Delegate to parent implementation for the actual processing
        async for event in super()._run_events(ctx):
            yield event
