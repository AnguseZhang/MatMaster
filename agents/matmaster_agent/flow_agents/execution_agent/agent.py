import copy
import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.config import MAX_TOOL_RETRIES, USE_STEP_EXECUTOR
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.flow_agents.execution_agent.utils import (
    should_exit_retryLoop,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.step_executor_agent import (
    create_step_executor_agent,
    get_step_executor_instruction,
)
from agents.matmaster_agent.flow_agents.step_validation_agent.prompt import (
    STEP_VALIDATION_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.style import separate_card
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    find_alternative_tool,
    get_agent_name,
    has_self_check,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.state import PLAN, STEP_DESCRIPTION
from agents.matmaster_agent.sub_agents.mapping import (
    MatMasterSubAgentsEnum,
)
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def _get_step_description(step: dict) -> str:
    """Step text: execution uses 'description'; plan schema uses 'step_description'."""
    return step.get('description') or step.get('step_description', '')


def _get_available_tools_for_step_executor(sub_agents: list) -> list:
    """Tool names that correspond to execution sub_agents (excluding title + validation)."""
    agent_names = {s.name for s in sub_agents[:-2]}
    return [
        t for t, info in ALL_TOOLS.items() if info.get('belonging_agent') in agent_names
    ]


def _get_available_tools_str(tool_names: list) -> str:
    """Format tool list for Step Executor instruction."""
    return '\n'.join(
        f"- {t}: {ALL_TOOLS.get(t, {}).get('description', '')}" for t in tool_names
    )


def _get_prev_outputs_summary(ctx: InvocationContext, index: int) -> str:
    """Brief summary of previous step outputs (description + status) for Step Executor."""
    plan = ctx.session.state.get(PLAN, {})
    steps = plan.get('steps', [])[:index]
    if not steps:
        return '(none)'
    lines = []
    for i, step in enumerate(steps):
        desc = _get_step_description(step)
        status = step.get('status', '')
        short_desc = desc[:80] + ('...' if len(desc) > 80 else '')
        lines.append(f"Step {i + 1}: {short_desc} status={status}")
    return '\n'.join(lines)


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

    @property
    def validation_agent(self):
        return self.sub_agents[-1]

    @property
    def title_agent(self):
        return self.sub_agents[-2]

    async def _update_retry_count(
        self, ctx: InvocationContext, index, count
    ) -> AsyncGenerator[Event, None]:
        update_plan = copy.deepcopy(ctx.session.state[PLAN])
        if not count:
            update_plan['steps'][index]['retry_count'] = update_plan['steps'][
                index
            ].get('retry_count', count)
        else:
            update_plan['steps'][index]['retry_count'] = count
        yield update_state_event(ctx, state_delta={PLAN: update_plan})

    async def _construct_function_call_ctx(
        self, ctx: InvocationContext, index
    ) -> AsyncGenerator[Event, None]:
        update_plan = copy.deepcopy(ctx.session.state['plan'])
        current_tool_name = update_plan['steps'][index]['tool_name']
        current_tool_description = _get_step_description(update_plan['steps'][index])
        update_plan['steps'][index]['status'] = PlanStepStatusEnum.PROCESS
        yield update_state_event(
            ctx,
            state_delta={
                'plan': update_plan,
                'plan_index': index,
            },
        )
        for materials_plan_function_call_event in context_function_event(
            ctx,
            self.name,
            'materials_plan_function_call',
            {
                'msg': f'According to the plan, I will call the `{current_tool_name}`: {current_tool_description}'
            },
            ModelRole,
        ):
            yield materials_plan_function_call_event

    async def _core_execution_agent(
        self, ctx: InvocationContext, index
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f'{ctx.session.id} Before Run: plan_index = {ctx.session.state["plan_index"]}, plan = {ctx.session.state['plan']}'
        )
        if ctx.session.state[PLAN]['steps'][index]['retry_count']:
            separate_card_info = 'ReExecuteStep'
            retry_info = f'({ctx.session.state[PLAN]['steps'][index]['retry_count']}/{MAX_TOOL_RETRIES})'
        else:
            separate_card_info = 'Step'
            retry_info = ''

        yield update_state_event(
            ctx,
            state_delta={
                'separate_card_info': separate_card_info,
            },
        )

        # 引导标题
        async for title_event in self.title_agent.run_async(ctx):
            yield title_event
        if ctx.session.state[PLAN]['steps'][index]['retry_count']:
            step_title = (
                i18n.t(separate_card_info)
                + f'{retry_info}'
                + ': '
                + ctx.session.state.get('step_title', {}).get('title', '')
            )
        else:
            step_title = ctx.session.state.get('step_title', {}).get('title', '')
        if (
            ctx.session.state[PLAN]['steps'][index]['status']
            == PlanStepStatusEnum.SUBMITTED
        ):
            step_title = '获取任务结果'

        yield update_state_event(
            ctx,
            state_delta={
                'matmaster_flow_active': {
                    'title': step_title,
                    'font_color': '#0E6DE8',
                    'bg_color': '#EBF2FB',
                    'border_color': '#B7D3F7',
                }
            },
        )
        for matmaster_flow_event in context_function_event(
            ctx,
            self.name,
            'matmaster_flow',
            None,
            ModelRole,
            {
                'title': step_title,
                'status': 'start',
                'font_color': '#0E6DE8',
                'bg_color': '#EBF2FB',
                'border_color': '#B7D3F7',
            },
        ):
            yield matmaster_flow_event

        # 核心执行工具
        current_tool_name = ctx.session.state[PLAN]['steps'][index]['tool_name']
        target_agent = get_agent_name(current_tool_name, self.sub_agents)
        logger.info(
            f'{ctx.session.id} tool_name = {current_tool_name}, target_agent = {target_agent.name}'
        )
        async for event in target_agent.run_async(ctx):
            yield event
        logger.info(
            f'{ctx.session.id} After Run: plan = {ctx.session.state['plan']}, {check_plan(ctx)}'
        )

    async def _tool_result_validation(
        self, ctx: InvocationContext, index
    ) -> AsyncGenerator[Event, None]:
        current_tool_name = ctx.session.state[PLAN]['steps'][index]['tool_name']
        current_tool_description = _get_step_description(
            ctx.session.state[PLAN]['steps'][index]
        )
        lines = (
            f"用户原始请求: {ctx.user_content.parts[0].text}",
            f"当前步骤描述: {current_tool_description}",
            f"工具名称: {current_tool_name}",
            '请根据以上信息判断，工具的参数配置及对应的执行结果是否严格满足用户原始需求。',
        )
        validation_instruction = '\n'.join(lines)
        self.validation_agent.instruction = (
            STEP_VALIDATION_INSTRUCTION + validation_instruction
        )

        async for validation_event in self.validation_agent.run_async(ctx):
            yield validation_event

    async def _prepare_retry_fake_success(
        self, ctx: InvocationContext, index, validation_reason
    ) -> AsyncGenerator[Event, None]:
        # 重试次数+1
        async for _update_retry_event in self._update_retry_count(
            ctx, index, ctx.session.state[PLAN]['steps'][index]['retry_count'] + 1
        ):
            yield _update_retry_event
        logger.warning(
            f'{ctx.session.id} Step {index + 1} validation failed: {validation_reason}'
        )

        # 向用户显示校验失败信息
        for step_validation_failed_event in all_text_event(
            ctx,
            self.name,
            separate_card(f"步骤 {index + 1} 结果校验未通过"),
            ModelRole,
        ):
            yield step_validation_failed_event

        for validation_failed_event in all_text_event(
            ctx,
            self.name,
            f"{validation_reason}",
            ModelRole,
        ):
            yield validation_failed_event

        # 重新标记为进行中状态，准备重试
        update_plan = copy.deepcopy(ctx.session.state['plan'])
        update_plan['steps'][index]['status'] = PlanStepStatusEnum.PROCESS
        update_plan['steps'][index]['validation_failure_reason'] = validation_reason
        original_description = _get_step_description(
            ctx.session.state[PLAN]['steps'][index]
        )
        update_plan['steps'][index][
            'description'
        ] = f"{original_description}\n\n注意：上次执行因以下原因校验失败，请改进：{validation_reason}"
        yield update_state_event(ctx, state_delta={'plan': update_plan})

    async def _prepare_retry_failed_result(
        self, ctx: InvocationContext, index, validation_reason
    ) -> AsyncGenerator[Event, None]:
        # 重试次数+1
        async for _update_retry_event in self._update_retry_count(
            ctx, index, ctx.session.state[PLAN]['steps'][index]['retry_count'] + 1
        ):
            yield _update_retry_event
        update_plan = copy.deepcopy(ctx.session.state['plan'])
        update_plan['steps'][index]['status'] = PlanStepStatusEnum.PROCESS
        retry_count = ctx.session.state[PLAN]['steps'][index]['retry_count']
        if validation_reason:
            logger.info(
                f'{ctx.session.id} Step {index + 1} failed due to validation, retrying {retry_count}/{MAX_TOOL_RETRIES}. Reason: {validation_reason}'
            )
            # 在重试时更新步骤描述，包含校验失败的原因
            original_description = _get_step_description(
                ctx.session.state[PLAN]['steps'][index]
            )
            update_plan['steps'][index][
                'description'
            ] = f"{original_description}\n\n注意：上次执行因以下原因校验失败，请改进：{validation_reason}"
        else:
            logger.info(
                f'{ctx.session.id} Step {index + 1} execution failed, retrying {retry_count}/{MAX_TOOL_RETRIES}'
            )
        yield update_state_event(ctx, state_delta={'plan': update_plan})

    async def _prepare_retry_other_tool(
        self, ctx: InvocationContext, index, next_tool
    ) -> AsyncGenerator[Event, None]:
        logger.info(
            f'{ctx.session.id} Switching to alternative tool: {next_tool} for step {index + 1}'
        )

        # 更新plan中的tool_name和status
        update_plan = copy.deepcopy(ctx.session.state['plan'])
        update_plan['steps'][index]['tool_name'] = next_tool
        update_plan['steps'][index]['status'] = PlanStepStatusEnum.PROCESS
        original_description = _get_step_description(
            ctx.session.state[PLAN]['steps'][index]
        ).split('\n\n注意：')[
            0
        ]  # 移除之前的失败原因
        update_plan['steps'][index]['description'] = original_description
        yield update_state_event(ctx, state_delta={'plan': update_plan})

    async def _run_step_executor_and_update_plan(
        self, ctx: InvocationContext, index: int
    ) -> AsyncGenerator[Event, None]:
        """When USE_STEP_EXECUTOR, run Step Executor and update plan step tool_name."""
        plan = ctx.session.state[PLAN]
        step = plan['steps'][index]
        goal = _get_step_description(step)
        suggested_tool = step.get('tool_name')
        available_tool_names = _get_available_tools_for_step_executor(self.sub_agents)
        if not available_tool_names:
            logger.warning(
                f'{ctx.session.id} Step Executor: no available tools for step {index + 1}, keep suggested_tool={suggested_tool}'
            )
            return
        available_tools_str = _get_available_tools_str(available_tool_names)
        prev_summary = _get_prev_outputs_summary(ctx, index)
        instruction = get_step_executor_instruction(
            goal=goal,
            prev_outputs_summary=prev_summary,
            available_tools_str=available_tools_str,
            suggested_tool=suggested_tool or None,
        )
        step_executor = create_step_executor_agent(
            MatMasterLlmConfig.tool_schema_model, instruction=instruction
        )
        async for _ in step_executor.run_async(ctx):
            pass  # consume events; result is written to state['step_executor']
        result = ctx.session.state.get('step_executor', {})
        chosen_tool = result.get('tool_name')
        if chosen_tool and chosen_tool in available_tool_names:
            update_plan = copy.deepcopy(plan)
            update_plan['steps'][index]['tool_name'] = chosen_tool
            logger.info(
                f'{ctx.session.id} Step Executor chose tool={chosen_tool} for step {index + 1}, reason={result.get("reason", "")}'
            )
            yield update_state_event(ctx, state_delta={PLAN: update_plan})
        else:
            logger.warning(
                f'{ctx.session.id} Step Executor returned invalid tool={chosen_tool}, keep plan tool_name={suggested_tool}'
            )

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state['plan']
        logger.info(f'{ctx.session.id} plan = {plan}')

        for index, initial_step in enumerate(plan['steps']):
            initial_current_tool_name = initial_step.get('tool_name')
            # 无 tool_name 的步必须由 Step Executor 选工具；未开启时报错并中止
            if not initial_current_tool_name and not USE_STEP_EXECUTOR:
                async for err_event in all_text_event(
                    ctx,
                    self.name,
                    f'步骤 {index + 1} 无指定工具；请在配置中开启 USE_STEP_EXECUTOR 由执行时选择工具。',
                    ModelRole,
                ):
                    yield err_event
                break
            tried_tools = (
                [initial_current_tool_name] if initial_current_tool_name else []
            )
            alternatives = (
                find_alternative_tool(initial_current_tool_name)
                if initial_current_tool_name
                else []
            )

            tool_attempt_success = False
            while not tool_attempt_success:
                if (
                    ctx.session.state[PLAN]['steps'][index]['status']
                    == PlanStepStatusEnum.SUCCESS
                ):
                    tool_attempt_success = True
                    break
                else:
                    # 初始化 retry_count
                    async for _update_retry_event in self._update_retry_count(
                        ctx, index, 0
                    ):
                        yield _update_retry_event

                    # 同一工具重试
                    while (
                        ctx.session.state[PLAN]['steps'][index]['retry_count']
                        <= MAX_TOOL_RETRIES
                    ):
                        # 制造工具调用上下文，已提交的任务跳过该步骤
                        if (
                            ctx.session.state[PLAN]['steps'][index]['status']
                            != PlanStepStatusEnum.SUBMITTED
                        ):
                            logger.info(
                                f'{ctx.session.id} Step {index + 1} status = {ctx.session.state[PLAN]['steps'][index]['status']}'
                            )
                            if (
                                USE_STEP_EXECUTOR
                                and ctx.session.state[PLAN]['steps'][index][
                                    'retry_count'
                                ]
                                == 0
                            ):
                                async for _ in self._run_step_executor_and_update_plan(
                                    ctx, index
                                ):
                                    yield _
                                # 无 tool_name 的步：Step Executor 未选出有效工具则中止
                                if not ctx.session.state[PLAN]['steps'][index].get(
                                    'tool_name'
                                ):
                                    async for err_event in all_text_event(
                                        ctx,
                                        self.name,
                                        f'步骤 {index + 1} 执行时未选出有效工具，请检查 Step Executor 或计划描述。',
                                        ModelRole,
                                    ):
                                        yield err_event
                                    return

                            async for (
                                _construct_function_call_event
                            ) in self._construct_function_call_ctx(ctx, index):
                                yield _construct_function_call_event

                        # 核心工具调用
                        async for _core_execution_event in self._core_execution_agent(
                            ctx, index
                        ):
                            yield _core_execution_event

                        current_steps = ctx.session.state['plan']['steps']
                        # 工具调用结果返回【成功】
                        if current_steps[index]['status'] == PlanStepStatusEnum.SUCCESS:
                            # 对成功的工具调用结果进行校验
                            if has_self_check(
                                ctx.session.state[PLAN]['steps'][index]['tool_name']
                            ):
                                # 校验工具结果
                                async for (
                                    _tool_result_validation_event
                                ) in self._tool_result_validation(ctx, index):
                                    yield _tool_result_validation_event

                                validation_result = ctx.session.state.get(
                                    'step_validation', {}
                                )
                                is_valid = validation_result.get('is_valid', True)
                                validation_reason = validation_result.get('reason', '')

                                # “假成功”结果，计划重试
                                if (not is_valid) and ctx.session.state[PLAN]['steps'][
                                    index
                                ]['retry_count'] < MAX_TOOL_RETRIES:
                                    async for (
                                        _prepare_retry_fake_success_event
                                    ) in self._prepare_retry_fake_success(
                                        ctx, index, validation_reason
                                    ):
                                        yield _prepare_retry_fake_success_event
                                else:
                                    # 校验成功，步骤完成
                                    tool_attempt_success = True
                                    break
                            else:
                                # 无需校验，步骤完成
                                tool_attempt_success = True
                                break
                        # 工具调用失败，且符合重试条件
                        elif (
                            current_steps[index]['status'] == PlanStepStatusEnum.FAILED
                            and ctx.session.state[PLAN]['steps'][index]['retry_count']
                            < MAX_TOOL_RETRIES
                        ):
                            # 对于某些错误，重试没有必要，直接退出
                            if should_exit_retryLoop(ctx):
                                break

                            validation_result = ctx.session.state.get(
                                'step_validation', {}
                            )
                            validation_reason = validation_result.get('reason', '')
                            async for (
                                _prepare_retry_failed_result_event
                            ) in self._prepare_retry_failed_result(
                                ctx, index, validation_reason
                            ):
                                yield _prepare_retry_failed_result_event
                        # 异步任务，直接退出当前函数
                        elif (
                            current_steps[index]['status']
                            == PlanStepStatusEnum.SUBMITTED
                        ):
                            return
                        else:
                            # 其他状态（SUBMITTED等），退出循环
                            break

                    # 更换其他工具重试
                    if (
                        not tool_attempt_success
                        and ctx.session.state['plan']['steps'][index]['status']
                        != PlanStepStatusEnum.SUBMITTED
                    ):
                        available_alts = [
                            alt for alt in alternatives if alt not in tried_tools
                        ]
                        if available_alts:
                            # 尝试替换工具
                            next_tool = available_alts[0]
                            tried_tools.append(next_tool)
                            async for (
                                _prepare_retry_other_tool_event
                            ) in self._prepare_retry_other_tool(ctx, index, next_tool):
                                yield _prepare_retry_other_tool_event
                        else:
                            logger.warning(
                                f'{ctx.session.id} No more alternative tools for step {index + 1}'
                            )
                            break  # 退出tool while

            # 最终仍然没有成功，中止计划
            if not tool_attempt_success:
                break
