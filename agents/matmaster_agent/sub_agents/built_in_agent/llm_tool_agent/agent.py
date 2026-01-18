import copy
from typing import AsyncGenerator

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.sub_agents.built_in_agent.llm_tool_agent.constant import (
    TOOL_AGENT_NAME,
)
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    update_state_event,
)


class LLMToolAgent(DisallowTransferAndContentLimitLlmAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=TOOL_AGENT_NAME,
            description='',
            instruction='Do not end with any question or prompt for user action.',
        )

    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        async for event in super()._run_events(ctx):
            yield event

        update_plan = copy.deepcopy(ctx.session.state['plan'])
        update_plan['steps'][ctx.session.state['plan_index']][
            'status'
        ] = PlanStepStatusEnum.SUCCESS
        yield update_state_event(ctx, state_delta={'plan': update_plan})

        current_step = ctx.session.state['plan']['steps'][
            ctx.session.state['plan_index']
        ]
        current_step_tool_name = current_step['tool_name']
        step_title = ctx.session.state.get('step_title', {}).get(
            'title',
            f"{i18n.t(ctx.session.state['separate_card_info'])} {ctx.session.state['plan_index'] + 1}: {current_step_tool_name}",
        )
        for matmaster_flow_event in context_function_event(
            ctx,
            self.name,
            'matmaster_flow',
            None,
            ModelRole,
            {
                'title': step_title,
                'status': 'end',
                'font_color': '#0E6DE8',
                'bg_color': '#EBF2FB',
                'border_color': '#B7D3F7',
            },
        ):
            yield matmaster_flow_event


def init_tool_agent(llm_config) -> LLMToolAgent:
    return LLMToolAgent(llm_config)
