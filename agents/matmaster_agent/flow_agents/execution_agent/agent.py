import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.error_agent import ErrorHandleLlmAgent
from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.flow_agents.model import FlowStatusEnum, PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.plan_execution_check_agent.prompt import (
    PLAN_EXECUTION_CHECK_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    get_agent_class_and_name,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.sub_agents.mapping import MatMasterSubAgentsEnum
from agents.matmaster_agent.utils.event_utils import update_state_event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MatMasterSupervisorAgent(ErrorHandleLlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self._plan_execution_check_agent = ErrorHandleLlmAgent(
            name='plan_execution_check_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='汇总计划的执行情况，并根据计划提示下一步的动作',
            instruction=PLAN_EXECUTION_CHECK_INSTRUCTION,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )

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
    def plan_execution_check_agent(self) -> LlmAgent:
        return self._plan_execution_check_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state['plan']
        logger.info(f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan = {plan}')
        for index, step in enumerate(plan['steps']):
            if step.get('tool_name'):
                target_agent_name, target_agent_class = get_agent_class_and_name(
                    step['tool_name']
                )
                target_agent = target_agent_class(MatMasterLlmConfig)
                if step['status'] == 'plan':
                    yield update_state_event(
                        ctx, state_delta={'plan_index': index}
                    )  # TODO: One Agent Many Tools Call
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan_index = {ctx.session.state["plan_index"]}'
                    )
                    async for event in target_agent.run_async(ctx):
                        yield event

                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} {check_plan(ctx)}'
                    )
                    if check_plan(ctx) not in [
                        FlowStatusEnum.NO_PLAN,
                        FlowStatusEnum.NEW_PLAN,
                    ]:
                        # 检查之前的计划执行情况
                        async for (
                            plan_execution_check_event
                        ) in self.plan_execution_check_agent.run_async(ctx):
                            yield plan_execution_check_event

                    current_steps = ctx.session.state['plan']['steps']
                    if (
                        current_steps[index]['status'] != PlanStepStatusEnum.SUCCESS
                    ):  # 如果上一步没成功，退出
                        break
