import logging
from typing import List, Literal, Optional

from google.adk.agents import InvocationContext
from pydantic import BaseModel, create_model

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST, ALL_TOOLS

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
    total_steps = len(plan_json['steps'])
    for step in plan_json['steps']:
        if step['status'] == PlanStepStatusEnum.PLAN:
            plan_step_count += 1
        elif step['status'] == PlanStepStatusEnum.PROCESS:
            process_step_count += 1

    if not plan_step_count and not process_step_count:
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
