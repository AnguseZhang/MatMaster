import logging
from typing import AsyncGenerator, override

from google.adk.agents import BaseAgent, InvocationContext
from google.adk.events import Event
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.flow_agents.utils import get_agent_class_and_name
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.sub_agents.mapping import MatMasterSubAgentsEnum
from agents.matmaster_agent.utils.event_utils import update_state_event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MatMasterSupervisorAgent(ErrorHandleLlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self.name = MATMASTER_SUPERVISOR_AGENT
        self.model = MatMasterLlmConfig.default_litellm_model
        self.global_instruction = 'GlobalInstruction'
        self.instruction = 'AgentInstruction'
        self.description = 'AgentDescription'
        self.after_model_callback = [
            # matmaster_check_job_status,
            check_transfer(
                prompt=MatMasterCheckTransferPrompt,
                target_agent_enum=MatMasterSubAgentsEnum,
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
            if step.get('tool_name'):
                target_agent_name, target_agent_class = get_agent_class_and_name(
                    step['tool_name']
                )
                target_agent = target_agent_class(
                    MatMasterLlmConfig, name_suffix=f"_{index}"
                )
                if step['status'] == 'plan':
                    yield update_state_event(
                        ctx, state_delta={'plan_index': index}
                    )  # TODO: One Agent Many Tools Call
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan_index = {ctx.session.state["plan_index"]}'
                    )
                    async for event in target_agent.run_async(ctx):
                        yield event
