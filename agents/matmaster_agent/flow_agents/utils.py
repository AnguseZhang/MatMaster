import logging
import re
from typing import List

from google.adk.agents import InvocationContext

from agents.matmaster_agent.constant import FRONTEND_STATE_KEY
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.state import (
    BIZ,
    MULTI_PLANS,
    PLAN,
    PLAN_CONFIRM,
    UPLOAD_FILE,
)
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_CLASS_MAPPING,
    ALL_AGENT_TOOLS_LIST,
)
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS

from agents.matmaster_agent.flow_agents.tool_name_utils import (
    normalize_tool_name_to_canonical,
)

logger = logging.getLogger(__name__)
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
    canonical = normalize_tool_name_to_canonical(tool_name)
    if canonical is None or canonical not in ALL_TOOLS:
        raise RuntimeError(f"ToolName Error: {tool_name}")
    try:
        target_agent_name = ALL_TOOLS[canonical]['belonging_agent']
    except BaseException:
        raise RuntimeError(f"ToolName Error: {tool_name}")

    for sub_agent in sub_agents:
        if sub_agent.name == target_agent_name:
            return sub_agent


def get_agent_for_tool(tool_name, sub_agents):
    """
    根据 tool_name 获取对应 Agent。若当前在 sub_agents 中则直接返回，
    否则动态构建（用于更换工具时，新工具所属 Agent 可能不在初始 sub_agents 中）。
    支持 RAG/计划中的大写工具名（如 BUILD_BULK_STRUCTURE_BY_TEMPLATE）自动规范为 ALL_TOOLS 键。
    """
    canonical = normalize_tool_name_to_canonical(tool_name)
    if canonical is None or canonical not in ALL_TOOLS:
        raise RuntimeError(f"ToolName Error: {tool_name}")
    agent = get_agent_name(canonical, sub_agents)
    if agent is not None:
        return agent
    try:
        target_agent_name = ALL_TOOLS[canonical]['belonging_agent']
    except BaseException:
        raise RuntimeError(f"ToolName Error: {tool_name}")
    if target_agent_name not in AGENT_CLASS_MAPPING:
        raise RuntimeError(
            f"Agent for tool {tool_name} (belonging_agent={target_agent_name}) "
            'not in AGENT_CLASS_MAPPING'
        )
    return AGENT_CLASS_MAPPING[target_agent_name](MatMasterLlmConfig)


def check_plan(ctx: InvocationContext):
    logger.info(
        f'{ctx.session.id} plan = {ctx.session.state.get(PLAN)} multi_plans = {ctx.session.state.get(MULTI_PLANS)}'
    )
    if not ctx.session.state.get(PLAN):
        if not ctx.session.state.get(MULTI_PLANS):
            return FlowStatusEnum.NO_PLAN
        else:
            return FlowStatusEnum.NEW_PLAN

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

    if failed_step_count:
        return FlowStatusEnum.FAILED
    elif (not plan_step_count and not process_step_count) or failed_step_count:
        return FlowStatusEnum.COMPLETE
    elif plan_step_count == total_steps:
        return FlowStatusEnum.NEW_PLAN
    else:
        return FlowStatusEnum.PROCESS


def should_bypass_confirmation(ctx: InvocationContext) -> bool:
    """Determine whether to skip plan confirmation based on the tools in the plan."""
    plan_steps = ctx.session.state['plan'].get('steps', [])
    tool_count = len(
        plan_steps
    )  # plan steps are `actual_steps` validated by `tool_name` before appended

    # Check if there is exactly one tool in the plan
    if tool_count == 1:
        # Find the first (and only) tool name (normalize for ALL_TOOLS lookup)
        first_tool_name = normalize_tool_name_to_canonical(
            plan_steps[0].get('tool_name', '')
        ) or plan_steps[0].get('tool_name', '')

        # Check if this tool has bypass_confirmation set to True
        if ALL_TOOLS.get(first_tool_name, {}).get('bypass_confirmation') is True:
            return True

    # TODO: Add more logic here for handling multiple tools in the plan
    elif tool_count == 2:
        first_tool_name = (
            normalize_tool_name_to_canonical(plan_steps[0].get('tool_name', ''))
            or plan_steps[0].get('tool_name', '')
        )
        second_tool_name = (
            normalize_tool_name_to_canonical(plan_steps[1].get('tool_name', ''))
            or plan_steps[1].get('tool_name', '')
        )

        if (
            first_tool_name == 'web-search'
            and second_tool_name == 'extract_info_from_webpage'
        ):
            return True

    return False


def find_alternative_tool(current_tool_name: str) -> List[str]:
    """Return alternative tool names for the current tool (maybe empty)."""
    canonical = normalize_tool_name_to_canonical(current_tool_name)
    tool = ALL_TOOLS.get(canonical or current_tool_name)
    if not tool:
        return []
    return tool.get('alternative', [])


def has_self_check(current_tool_name: str) -> bool:
    """Return self check info for the current tool."""
    canonical = normalize_tool_name_to_canonical(current_tool_name)
    tool = ALL_TOOLS.get(canonical or current_tool_name)
    if not tool:
        return False
    return tool.get('self_check', False)


def scenes_contain_query_job_status(ctx: InvocationContext) -> bool:
    """True when current scenes include query_job_status (e.g. 查询任务/查看任务状态)."""
    scenes = ctx.session.state.get('scenes') or []
    query_value = SceneEnum.QUERY_JOB_STATUS.value
    return any(getattr(s, 'value', s) == query_value for s in scenes)


def is_plan_confirmed(ctx: InvocationContext) -> bool:
    # 1) 原有：前端状态里已确认
    biz_state = ctx.session.state.get(FRONTEND_STATE_KEY, {}).get(BIZ, {})
    if biz_state.get(PLAN_CONFIRM, False):
        return True

    # 2) 用户输入匹配“方案 + 数字”（方案和数字间允许空格）
    try:
        text = (ctx.user_content.parts[0].text or '').strip()
    except Exception:
        text = ''
    if re.match(r'^\s*方案\s*\d+\s*$', text):
        return True

    # 3) 查询任务/任务状态场景：仅查任务状态或结果，无需用户点确认，直接视为已确认
    if scenes_contain_query_job_status(ctx):
        return True

    return False
