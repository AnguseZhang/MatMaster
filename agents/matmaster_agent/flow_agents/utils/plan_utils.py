import logging
from typing import List, Literal, Optional

from google.adk.agents import InvocationContext
from pydantic import BaseModel, create_model

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.flow_agents.utils.step_utils import get_step_status
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.state import UPLOAD_FILE
from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def get_tools_list(ctx: InvocationContext, scenes: list):
    if not scenes:
        return ALL_AGENT_TOOLS_LIST
    else:
        tools_list_by_scene = [
            k
            for k, v in ALL_TOOLS.items()
            if any(scene in v['scene'] for scene in scenes)
        ]
        if not ctx.session.state[UPLOAD_FILE]:
            final_tools_list = [
                t
                for t in tools_list_by_scene
                if SceneEnum.NEED_UPLOAD_FILE not in ALL_TOOLS[t]['scene']
            ]
        else:
            final_tools_list = tools_list_by_scene

        return final_tools_list


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
        step_status = get_step_status(step)
        if step_status == PlanStepStatusEnum.PLAN:
            plan_step_count += 1
        elif step_status == PlanStepStatusEnum.PROCESS:
            process_step_count += 1
        elif step_status == PlanStepStatusEnum.FAILED:
            failed_step_count += 1

    logger.info(
        f'{ctx.session.id} plan_step_count = {plan_step_count}, process_step_count = {process_step_count}, failed_step_count = {failed_step_count}, total_steps = {total_steps}'
    )
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
        feasibility=(str, ...),
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
    step_count = len(plan_steps)

    # Check if there is exactly one tool in the plan
    if step_count == 1:
        # Find the first (and only) tool name
        first_tool_name = plan_steps[0]['tools'][0].get('tool_name', '')

        # Check if this tool has bypass_confirmation set to True
        if ALL_TOOLS[first_tool_name].get('bypass_confirmation'):
            return True

    # TODO: Add more logic here for handling multiple tools in the plan
    elif step_count == 2:
        first_tool_name = plan_steps[0]['tools'][0].get('tool_name', '')
        second_tool_name = plan_steps[1]['tools'][0].get('tool_name', '')

        if (
            first_tool_name == 'web-search'
            and second_tool_name == 'extract_info_from_webpage'
        ):
            return True

    return False
