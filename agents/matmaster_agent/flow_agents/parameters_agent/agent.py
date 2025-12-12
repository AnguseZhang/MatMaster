import asyncio
import copy
import logging
from typing import AsyncGenerator, Dict, List

from google.adk.agents import InvocationContext
from google.adk.events import Event

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferLlmAgent,
)
from agents.matmaster_agent.base_agents.recommend_summary_agent.recommend_params_agent.schema import (
    create_tool_args_schema,
)
from agents.matmaster_agent.base_agents.recommend_summary_agent.tool_call_info_agent.prompt import (
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.base_agents.recommend_summary_agent.tool_call_info_agent.utils import (
    update_tool_call_info_with_function_declarations,
    update_tool_call_info_with_recommend_params,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.flow_agents.execution_agent.agent import (
    MatMasterSupervisorAgent,
)
from agents.matmaster_agent.flow_agents.parameters_agent.schema import (
    AsyncToolParamsSchema,
    DflowParamsCollectionSchema,
)
from agents.matmaster_agent.flow_agents.utils import (
    analyze_async_task_dependencies,
    get_agent_name,
    get_async_tool_steps,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    save_parameters_to_json,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


# 用于保护共享状态的锁
_collect_params_lock = asyncio.Lock()


async def collect_tool_params_parallel(
    ctx: InvocationContext,
    async_steps: List[Dict],
    execution_agent_sub_agents: List,
) -> List[AsyncToolParamsSchema]:
    """
    并行收集所有异步工具的参数

    Args:
        ctx: InvocationContext
        async_steps: 异步工具步骤列表
        execution_agent_sub_agents: execution_agent 的子代理列表

    Returns:
        List[AsyncToolParamsSchema]: 收集到的参数列表
    """

    async def collect_single_tool_params(step_info: Dict) -> AsyncToolParamsSchema:
        """收集单个工具的参数"""
        step_index = step_info['index']
        step = step_info['step']
        tool_name = step_info['tool_name']

        try:
            # 获取对应的 agent
            target_agent = get_agent_name(tool_name, execution_agent_sub_agents)
            agent_name = target_agent.name

            # 检查 agent 是否有 tool_call_info_agent
            if not hasattr(target_agent, 'tool_call_info_agent'):
                logger.warning(
                    f'{ctx.session.id} Agent {agent_name} does not have tool_call_info_agent'
                )
                return AsyncToolParamsSchema(
                    tool_name=tool_name,
                    step_index=step_index,
                    description=step['description'],
                    tool_args={},
                    missing_tool_args=[],
                    agent_name=agent_name,
                )

            # 设置 instruction
            target_agent.tool_call_info_agent.instruction = (
                gen_tool_call_info_instruction(
                    user_prompt=step['description'],
                    agent_prompt=getattr(target_agent, 'instruction', ''),
                    tool_args_recommend_prompt=ALL_TOOLS.get(tool_name, {}).get(
                        'args_setting', ''
                    ),
                )
            )

            # 使用锁保护共享状态
            async with _collect_params_lock:
                # 保存原始的 plan_index 和 tool_call_info
                original_plan_index = ctx.session.state.get('plan_index')
                original_tool_call_info = ctx.session.state.get('tool_call_info')

                # 设置当前步骤的 plan_index
                ctx.session.state['plan_index'] = step_index

                # 清空之前的 tool_call_info（如果存在）
                ctx.session.state['tool_call_info'] = None

                # 收集参数
                tool_call_info = None
                try:
                    # 步骤1: 调用 tool_call_info_agent 获取初始参数
                    async for event in target_agent.tool_call_info_agent.run_async(ctx):
                        # 手动处理 update_state_event，直接更新 state
                        if event.actions and event.actions.state_delta:
                            state_delta = event.actions.state_delta
                            for key, value in state_delta.items():
                                ctx.session.state[key] = value
                                logger.debug(
                                    f'{ctx.session.id} Updated state[{key}] = {value}'
                                )

                    # 获取初始 tool_call_info
                    if ctx.session.state.get('tool_call_info'):
                        tool_call_info = copy.deepcopy(
                            ctx.session.state['tool_call_info']
                        )

                    # 步骤2: 如果有 missing_tool_args，进行参数补全
                    if tool_call_info and tool_call_info.get('missing_tool_args'):
                        # 确保 tool_args 和 missing_tool_args 存在
                        if 'tool_args' not in tool_call_info:
                            tool_call_info['tool_args'] = {}
                        if 'missing_tool_args' not in tool_call_info:
                            tool_call_info['missing_tool_args'] = []

                        # 更新 function_declarations
                        function_declarations = ctx.session.state.get(
                            'function_declarations', []
                        )
                        if function_declarations:
                            tool_call_info, current_function_declaration = (
                                update_tool_call_info_with_function_declarations(
                                    tool_call_info, function_declarations
                                )
                            )
                            ctx.session.state['tool_call_info'] = tool_call_info

                        # 检查是否还有 missing_tool_args（过滤掉 executor, storage）
                        missing_tool_args = [
                            item
                            for item in tool_call_info.get('missing_tool_args', [])
                            if item not in ['executor', 'storage']
                        ]

                        if missing_tool_args:
                            # 调用 recommend_params_agent
                            async for (
                                event
                            ) in target_agent.recommend_params_agent.run_async(ctx):
                                if event.actions and event.actions.state_delta:
                                    state_delta = event.actions.state_delta
                                    for key, value in state_delta.items():
                                        ctx.session.state[key] = value

                            # 调用 recommend_params_schema_agent
                            target_agent.recommend_params_schema_agent.output_schema = (
                                create_tool_args_schema(
                                    missing_tool_args, current_function_declaration
                                )
                            )
                            async for (
                                event
                            ) in target_agent.recommend_params_schema_agent.run_async(
                                ctx
                            ):
                                if event.actions and event.actions.state_delta:
                                    state_delta = event.actions.state_delta
                                    for key, value in state_delta.items():
                                        ctx.session.state[key] = value

                            # 合并补全的参数
                            recommend_params = ctx.session.state.get(
                                'recommend_params', {}
                            )
                            if recommend_params:
                                tool_call_info = (
                                    update_tool_call_info_with_recommend_params(
                                        tool_call_info, recommend_params
                                    )
                                )
                                ctx.session.state['tool_call_info'] = tool_call_info
                                logger.info(
                                    f'{ctx.session.id} Params completed for {tool_name}: '
                                    f'tool_args={tool_call_info.get("tool_args", {})}'
                                )

                except Exception as e:
                    logger.error(
                        f'{ctx.session.id} Error collecting params for {tool_name}: {e}',
                        exc_info=True,
                    )

                # 恢复原始的 plan_index 和 tool_call_info
                if original_plan_index is not None:
                    ctx.session.state['plan_index'] = original_plan_index
                else:
                    ctx.session.state.pop('plan_index', None)

                if original_tool_call_info is not None:
                    ctx.session.state['tool_call_info'] = original_tool_call_info
                else:
                    ctx.session.state.pop('tool_call_info', None)

            # 验证收集到的参数
            if tool_call_info and tool_call_info.get('tool_name') == tool_name:
                tool_args = tool_call_info.get('tool_args', {})
                missing_tool_args = tool_call_info.get('missing_tool_args', [])

                # 如果 tool_args 为空，尝试从 function_declarations 获取默认值
                if not tool_args and ctx.session.state.get('function_declarations'):
                    function_declarations = ctx.session.state['function_declarations']
                    current_function_declaration = [
                        item
                        for item in function_declarations
                        if item.get('name') == tool_name
                    ]
                    if current_function_declaration:
                        params = current_function_declaration[0].get('parameters', {})
                        properties = params.get('properties', {})
                        # 提取有默认值的参数
                        for param_name, param_schema in properties.items():
                            if 'default' in param_schema:
                                tool_args[param_name] = param_schema['default']
                                logger.debug(
                                    f'{ctx.session.id} Added default value for {param_name}: '
                                    f'{param_schema["default"]}'
                                )

                # 修复 build_bulk_structure_by_template 的 crystal_structure 参数大小写问题
                if (
                    tool_name == 'build_bulk_structure_by_template'
                    and 'crystal_structure' in tool_args
                ):
                    crystal_structure = tool_args['crystal_structure']
                    if isinstance(crystal_structure, str):
                        # 转换为小写
                        tool_args['crystal_structure'] = crystal_structure.lower()
                        logger.info(
                            f'{ctx.session.id} Fixed crystal_structure case: '
                            f'{crystal_structure} -> {tool_args["crystal_structure"]}'
                        )

                logger.info(
                    f'{ctx.session.id} Collected params for {tool_name}: '
                    f'tool_args={tool_args}, missing_tool_args={missing_tool_args}'
                )

                return AsyncToolParamsSchema(
                    tool_name=tool_name,
                    step_index=step_index,
                    description=step['description'],
                    tool_args=tool_args,
                    missing_tool_args=missing_tool_args,
                    agent_name=agent_name,
                )
            else:
                logger.warning(
                    f'{ctx.session.id} Failed to collect valid params for {tool_name}, '
                    f'tool_call_info: {tool_call_info}'
                )
        except Exception as e:
            logger.error(
                f'{ctx.session.id} Exception collecting params for {tool_name}: {e}'
            )

        # 如果收集失败，返回基本信息
        try:
            target_agent = get_agent_name(tool_name, execution_agent_sub_agents)
            agent_name = target_agent.name
        except Exception:
            agent_name = 'unknown'

        return AsyncToolParamsSchema(
            tool_name=tool_name,
            step_index=step_index,
            description=step['description'],
            tool_args={},
            missing_tool_args=[],
            agent_name=agent_name,
        )

    # 并行收集所有工具的参数
    tasks = [collect_single_tool_params(step_info) for step_info in async_steps]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理异常
    params_list = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(
                f'{ctx.session.id} Failed to collect params for {async_steps[i]["tool_name"]}: {result}'
            )
            # 返回基本信息
            step_info = async_steps[i]
            params_list.append(
                AsyncToolParamsSchema(
                    tool_name=step_info['tool_name'],
                    step_index=step_info['index'],
                    description=step_info['step']['description'],
                    tool_args={},
                    missing_tool_args=[],
                    agent_name=get_agent_name(
                        step_info['tool_name'], execution_agent_sub_agents
                    ).name,
                )
            )
        else:
            params_list.append(result)

    return params_list


class ParametersAgent(DisallowTransferLlmAgent):
    execution_agent: MatMasterSupervisorAgent

    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        ParametersAgent 的主要执行逻辑

        1. 收集所有异步工具的参数（并行）
        2. 分析依赖关系
        3. 生成包含 nodes 和 edges 的 JSON 文件
        """
        # 获取所有异步工具步骤
        async_steps = get_async_tool_steps(ctx)
        if not async_steps:
            logger.warning(f'{ctx.session.id} No async tools found in plan')
            return

        logger.info(
            f'{ctx.session.id} Found {len(async_steps)} async tools: {[s["tool_name"] for s in async_steps]}'
        )

        # 检查是否已经收集过参数
        parameters_collection = ctx.session.state.get('parameters_collection')
        parameters_confirm = ctx.session.state.get('parameters_confirm', {}).get(
            'flag', False
        )

        if not parameters_collection:
            # 阶段1: 并行收集所有异步工具的参数
            logger.info(
                f'{ctx.session.id} Collecting params for async tools in parallel...'
            )

            params_list = await collect_tool_params_parallel(
                ctx, async_steps, self.execution_agent.sub_agents
            )

            # 分析依赖关系
            task_groups = analyze_async_task_dependencies(ctx, async_steps)

            # 保存收集到的参数
            params_collection = DflowParamsCollectionSchema(
                async_tools=params_list,
                total_count=len(params_list),
            )

            yield update_state_event(
                ctx,
                state_delta={'parameters_collection': params_collection.model_dump()},
            )

            # 展示参数信息（不生成 JSON，等待用户确认）
            params_text = self._format_params_for_display(params_collection)
            params_text += (
                '\n\n⚠️ 请仔细检查上述参数，确认无误后系统将生成参数 JSON 文件。'
            )

            for params_display_event in all_text_event(
                ctx, self.name, params_text, ModelRole
            ):
                yield params_display_event

        # 阶段2: 如果参数已确认，生成 JSON 文件
        if parameters_confirm and not ctx.session.state.get('parameters_json_path'):
            logger.info(
                f'{ctx.session.id} Parameters confirmed, generating JSON file...'
            )

            # 获取已收集的参数
            params_collection = DflowParamsCollectionSchema(
                **ctx.session.state['parameters_collection']
            )

            # 将 params_list 转换为字典列表（包含所有必要信息）
            params_dict_list = []
            for params in params_collection.async_tools:
                params_dict_list.append(
                    {
                        'tool_name': params.tool_name,
                        'step_index': params.step_index,
                        'description': params.description,
                        'tool_args': params.tool_args,
                        'missing_tool_args': params.missing_tool_args,
                        'agent_name': params.agent_name,
                    }
                )

            # 分析依赖关系
            async_steps = get_async_tool_steps(ctx)
            task_groups = analyze_async_task_dependencies(ctx, async_steps)

            # 保存为 JSON 文件
            json_path = save_parameters_to_json(ctx, params_dict_list, task_groups)

            # 保存 JSON 路径到 state
            yield update_state_event(
                ctx,
                state_delta={'parameters_json_path': json_path},
            )

            # 展示 JSON 生成成功信息
            json_success_text = f'\n\n✅ 参数确认完成！参数 JSON 文件已生成：`{json_path}`\n\n该 JSON 文件包含 {len(params_dict_list)} 个节点的参数配置和依赖关系，可用于后续的计算任务执行。'

            for json_success_event in all_text_event(
                ctx, self.name, json_success_text, ModelRole
            ):
                yield json_success_event

    def _format_params_for_display(
        self, params_collection: DflowParamsCollectionSchema
    ) -> str:
        """格式化参数展示文本"""
        lines = [
            '## 异步任务参数汇总\n',
            f'共发现 {params_collection.total_count} 个异步计算任务，请仔细检查每个任务的参数：\n',
        ]

        # 按顺序显示所有任务
        for i, tool_params in enumerate(params_collection.async_tools, 1):
            lines.append('\n---\n')
            lines.append(f'### 任务 {i}: {tool_params.tool_name}')
            lines.append(
                f'**步骤 {tool_params.step_index + 1}**: {tool_params.description}'
            )
            lines.append(f'**所属代理**: {tool_params.agent_name}\n')

            # 显示已收集的参数（包括有默认值的参数）
            if tool_params.tool_args:
                lines.append('**已收集的参数**:')
                for key, value in tool_params.tool_args.items():
                    # 格式化值，如果是长字符串则截断
                    display_value = value
                    if isinstance(value, str) and len(value) > 100:
                        display_value = value[:100] + '...'
                    lines.append(f'  - `{key}`: `{display_value}`')
                lines.append('')
            else:
                # 如果没有收集到参数，但也没有缺失参数，说明所有参数都有默认值
                if not tool_params.missing_tool_args:
                    lines.append(
                        '**已收集的参数**: 所有参数使用默认值（无需用户提供）\n'
                    )
                else:
                    lines.append('**已收集的参数**: 无\n')

            # 显示缺失的参数
            if tool_params.missing_tool_args:
                lines.append(
                    f'**⚠️ 缺失的参数**: `{", ".join(tool_params.missing_tool_args)}`\n'
                )
            else:
                lines.append('**参数完整性**: ✅ 所有必需参数已收集\n')

        return '\n'.join(lines)
