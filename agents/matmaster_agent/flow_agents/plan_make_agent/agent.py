import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.state import CURRENT_STEP
from agents.matmaster_agent.utils.event_utils import update_state_event

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class PlanMakeAgent(DisallowTransferAndContentLimitSchemaAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        for _ in range(2):
            async for event in super()._run_events(ctx):
                yield event

            if ctx.session.state.get(CURRENT_STEP):
                logger.info(
                    f'{ctx.session.id} NEXT_STEP = {ctx.session.state[CURRENT_STEP]}'
                )
                break
            else:
                logger.error(f'{ctx.session.id} Multi Plans Generate Error, Retry')

        if not ctx.session.state.get(CURRENT_STEP):
            raise RuntimeError(
                f'{ctx.session.id} After Retry, Multi Plans Generate Still Error!!'
            )

        # 处理无工具的情况
        update_current_step = ctx.session.state[CURRENT_STEP]
        if not update_current_step['tool_name']:
            update_current_step['tool_name'] = 'llm_tool'

        yield update_state_event(ctx, state_delta={CURRENT_STEP: update_current_step})
