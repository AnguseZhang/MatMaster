import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.state import MULTI_PLANS
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

            if ctx.session.state.get(MULTI_PLANS):
                logger.info(
                    f'{ctx.session.id} multi_plans = {ctx.session.state[MULTI_PLANS]}'
                )
                break
            else:
                logger.error(f'{ctx.session.id} Multi Plans Generate Error, Retry')

        if not ctx.session.state.get(MULTI_PLANS):
            raise RuntimeError(
                f'{ctx.session.id} After Retry, Multi Plans Generate Still Error!!'
            )

        # 计算 feasibility
        update_multi_plans = ctx.session.state['multi_plans']
        for update_plan in update_multi_plans['plans']:
            update_plan['feasibility'] = 'null'
            total_steps = len(update_plan.get('steps', []))
            exist_step = 0
            update_plan_steps = []
            for step in update_plan.get('steps', []):
                if not step['tool_name']:
                    step['tool_name'] = 'llm_tool'
                update_plan_steps.append(step)
            update_plan['steps'] = update_plan_steps

            for index, step in enumerate(update_plan['steps']):
                if index == 0 and not step['tool_name']:
                    break
                if step['tool_name']:
                    exist_step += 1
                else:
                    break
            if not exist_step:
                pass
            elif exist_step != total_steps:
                update_plan['feasibility'] = 'part'
            else:
                update_plan['feasibility'] = 'full'

        yield update_state_event(ctx, state_delta={'multi_plans': update_multi_plans})
