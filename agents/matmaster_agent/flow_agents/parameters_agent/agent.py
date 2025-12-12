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
    串行收集所有异步工具的参数

    注意：虽然函数名是 parallel，但实际是串行执行，因为 tool_call_info 和 function_declarations
    是共享的 state，并行调用会导致相互覆盖

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

        # 根据plan中的步骤顺序，确定前后关系
        plan = ctx.session.state.get('plan', {})
        all_steps = plan.get('steps', [])

        # 确定前后关系
        # 前一个步骤索引
        prev_step_index = None
        if step_index > 0:
            prev_step_index = step_index - 1

        # 后续步骤索引列表
        next_step_indices = []
        if step_index < len(all_steps) - 1:
            # 找到所有后续步骤
            for i in range(step_index + 1, len(all_steps)):
                next_step_indices.append(i)

        # 检查前面是否有结构文件输出任务（不仅检查前一个步骤，还要检查所有前面的步骤）
        depends_on_previous_output = False
        # 获取 function_declarations 用于动态判断（后续也会用到）
        function_declarations = ctx.session.state.get('function_declarations', [])

        if step_index > 0:
            # 从前往后检查所有前面的步骤
            for i in range(step_index - 1, -1, -1):
                prev_step = all_steps[i] if i < len(all_steps) else None
                if prev_step:
                    prev_tool_name = prev_step.get('tool_name')
                    # 动态判断前一个工具是否输出结构文件
                    prev_decl = (
                        next(
                            (
                                d
                                for d in function_declarations
                                if d.get('name') == prev_tool_name
                            ),
                            None,
                        )
                        if function_declarations
                        else None
                    )

                    from agents.matmaster_agent.utils.event_utils import (
                        _is_structure_output_tool,
                    )

                    if _is_structure_output_tool(prev_tool_name, prev_decl):
                        depends_on_previous_output = True
                        logger.info(
                            f'{ctx.session.id} Task {tool_name} (step {step_index}) depends on '
                            f'previous structure output task {prev_tool_name} (step {i}) output'
                        )
                        break

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
                    prev_step_index=prev_step_index,
                    next_step_indices=next_step_indices,
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
                    # 注意：save_tool_call_info_before_remove callback 已经会在 LLM 响应时
                    # 自动保存 function_call 到 state['tool_call_info']，这里不需要手动捕获
                    logger.info(
                        f'{ctx.session.id} Calling tool_call_info_agent for {tool_name}'
                    )
                    event_count = 0
                    async for event in target_agent.tool_call_info_agent.run_async(ctx):
                        event_count += 1
                        # 手动处理 update_state_event，直接更新 state
                        if event.actions and event.actions.state_delta:
                            state_delta = event.actions.state_delta
                            logger.info(
                                f'{ctx.session.id} Received state_delta from tool_call_info_agent: {state_delta}'
                            )
                            for key, value in state_delta.items():
                                ctx.session.state[key] = value
                                logger.info(
                                    f'{ctx.session.id} Updated state[{key}] = {value}'
                                )

                    logger.info(
                        f'{ctx.session.id} tool_call_info_agent finished, event_count={event_count}, '
                        f'tool_call_info in state: {ctx.session.state.get("tool_call_info")}'
                    )

                    # 重要：在调用 tool_call_info_agent 后，function_declarations 应该已经被 default_before_model_callback 更新
                    # 但是，为了确保 function_declarations 被正确保存到 ctx.session.state，我们在这里检查并同步
                    # 注意：callback_context.state 和 ctx.session.state 应该是同一个对象，但为了保险起见，我们显式同步
                    function_declarations_after_call = ctx.session.state.get(
                        'function_declarations', []
                    )
                    logger.info(
                        f'{ctx.session.id} function_declarations after tool_call_info_agent call: '
                        f'count = {len(function_declarations_after_call)}, '
                        f'tool names = {[d.get("name") for d in function_declarations_after_call if isinstance(d, dict)]}'
                    )

                    # 获取初始 tool_call_info（从 state 中获取，由 save_tool_call_info_before_remove 保存）
                    if ctx.session.state.get('tool_call_info'):
                        tool_call_info = copy.deepcopy(
                            ctx.session.state['tool_call_info']
                        )
                        logger.info(
                            f'{ctx.session.id} Got tool_call_info from state: {tool_call_info}'
                        )
                    else:
                        logger.warning(
                            f'{ctx.session.id} No tool_call_info in state after tool_call_info_agent'
                        )
                        tool_call_info = None

                    # 步骤2: 使用 function_declarations 补充参数（包括有默认值的参数）
                    if tool_call_info:
                        # 确保 tool_args 和 missing_tool_args 存在
                        if 'tool_args' not in tool_call_info:
                            tool_call_info['tool_args'] = {}
                        if 'missing_tool_args' not in tool_call_info:
                            tool_call_info['missing_tool_args'] = []

                        # 更新 function_declarations（无论 missing_tool_args 是否为空都要调用，以补充有默认值的参数）
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
                            logger.info(
                                f'{ctx.session.id} Updated tool_call_info with function_declarations: '
                                f'tool_args={tool_call_info.get("tool_args", {})}, '
                                f'missing_tool_args={tool_call_info.get("missing_tool_args", [])}'
                            )

                            # 重要：确保 function_declarations 被显式保存到 ctx.session.state
                            # 虽然 callback_context.state 和 ctx.session.state 应该是同一个对象，
                            # 但为了确保 function_declarations 被正确持久化，我们显式保存
                            ctx.session.state['function_declarations'] = (
                                function_declarations
                            )
                            logger.info(
                                f'{ctx.session.id} Explicitly saved function_declarations to ctx.session.state: '
                                f'count = {len(function_declarations)}, '
                                f'tool names = {[d.get("name") for d in function_declarations if isinstance(d, dict)]}'
                            )
                        else:
                            logger.warning(
                                f'{ctx.session.id} function_declarations is empty for {tool_name} (step {step_index}), '
                                f'cannot update tool_call_info with default values'
                            )

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

                # 如果当前任务依赖前一个任务的输出，移除结构文件参数
                # 让 edges 连接来处理这些参数
                if depends_on_previous_output:
                    # 动态识别结构文件参数：从 function_declarations 中查找
                    # 注意：function_declarations 已在前面获取，这里直接复用
                    current_function_declaration = [
                        item
                        for item in function_declarations
                        if item.get('name') == tool_name
                    ]

                    # 从 function_declarations 中动态识别结构文件参数
                    structure_file_params = []
                    if current_function_declaration:
                        from agents.matmaster_agent.utils.event_utils import (
                            _get_parameter_type,
                            _is_structure_file_parameter,
                        )

                        properties = (
                            current_function_declaration[0]
                            .get('parameters', {})
                            .get('properties', {})
                        )
                        for param_name, param_schema in properties.items():
                            param_type = (
                                _get_parameter_type(param_schema)
                                if isinstance(param_schema, dict)
                                else 'str'
                            )
                            # 使用统一的动态识别方法
                            if _is_structure_file_parameter(
                                param_name, param_schema, param_type
                            ):
                                structure_file_params.append(param_name)

                    # 从 tool_args 中移除结构文件参数（如果存在）
                    removed_params = []
                    for param_name in list(tool_args.keys()):
                        if param_name in structure_file_params:
                            removed_params.append(param_name)
                            del tool_args[param_name]
                            logger.info(
                                f'{ctx.session.id} Removed structure file parameter {param_name} '
                                f'from {tool_name} (step {step_index}) as it depends on previous task output'
                            )

                    # 如果参数被移除，确保它在 missing_tool_args 中（或者不添加，让 edges 处理）
                    # 这里我们不添加到 missing_tool_args，因为 edges 会通过连接来提供值
                    if removed_params:
                        logger.info(
                            f'{ctx.session.id} Structure file parameters {removed_params} will be '
                            f'provided via edges connection for {tool_name}'
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
                    prev_step_index=prev_step_index,
                    next_step_indices=next_step_indices,
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

        # 确保包含前后关系信息
        return AsyncToolParamsSchema(
            tool_name=tool_name,
            step_index=step_index,
            description=step['description'],
            tool_args={},
            missing_tool_args=[],
            agent_name=agent_name,
            prev_step_index=prev_step_index,
            next_step_indices=next_step_indices,
        )

    # 串行收集所有工具的参数（避免共享 state 相互覆盖）
    # 并行调用会导致相互覆盖，导致参数收集失败
    params_list = []
    # 收集所有工具的 function_declarations（用于后续生成 JSON）
    all_function_declarations = []
    function_declarations_dict = {}  # 用于去重

    for step_info in async_steps:
        try:
            result = await collect_single_tool_params(step_info)
            params_list.append(result)

            # 收集当前工具的 function_declarations
            # 从 state 中获取（在 collect_single_tool_params 中已经保存）
            current_function_declarations = ctx.session.state.get(
                'function_declarations', []
            )
            for decl in current_function_declarations:
                if isinstance(decl, dict) and decl.get('name'):
                    tool_name = decl.get('name')
                    # 只保存 plan 中需要的工具的 function_declarations
                    if tool_name in [s['tool_name'] for s in async_steps]:
                        if tool_name not in function_declarations_dict:
                            function_declarations_dict[tool_name] = decl
                            all_function_declarations.append(decl)
        except Exception as e:
            logger.error(
                f'{ctx.session.id} Failed to collect params for {step_info["tool_name"]}: {e}',
                exc_info=True,
            )
            # 返回基本信息
            # 获取plan信息以确定前后关系
            plan = ctx.session.state.get('plan', {})
            all_steps = plan.get('steps', [])
            step_index = step_info['index']
            prev_step_index = step_index - 1 if step_index > 0 else None
            next_step_indices = (
                list(range(step_index + 1, len(all_steps)))
                if step_index < len(all_steps) - 1
                else []
            )

            params_list.append(
                AsyncToolParamsSchema(
                    tool_name=step_info['tool_name'],
                    step_index=step_index,
                    description=step_info['step']['description'],
                    tool_args={},
                    missing_tool_args=[],
                    agent_name=get_agent_name(
                        step_info['tool_name'], execution_agent_sub_agents
                    ).name,
                    prev_step_index=prev_step_index,
                    next_step_indices=next_step_indices,
                )
            )

    # 如果 all_function_declarations 为空，尝试从最后一次 state 中获取
    if not all_function_declarations:
        final_function_declarations = ctx.session.state.get('function_declarations', [])
        for decl in final_function_declarations:
            if isinstance(decl, dict) and decl.get('name'):
                tool_name = decl.get('name')
                if tool_name in [s['tool_name'] for s in async_steps]:
                    if tool_name not in function_declarations_dict:
                        function_declarations_dict[tool_name] = decl
                        all_function_declarations.append(decl)

    logger.info(
        f'{ctx.session.id} Collected {len(all_function_declarations)} function_declarations in collect_tool_params_parallel: '
        f'{[d.get("name") for d in all_function_declarations if isinstance(d, dict)]}'
    )

    # 将 function_declarations 保存到 state（用于后续使用）
    if all_function_declarations:
        ctx.session.state['function_declarations'] = all_function_declarations

    return params_list, all_function_declarations


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

        # 检查 function_declarations 是否已收集
        function_declarations = ctx.session.state.get('function_declarations', [])
        logger.info(
            f'{ctx.session.id} Current function_declarations count: {len(function_declarations)}, '
            f'tool names: {[d.get("name") for d in function_declarations if isinstance(d, dict)]}'
        )

        if not parameters_collection:
            # 阶段1: 串行收集所有异步工具的参数（避免共享 state 相互覆盖）
            logger.info(
                f'{ctx.session.id} Collecting params for async tools sequentially...'
            )

            params_list, collected_function_declarations = (
                await collect_tool_params_parallel(
                    ctx, async_steps, self.execution_agent.sub_agents
                )
            )

            # 分析依赖关系
            task_groups = analyze_async_task_dependencies(ctx, async_steps)

            # 保存收集到的参数（包括 function_declarations）
            params_collection = DflowParamsCollectionSchema(
                async_tools=params_list,
                total_count=len(params_list),
                function_declarations=collected_function_declarations,
            )

            logger.info(
                f'{ctx.session.id} Saved {len(collected_function_declarations)} function_declarations to parameters_collection'
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

            # 重置 parameters_confirm，确保用户需要重新确认参数（而不是使用之前确认plan的回复）
            if ctx.session.state.get('parameters_confirm', {}).get('flag', False):
                yield update_state_event(
                    ctx,
                    state_delta={
                        'parameters_confirm': {
                            'flag': False,
                            'reason': 'New parameters displayed, waiting for user confirmation',
                        }
                    },
                )

        # 阶段2: 如果参数已确认，生成 JSON 文件
        if parameters_confirm and not ctx.session.state.get('parameters_json_path'):
            logger.info(
                f'{ctx.session.id} Parameters confirmed, generating JSON file...'
            )

            # 获取已收集的参数
            params_collection = DflowParamsCollectionSchema(
                **ctx.session.state['parameters_collection']
            )

            # 将 params_list 转换为字典列表（包含所有必要信息，包括前后关系）
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
                        'prev_step_index': params.prev_step_index,
                        'next_step_indices': params.next_step_indices,
                    }
                )

            # 分析依赖关系
            async_steps = get_async_tool_steps(ctx)
            task_groups = analyze_async_task_dependencies(ctx, async_steps)

            # 确保 function_declarations 已收集
            # 优先从 parameters_collection 中获取（最可靠）
            function_declarations = []
            if (
                hasattr(params_collection, 'function_declarations')
                and params_collection.function_declarations
            ):
                function_declarations = params_collection.function_declarations
                logger.info(
                    f'{ctx.session.id} Using function_declarations from parameters_collection: '
                    f'count = {len(function_declarations)}'
                )

            # 如果 parameters_collection 中没有，从 state 中获取
            if not function_declarations:
                function_declarations = ctx.session.state.get(
                    'function_declarations', []
                )
                if function_declarations:
                    logger.info(
                        f'{ctx.session.id} Using function_declarations from state: '
                        f'count = {len(function_declarations)}'
                    )

            if function_declarations:
                # 确保 function_declarations 被保存到 state（用于 save_parameters_to_json）
                ctx.session.state['function_declarations'] = function_declarations
                logger.info(
                    f'{ctx.session.id} function_declarations ready for save_parameters_to_json: '
                    f'count = {len(function_declarations)}, '
                    f'tool names = {[d.get("name") for d in function_declarations if isinstance(d, dict)]}'
                )
            else:
                logger.error(
                    f'{ctx.session.id} function_declarations is still empty. '
                    f'This will cause issues in save_parameters_to_json (missing stru_file parameters, empty edges). '
                    f'Tool names in plan: {[params["tool_name"] for params in params_dict_list]}'
                )

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
