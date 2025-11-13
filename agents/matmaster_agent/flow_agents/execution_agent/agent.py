import copy
import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferLlmAgent,
)
from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    get_agent_name,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.sub_agents.mapping import (
    MatMasterSubAgentsEnum,
)
from agents.matmaster_agent.utils.event_utils import update_state_event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MatMasterSupervisorAgent(DisallowTransferLlmAgent):
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
            MatMasterLlmConfig.opik_tracer.after_model_callback,
            # matmaster_hallucination_retry,
        ]

        return self

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state['plan']
        logger.info(f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan = {plan}')
        for index, step in enumerate(plan['steps']):
            if step.get('tool_name'):
                target_agent = get_agent_name(step['tool_name'], self.sub_agents)
                if step['status'] in [
                    PlanStepStatusEnum.PLAN,
                    PlanStepStatusEnum.PROCESS,
                    PlanStepStatusEnum.FAILED,
                ]:
                    yield update_state_event(
                        ctx, state_delta={'plan_index': index}
                    )  # TODO: One Agent Many Tools Call
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan_index = {ctx.session.state["plan_index"]}'
                    )
                    async for event in target_agent.run_async(ctx):
                        if (
                            ctx.session.state['plan']['steps'][index]['status']
                            == PlanStepStatusEnum.PLAN
                        ):
                            update_plan = copy.deepcopy(ctx.session.state['plan'])
                            update_plan['steps'][index][
                                'status'
                            ] = PlanStepStatusEnum.PROCESS
                            yield update_state_event(
                                ctx, state_delta={'plan': update_plan}
                            )
                        yield event

                    plan = ctx.session.state['plan']
                    logger.info(
                        f'[{MATMASTER_AGENT_NAME}] {ctx.session.id} plan = {plan}, {check_plan(ctx)}'
                    )
                    if check_plan(ctx) not in [
                        FlowStatusEnum.NO_PLAN,
                        FlowStatusEnum.NEW_PLAN,
                    ]:
                        # 检查之前的计划执行情况
                        async for execution_result_event in self.sub_agents[
                            -1
                        ].run_async(ctx):
                            yield execution_result_event

                    current_steps = ctx.session.state['plan']['steps']
                    if (
                        current_steps[index]['status'] != PlanStepStatusEnum.SUCCESS
                    ):  # 如果上一步没成功，退出
                        break
