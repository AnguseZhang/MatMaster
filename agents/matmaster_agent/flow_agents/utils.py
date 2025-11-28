import logging
from typing import List, Literal, Optional

from google.adk.agents import InvocationContext
from pydantic import BaseModel, create_model

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_tools_list(scenes: list):
    if not scenes:
        return ALL_AGENT_TOOLS_LIST
    else:
        return [
            k
            for k, v in ALL_TOOLS.items()
            if any(scene in v['scene'] for scene in scenes)
        ]


def get_agent_name(tool_name, sub_agents):
    try:
        target_agent_name = ALL_TOOLS[tool_name]['belonging_agent']
    except BaseException:
        raise RuntimeError(f"ToolName Error: {tool_name}")

    for sub_agent in sub_agents:
        if sub_agent.name == target_agent_name:
            return sub_agent


def check_plan(ctx: InvocationContext):
    if not ctx.session.state.get('plan'):
        return FlowStatusEnum.NO_PLAN

    if ctx.session.state['plan']['feasibility'] == 'null':
        return FlowStatusEnum.NO_PLAN

    plan_json = ctx.session.state['plan']
    plan_step_count = 0  # 统计状态为 plan 的 step 个数
    process_step_count = 0
    failed_step_count = 0
    total_steps = len(plan_json['steps'])
    for step in plan_json['steps']:
        if step['status'] == PlanStepStatusEnum.PLAN:
            plan_step_count += 1
        elif step['status'] in [
            PlanStepStatusEnum.PROCESS,
            PlanStepStatusEnum.SUBMITTED,
        ]:
            process_step_count += 1
        elif step['status'] == PlanStepStatusEnum.FAILED:
            failed_step_count += 1

    if (not plan_step_count and not process_step_count) or failed_step_count:
        return FlowStatusEnum.COMPLETE
    elif plan_step_count == total_steps:
        return FlowStatusEnum.NEW_PLAN
    else:
        return FlowStatusEnum.PROCESS


def create_dynamic_plan_schema(available_tools: list):
    # 动态创建 PlanStepSchema
    DynamicPlanStepSchema = create_model(
        'DynamicPlanStepSchema',
        tool_name=(Optional[Literal[tuple(available_tools)]], None),
        description=(str, ...),
        status=(
            Literal[tuple(PlanStepStatusEnum.__members__.values())],
            PlanStepStatusEnum.PLAN.value,
        ),
        __base__=BaseModel,
    )

    # 动态创建 PlanSchema
    DynamicPlanSchema = create_model(
        'DynamicPlanSchema',
        steps=(List[DynamicPlanStepSchema], ...),
        __base__=BaseModel,
    )

    return DynamicPlanSchema


def should_bypass_confirmation(ctx: InvocationContext) -> bool:
    """Determine whether to skip plan confirmation based on the tools in the plan."""
    plan_steps = ctx.session.state['plan'].get('steps', [])
    tool_count = len(
        plan_steps
    )  # plan steps are `actual_steps` validated by `tool_name` before appended

    # Check if there is exactly one tool in the plan
    if tool_count == 1:
        # Find the first (and only) tool name
        first_tool_name = plan_steps[0].get('tool_name', '')

        # Check if this tool has bypass_confirmation set to True
        if ALL_TOOLS.get(first_tool_name, {}).get('bypass_confirmation') is True:
            return True

    # TODO: Add more logic here for handling multiple tools in the plan
    elif tool_count == 2:
        first_tool_name = plan_steps[0].get('tool_name', '')
        second_tool_name = plan_steps[1].get('tool_name', '')

        if (
            first_tool_name == 'web-search'
            and second_tool_name == 'extract_info_from_webpage'
        ):
            return True

    return False


def get_async_tool_steps(ctx: InvocationContext) -> List[dict]:
    """
    获取计划中所有异步工具的步骤

    Args:
        ctx: InvocationContext

    Returns:
        List[dict]: 异步工具步骤列表，每个元素包含 index, step, tool_name
    """
    plan = ctx.session.state.get('plan', {})
    steps = plan.get('steps', [])

    async_steps = []
    for index, step in enumerate(steps):
        tool_name = step.get('tool_name')
        if tool_name and tool_name in ALL_TOOLS:
            # 检查工具是否为异步工具（通过检查工具是否属于异步 agent）
            tool_info = ALL_TOOLS[tool_name]
            belonging_agent = tool_info.get('belonging_agent', '')
            # 如果工具属于异步 agent（如 apex_agent, abacus_agent 等），则认为是异步工具
            # 这里可以根据实际需求调整判断逻辑
            if belonging_agent and 'agent' in belonging_agent:
                async_steps.append(
                    {
                        'index': index,
                        'step': step,
                        'tool_name': tool_name,
                    }
                )

    return async_steps


def analyze_async_task_dependencies(
    ctx: InvocationContext, async_steps: List[dict]
) -> List[List[int]]:
    """
    分析异步任务之间的依赖关系

    Args:
        ctx: InvocationContext
        async_steps: 异步工具步骤列表

    Returns:
        List[List[int]]: 任务分组列表，每个分组内的任务有依赖关系
    """
    # 简单的依赖分析：按照 step_index 顺序分组
    # 可以根据实际需求实现更复杂的依赖分析逻辑
    if not async_steps:
        return []

    # 按 step_index 排序
    sorted_steps = sorted(async_steps, key=lambda x: x['index'])

    # 简单的分组：每个连续的任务为一组
    task_groups = []
    current_group = [sorted_steps[0]['index']]

    for i in range(1, len(sorted_steps)):
        prev_index = sorted_steps[i - 1]['index']
        curr_index = sorted_steps[i]['index']

        # 如果步骤是连续的，放在同一组；否则开始新组
        if curr_index == prev_index + 1:
            current_group.append(curr_index)
        else:
            task_groups.append(current_group)
            current_group = [curr_index]

    if current_group:
        task_groups.append(current_group)

    return task_groups
