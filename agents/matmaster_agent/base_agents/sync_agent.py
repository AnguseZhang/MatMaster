import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.error_agent import (
    ErrorHandleBaseAgent,
)
from agents.matmaster_agent.base_agents.mcp_agent import (
    MCPAgent,
    MCPRunEventsMixin,
)
from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.style import tool_hallucination_card, tool_retry_failed_card
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    update_state_event,
)

logger = logging.getLogger(__name__)


class SyncMCPAgent(MCPRunEventsMixin, MCPAgent):
    pass


class ToolValidatorAgent(ErrorHandleBaseAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        if ctx.session.state['error_occurred']:
            return

        if ctx.session.state['tools_count'] > ctx.session.state['tools_count_ori']:
            yield update_state_event(
                ctx,
                state_delta={
                    'tools_count_ori': ctx.session.state['tools_count'],
                    'tool_hallucination': False,
                },
            )
            yield Event(author=self.name)
        else:
            if not ctx.session.state['tool_hallucination']:
                message = tool_hallucination_card(i18n=i18n)
                yield update_state_event(
                    ctx,
                    state_delta={
                        'tool_hallucination': True,
                    },
                )
            else:
                message = tool_retry_failed_card(i18n=i18n)

            for tool_hallucination_event in all_text_event(
                ctx,
                self.name,
                message,
                ModelRole,
            ):
                yield tool_hallucination_event

        logger.info(
            f'[{MATMASTER_AGENT_NAME}]:[{self.name}] state = {ctx.session.state}'
        )
