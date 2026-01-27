import copy
import json
import logging
from typing import AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.base_callbacks.public_callback import check_transfer
from agents.matmaster_agent.config import MAX_TOOL_RETRIES
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.flow_agents.constant import MATMASTER_SUPERVISOR_AGENT
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.step_validation_agent.prompt import (
    STEP_VALIDATION_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.style import separate_card
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    find_alternative_tool,
    get_agent_name,
    get_self_check,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.prompt import MatMasterCheckTransferPrompt
from agents.matmaster_agent.state import ERROR_DETAIL, ERROR_OCCURRED
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

    @property
    def validation_agent(self):
        return self.sub_agents[-1]

    @property
    def title_agent(self):
        return self.sub_agents[-2]

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state['plan']
        logger.info(f'{ctx.session.id} plan = {plan}')

        for index, step in enumerate(plan['steps']):
            if step.get('tool_name'):
                current_tool_name = step['tool_name']
                tried_tools = [current_tool_name]
                alternatives = find_alternative_tool(current_tool_name)

                tool_attempt_success = False
                while not tool_attempt_success:
                    target_agent = get_agent_name(current_tool_name, self.sub_agents)
                    logger.info(
                        f'{ctx.session.id} tool_name = {current_tool_name}, target_agent = {target_agent.name}'
                    )
                    if step['status'] == PlanStepStatusEnum.SUCCESS:
                        tool_attempt_success = True
                        break
                    elif step['status'] in [
                        PlanStepStatusEnum.PLAN,
                        PlanStepStatusEnum.PROCESS,
                        PlanStepStatusEnum.FAILED,
                        PlanStepStatusEnum.SUBMITTED,
                    ]:
                        retry_count = 0
                        validation_reason = ''
                        # 同一工具重试
                        while retry_count <= MAX_TOOL_RETRIES:
                            # 制造工具调用上下文，已提交的任务跳过该步骤
                            if step['status'] != PlanStepStatusEnum.SUBMITTED:
                                update_plan = copy.deepcopy(ctx.session.state['plan'])
                                update_plan['steps'][index][
                                    'status'
                                ] = PlanStepStatusEnum.PROCESS
                                yield update_state_event(
                                    ctx,
                                    state_delta={
                                        'plan': update_plan,
                                        'plan_index': index,
                                    },
                                )
                                for (
                                    materials_plan_function_call_event
                                ) in context_function_event(
                                    ctx,
                                    self.name,
                                    'materials_plan_function_call',
                                    {
                                        'msg': f'According to the plan, I will call the `{current_tool_name}`: {step['description']}'
                                    },
                                    ModelRole,
                                ):
                                    yield materials_plan_function_call_event

                            logger.info(
                                f'{ctx.session.id} Before Run: plan_index = {ctx.session.state["plan_index"]}, plan = {ctx.session.state['plan']}'
                            )
                            if retry_count:
                                separate_card_info = 'ReExecuteStep'
                            else:
                                separate_card_info = 'Step'

                            yield update_state_event(
                                ctx,
                                state_delta={
                                    'separate_card_info': separate_card_info,
                                },
                            )

                            # 引导标题
                            async for title_event in self.title_agent.run_async(ctx):
                                yield title_event

                            step_title = ctx.session.state.get('step_title', {}).get(
                                'title',
                                f"{i18n.t(separate_card_info)} {index + 1}: {current_tool_name}",
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
                            truncation_mode = ctx.session.state.get('truncation_mode', False)
                            l1b_truncated = False
                            captured_function_calls = []
                            
                            async for event in target_agent.run_async(ctx):
                                # L1b 截断模式：检查 state 中是否有记录的 function_call
                                if truncation_mode == 'L1b':
                                    # 优先使用 private_callback 记录的原始工具信息
                                    state_captured = ctx.session.state.get('l1b_captured_function_calls', [])
                                    if state_captured and not l1b_truncated:
                                        captured_function_calls = state_captured
                                        logger.info(
                                            f'{ctx.session.id} L1b truncation: using captured function_calls from state, '
                                            f'count={len(captured_function_calls)}'
                                        )
                                        l1b_truncated = True
                                    # 如果 state 中没有，则尝试从 event 中捕获（备用方案）
                                    elif event.content and event.content.parts:
                                        for part in event.content.parts:
                                            if part.function_call:
                                                func_name = getattr(part.function_call, 'name', '')
                                                func_args = getattr(part.function_call, 'args', {})
                                                # 跳过内部 agent 调用，只在没有 state 记录时使用
                                                if not state_captured:
                                                    captured_function_calls.append({
                                                        'tool_name': func_name,
                                                        'tool_args': func_args,
                                                    })
                                                    logger.info(
                                                        f'{ctx.session.id} L1b truncation: captured function_call from event '
                                                        f'tool={func_name}, args={func_args}'
                                                    )
                                                    l1b_truncated = True
                                
                                yield event
                                
                                # 捕获到 function_call 后立即截断，不等待执行结果
                                if l1b_truncated:
                                    # 输出 L1b 截断事件
                                    for truncation_event in context_function_event(
                                        ctx,
                                        self.name,
                                        'matmaster_l1b_truncation',
                                        None,
                                        ModelRole,
                                        {
                                            'status': 'truncated_with_args',
                                            'step_index': index,
                                            'tool_name': current_tool_name,
                                            'function_calls': json.dumps(
                                                captured_function_calls,
                                                ensure_ascii=False
                                            ),
                                            'plan': json.dumps(
                                                ctx.session.state.get('plan', {}),
                                                ensure_ascii=False
                                            ),
                                        },
                                    ):
                                        yield truncation_event
                                    logger.info(
                                        f'{ctx.session.id} L1b truncation mode: '
                                        f'captured {len(captured_function_calls)} function calls, exiting'
                                    )
                                    return  # 截断退出
                            logger.info(
                                f'{ctx.session.id} After Run: plan = {ctx.session.state['plan']}, {check_plan(ctx)}'
                            )

                            current_steps = ctx.session.state['plan']['steps']
                            DOWNLOAD_RESULTS_TXT_FAILED = (
                                ctx.session.state[ERROR_OCCURRED]
                                and ctx.session.state[ERROR_DETAIL].startswith(
                                    'ClientResponseError'
                                )
                                and 'results.txt' in ctx.session.state[ERROR_DETAIL]
                            )
                            # 工具调用结果返回【成功】
                            if (
                                current_steps[index]['status']
                                == PlanStepStatusEnum.SUCCESS
                            ):
                                # 对成功的工具调用结果进行校验
                                if get_self_check(current_tool_name):
                                    lines = (
                                        f"用户原始请求: {ctx.user_content.parts[0].text}",
                                        f"当前步骤描述: {step['description']}",
                                        f"工具名称: {current_tool_name}",
                                        '请根据以上信息判断，工具的参数配置及对应的执行结果是否严格满足用户原始需求。',
                                    )
                                    validation_instruction = '\n'.join(lines)
                                    self.validation_agent.instruction = (
                                        STEP_VALIDATION_INSTRUCTION
                                        + validation_instruction
                                    )

                                    async for (
                                        validation_event
                                    ) in self.validation_agent.run_async(ctx):
                                        yield validation_event

                                    validation_result = ctx.session.state.get(
                                        'step_validation', {}
                                    )
                                    is_valid = validation_result.get('is_valid', True)
                                    validation_reason = validation_result.get(
                                        'reason', ''
                                    )

                                    # “假成功”结果，计划重试
                                    if (
                                        not is_valid
                                    ) and retry_count < MAX_TOOL_RETRIES:
                                        retry_count += 1
                                        logger.warning(
                                            f'{ctx.session.id} Step {index + 1} validation failed: {validation_reason}'
                                        )

                                        # 向用户显示校验失败信息
                                        for (
                                            step_validation_failed_event
                                        ) in all_text_event(
                                            ctx,
                                            self.name,
                                            separate_card(
                                                f"步骤 {index + 1} 结果校验未通过"
                                            ),
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
                                        update_plan = copy.deepcopy(
                                            ctx.session.state['plan']
                                        )
                                        update_plan['steps'][index][
                                            'status'
                                        ] = PlanStepStatusEnum.PROCESS
                                        update_plan['steps'][index][
                                            'validation_failure_reason'
                                        ] = validation_reason
                                        original_description = step['description']
                                        update_plan['steps'][index][
                                            'description'
                                        ] = f"{original_description}\n\n注意：上次执行因以下原因校验失败，请改进：{validation_reason}"
                                        yield update_state_event(
                                            ctx, state_delta={'plan': update_plan}
                                        )
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
                                current_steps[index]['status']
                                == PlanStepStatusEnum.FAILED
                                and retry_count < MAX_TOOL_RETRIES
                            ):
                                # 下载 results.txt 失败，退出同一工具重试
                                if DOWNLOAD_RESULTS_TXT_FAILED:
                                    break
                                retry_count += 1
                                update_plan = copy.deepcopy(ctx.session.state['plan'])
                                update_plan['steps'][index][
                                    'status'
                                ] = PlanStepStatusEnum.PROCESS
                                if validation_reason:
                                    logger.info(
                                        f'{ctx.session.id} Step {index + 1} failed due to validation, retrying {retry_count}/{MAX_TOOL_RETRIES}. Reason: {validation_reason}'
                                    )
                                    # 在重试时更新步骤描述，包含校验失败的原因
                                    original_description = step['description']
                                    update_plan['steps'][index][
                                        'description'
                                    ] = f"{original_description}\n\n注意：上次执行因以下原因校验失败，请改进：{validation_reason}"
                                else:
                                    logger.info(
                                        f'{ctx.session.id} Step {index + 1} execution failed, retrying {retry_count}/{MAX_TOOL_RETRIES}'
                                    )

                                # 重置状态为 PROCESS 以便重试
                                yield update_state_event(
                                    ctx, state_delta={'plan': update_plan}
                                )
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
                            and current_steps[index]['status']
                            != PlanStepStatusEnum.SUBMITTED
                        ):
                            available_alts = [
                                alt for alt in alternatives if alt not in tried_tools
                            ]
                            if available_alts:
                                # 尝试替换工具
                                next_tool = available_alts[0]
                                tried_tools.append(next_tool)
                                current_tool_name = next_tool
                                logger.info(
                                    f'{ctx.session.id} Switching to alternative tool: {next_tool} for step {index + 1}'
                                )

                                # 更新plan中的tool_name和status
                                update_plan = copy.deepcopy(ctx.session.state['plan'])
                                update_plan['steps'][index]['tool_name'] = next_tool
                                update_plan['steps'][index][
                                    'status'
                                ] = PlanStepStatusEnum.PROCESS
                                original_description = step['description'].split(
                                    '\n\n注意：'
                                )[
                                    0
                                ]  # 移除之前的失败原因
                                update_plan['steps'][index][
                                    'description'
                                ] = original_description
                                yield update_state_event(
                                    ctx, state_delta={'plan': update_plan}
                                )
                            else:
                                logger.warning(
                                    f'{ctx.session.id} No more alternative tools for step {index + 1}'
                                )
                                break  # 退出tool while

                # 最终仍然没有成功，中止计划
                if not tool_attempt_success:
                    break
