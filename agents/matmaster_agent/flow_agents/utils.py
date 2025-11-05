import asyncio
import logging

from google.adk.agents import InvocationContext
from mcp import ClientSession
from mcp.client.sse import sse_client

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.flow_agents.model import FlowStatusEnum, PlanStepStatusEnum
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_CLASS_MAPPING,
    ALL_AGENT_TOOLS_DICT,
    ALL_TOOLSET_DICT,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_agent_class_and_name(tool_name):
    target_agent_name = ''
    for key, value in ALL_AGENT_TOOLS_DICT.items():
        if tool_name in value:
            target_agent_name = key
            break

    if not target_agent_name:
        raise RuntimeError(f"ToolName Error: {tool_name}")

    return target_agent_name, AGENT_CLASS_MAPPING[f'{target_agent_name}']


def check_plan(ctx: InvocationContext):
    if not ctx.session.state.get('plan'):
        return FlowStatusEnum.NO_PLAN

    plan_json = ctx.session.state['plan']
    for step in plan_json['steps']:
        if step['status'] != PlanStepStatusEnum.PLAN:
            return FlowStatusEnum.PROCESS

    return FlowStatusEnum.NEW_PLAN


def get_health_toolset():
    """同步版本的 get_health_toolset"""

    async def _async_get_health_toolset():
        health_results = []  # 存储结果，每个元素是 (variable_name, toolset) 元组

        for name, toolset in ALL_TOOLSET_DICT.items():
            server_url = toolset._connection_params.url
            try:
                async with sse_client(server_url) as (read, write):
                    async with ClientSession(read, write) as session:
                        # 初始化
                        await session.initialize()
                        # 调用 tools/list 方法（对应 get_tools）
                        await session.list_tools()

                health_results.append(toolset)
            except BaseException:
                logger.error(
                    f'[{MATMASTER_AGENT_NAME}] Error Connect: name = {name}, server_url = {server_url}'
                )
                continue

        return health_results

    # 运行异步函数并返回结果
    return asyncio.run(_async_get_health_toolset())
