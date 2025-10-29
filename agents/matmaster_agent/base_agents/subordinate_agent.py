from typing import Optional

from google.adk.agents import InvocationContext

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
)


class SubordinateFeaturesMixin(BaseMixin):
    supervisor_agent: Optional[str] = None  # Direct supervisor agent in the hierarchy

    async def _after_events(self, ctx: InvocationContext):
        if self.supervisor_agent:
            for function_event in context_function_event(
                ctx,
                self.name,
                'transfer_to_agent',
                None,
                ModelRole,
                {'agent_name': self.supervisor_agent},
            ):
                yield function_event


# LlmAgent -> ErrorHandleAgent -> SubordinateAgent
class SubordinateLlmAgent(SubordinateFeaturesMixin, ErrorHandleLlmAgent):
    pass
