import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.utils.event_utils import update_state_event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlanMakeAgent(SchemaAgent):
    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            yield event

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan = {ctx.session.state["plan"]}'
        )
        # 计算 feasibility
        update_plan = ctx.session.state['plan']
        update_plan['feasibility'] = 'null'
        total_steps = len(update_plan['steps'])
        exist_step = 0
        for index, step in enumerate(update_plan['steps']):
            if index == 0 and not step['tool_name']:
                break
            if step['tool_name']:
                exist_step += 1
            else:
                break
        if exist_step != total_steps:
            update_plan['feasibility'] = 'part'
        else:
            update_plan['feasibility'] = 'full'

        yield update_state_event(ctx, state_delta={'plan': update_plan})
