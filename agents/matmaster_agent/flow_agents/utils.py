import logging

from google.adk.agents import InvocationContext

from agents.matmaster_agent.flow_agents.model import FlowStatusEnum, PlanStepStatusEnum
from agents.matmaster_agent.sub_agents.mapping import (
    ALL_AGENT_TOOLS_DICT,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_agent_name(tool_name, sub_agents):
    target_agent_name = ''
    for key, value in ALL_AGENT_TOOLS_DICT.items():
        if tool_name in value:
            target_agent_name = key
            break

    if not target_agent_name:
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
