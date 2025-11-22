import copy
import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.flow_agents.style import step_card
from agents.matmaster_agent.flow_agents.utils.plan_utils import (
    check_plan,
    get_agent_name,
)
from agents.matmaster_agent.flow_agents.utils.step_utils import (
    get_step_status,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.sub_agents.mapping import (
    MatMasterSubAgentsEnum,
)
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class MatMasterSupervisorAgent(DisallowTransferAndContentLimitLlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self.name = MATMASTER_SUPERVISOR_AGENT
        self.model = MatMasterLlmConfig.default_litellm_model
        self.global_instruction = 'GlobalInstruction'
        self.instruction = 'AgentInstruction'
        self.description = 'AgentDescription'
        self.after_model_callback = [
            check_transfer(
                prompt=MatMasterCheckTransferPrompt,
                target_agent_enum=MatMasterSubAgentsEnum,
            ),
            MatMasterLlmConfig.opik_tracer.after_model_callback,
        ]

        return self

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state['plan']
        logger.info(f'{ctx.session.id} plan = {plan}')
        for index, step in enumerate(plan['steps']):
            step_relationship = step['relationship']
            step_status = get_step_status(step)  # plan, process, failed
            if step_relationship == 'any':
                if step_status == PlanStepStatusEnum.PLAN:  # 所有 tool 均未执行
                    for step_tool_index, step_tool in enumerate(step['tools']):
                        target_agent = get_agent_name(
                            step_tool['tool_name'], self.sub_agents
                        )
                        logger.info(
                            f'{ctx.session.id} tool_name = {step_tool['tool_name']}, target_agent = {target_agent.name}'
                        )

                        update_plan = copy.deepcopy(ctx.session.state['plan'])
                        update_plan['steps'][index]['tools'][step_tool_index][
                            'status'
                        ] = PlanStepStatusEnum.PROCESS
                        yield update_state_event(
                            ctx,
                            state_delta={
                                'plan': update_plan,
                                'plan_index': index,
                                'tool_index': step_tool_index,
                            },
                        )
                        for (
                            materials_plan_function_call_event
                        ) in context_function_event(
                            ctx,
                            self.name,
                            'materials_plan_function_call',
                            {
                                'msg': f'According to the plan, I will call the `{step_tool['tool_name']}`: {step_tool['description']}'
                            },
                            ModelRole,
                        ):
                            yield materials_plan_function_call_event

                        logger.info(
                            f'{ctx.session.id} Before Run: plan_index = {ctx.session.state["plan_index"]}, plan = {ctx.session.state['plan']}'
                        )
                        for step_event in all_text_event(
                            ctx, self.name, step_card(index + 1, i18n), ModelRole
                        ):
                            yield step_event

                        async for event in target_agent.run_async(ctx):
                            yield event
                        logger.info(
                            f'{ctx.session.id} After Run: plan = {ctx.session.state['plan']}, {check_plan(ctx)}'
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
                        get_step_status(current_steps[index])
                        != PlanStepStatusEnum.SUCCESS
                    ):  # 如果上一步没成功，退出
                        break

                # for step_tool_index, step_tool in enumerate(step['tools']):
                #     target_agent = get_agent_name(step_tool['tool_name'], self.sub_agents)
                #     logger.info(
                #         f'{ctx.session.id} tool_name = {step_tool['tool_name']}, target_agent = {target_agent.name}'
                #     )
                #     if step_tool['status'] in [
                #         PlanStepStatusEnum.PLAN,
                #         PlanStepStatusEnum.PROCESS,
                #         PlanStepStatusEnum.FAILED,
                #         PlanStepStatusEnum.SUBMITTED,
                #     ]:
                #         if step_tool['status'] != PlanStepStatusEnum.SUBMITTED:
                #             update_plan = copy.deepcopy(ctx.session.state['plan'])
                #             update_plan['steps'][index][
                #                 'status'
                #             ] = PlanStepStatusEnum.PROCESS
                #             yield update_state_event(
                #                 ctx, state_delta={'plan': update_plan, 'plan_index': index}
                #             )
                #             for (
                #                     materials_plan_function_call_event
                #             ) in context_function_event(
                #                 ctx,
                #                 self.name,
                #                 'materials_plan_function_call',
                #                 {
                #                     'msg': f'According to the plan, I will call the `{step['tool_name']}`: {step['description']}'
                #                 },
                #                 ModelRole,
                #             ):
                #                 yield materials_plan_function_call_event
                #
                #         logger.info(
                #             f'{ctx.session.id} Before Run: plan_index = {ctx.session.state["plan_index"]}, plan = {ctx.session.state['plan']}'
                #         )
                #         async for event in target_agent.run_async(ctx):
                #             yield event
                #         logger.info(
                #             f'{ctx.session.id} After Run: plan = {ctx.session.state['plan']}, {check_plan(ctx)}'
                #         )
                #         if check_plan(ctx) not in [
                #             FlowStatusEnum.NO_PLAN,
                #             FlowStatusEnum.NEW_PLAN,
                #         ]:
                #             # 检查之前的计划执行情况
                #             async for execution_result_event in self.sub_agents[
                #                 -1
                #             ].run_async(ctx):
                #                 yield execution_result_event
                #
                #         current_steps = ctx.session.state['plan']['steps']
                #         if (
                #                 current_steps[index]['status'] != PlanStepStatusEnum.SUCCESS
                #         ):  # 如果上一步没成功，退出
                #             break
            elif step_relationship == 'all':
                pass
            else:
                raise TypeError(f'step_relationship = {step_relationship}')
