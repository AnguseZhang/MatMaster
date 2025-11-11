from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    handle_upload_file_event,
)


class ExpandAgent(SchemaAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for upload_event in handle_upload_file_event(ctx, self.name):
            yield upload_event

        async for event in super()._run_events(ctx):
            yield event

        for expand_event in context_function_event(
            ctx,
            self.name,
            'update_user_content',
            {'update_user_content': ctx.session.state['expand']['update_user_content']},
            ModelRole,
            None,
        ):
            yield expand_event
