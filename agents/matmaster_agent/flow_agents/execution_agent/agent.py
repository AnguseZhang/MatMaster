import logging
from typing import AsyncGenerator, override

from google.adk.agents import BaseAgent, InvocationContext
from google.adk.events import Event
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.model import MatMasterTargetAgentEnum
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.sub_agents.structure_generate_agent.agent import (
    init_structure_generate_agent,
)
from agents.matmaster_agent.utils.event_utils import update_state_event
from agents.matmaster_agent.utils.helper_func import get_target_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MatMasterSupervisorDemoAgent(ErrorHandleLlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self._structure_generate_agent = init_structure_generate_agent(
            MatMasterLlmConfig
        )

        self.name = MATMASTER_SUPERVISOR_AGENT
        self.model = MatMasterLlmConfig.default_litellm_model
        self.sub_agents = [self.structure_generate_agent]
        self.global_instruction = 'GlobalInstruction'
        self.instruction = 'AgentInstruction'
        self.description = 'AgentDescription'
        self.after_model_callback = [
            # matmaster_check_job_status,
            check_transfer(
                prompt=MatMasterCheckTransferPrompt,
                target_agent_enum=MatMasterTargetAgentEnum,
            ),
            # matmaster_hallucination_retry,
        ]

        return self

    @computed_field
    @property
    def structure_generate_agent(self) -> BaseAgent:
        return self._structure_generate_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state['plan']
        logger.info(f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan = {plan}')
        for index, step in enumerate(plan['steps']):
            target_agent: BaseAgent = get_target_agent(
                step['tool_name'], self.sub_agents
            )
            if step['status'] == 'plan':
                yield update_state_event(ctx, state_delta={'plan_index': index})
                async for event in target_agent.run_async(ctx):
                    yield event
