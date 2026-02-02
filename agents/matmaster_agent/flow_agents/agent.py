import copy
import json
import logging
from asyncio import CancelledError
from typing import AsyncGenerator

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from opik.integrations.adk import track_adk_agent_recursive
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_callbacks.private_callback import (
    remove_function_call,
)
from agents.matmaster_agent.constant import (
    CURRENT_ENV,
    FRONTEND_STATE_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.core_agents.base_agents.error_agent import (
    ErrorHandleBaseAgent,
)
from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.core_agents.public_agents.job_agents.agent import (
    BaseAsyncJobAgent,
)
from agents.matmaster_agent.flow_agents.analysis_agent.prompt import (
    get_analysis_instruction,
)
from agents.matmaster_agent.flow_agents.chat_agent.prompt import (
    ChatAgentDescription,
    ChatAgentGlobalInstruction,
    ChatAgentInstruction,
)
from agents.matmaster_agent.flow_agents.constant import (
    MATMASTER_FLOW,
    MATMASTER_FLOW_PLANS,
    MATMASTER_GENERATE_NPS,
)
from agents.matmaster_agent.flow_agents.execution_agent.agent import (
    MatMasterSupervisorAgent,
)
from agents.matmaster_agent.flow_agents.expand_agent.agent import ExpandAgent
from agents.matmaster_agent.flow_agents.expand_agent.constant import EXPAND_AGENT
from agents.matmaster_agent.flow_agents.expand_agent.prompt import EXPAND_INSTRUCTION
from agents.matmaster_agent.flow_agents.expand_agent.schema import ExpandSchema
from agents.matmaster_agent.flow_agents.handle_upload_agent.agent import (
    HandleUploadAgent,
)
from agents.matmaster_agent.flow_agents.intent_agent.constant import INTENT_AGENT
from agents.matmaster_agent.flow_agents.intent_agent.model import IntentEnum
from agents.matmaster_agent.flow_agents.intent_agent.prompt import INTENT_INSTRUCTION
from agents.matmaster_agent.flow_agents.intent_agent.schema import IntentSchema
from agents.matmaster_agent.flow_agents.plan_make_agent.agent import PlanMakeAgent
from agents.matmaster_agent.flow_agents.plan_make_agent.callback import (
    filter_plan_make_llm_contents,
)
from agents.matmaster_agent.flow_agents.plan_make_agent.constant import PLAN_MAKE_AGENT
from agents.matmaster_agent.flow_agents.plan_make_agent.prompt import (
    get_plan_make_instruction,
)
from agents.matmaster_agent.flow_agents.plan_make_agent.schema import (
    create_dynamic_multi_plans_schema,
)
from agents.matmaster_agent.flow_agents.report_agent.prompt import (
    get_report_instruction,
)
from agents.matmaster_agent.flow_agents.scene_agent.constant import SCENE_AGENT
from agents.matmaster_agent.flow_agents.scene_agent.prompt import SCENE_INSTRUCTION
from agents.matmaster_agent.flow_agents.scene_agent.schema import SceneSchema
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum
from agents.matmaster_agent.flow_agents.step_title_agent.callback import (
    filter_llm_contents,
)
from agents.matmaster_agent.flow_agents.step_title_agent.prompt import (
    STEP_TITLE_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.step_title_agent.schema import StepTitleSchema
from agents.matmaster_agent.flow_agents.step_validation_agent.prompt import (
    STEP_VALIDATION_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.step_validation_agent.schema import (
    StepValidationSchema,
)
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    get_tools_list,
    is_plan_confirmed,
    should_bypass_confirmation,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.memory.agent import MemoryWriterAgent
from agents.matmaster_agent.memory.kernel import get_memory_kernel
from agents.matmaster_agent.memory.prompt import (
    LONG_CONTEXT_THRESHOLD,
    get_memory_writer_instruction,
)
from agents.matmaster_agent.memory.reader import format_short_term_memory
from agents.matmaster_agent.prompt import (
    GLOBAL_INSTRUCTION,
    HUMAN_FRIENDLY_FORMAT_REQUIREMENT,
)
from agents.matmaster_agent.services.icl import (
    expand_input_examples,
    scene_tags_from_examples,
    select_examples,
    select_update_examples,
    toolchain_from_examples,
)
from agents.matmaster_agent.services.questions import get_random_questions
from agents.matmaster_agent.state import (
    BIZ,
    EXPAND,
    MULTI_PLANS,
    PLAN,
    UPLOAD_FILE,
)
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_CLASS_MAPPING,
    ALL_AGENT_TOOLS_LIST,
)
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    is_text,
    send_error_event,
    update_state_event,
)
from agents.matmaster_agent.utils.io_oss import (
    ReportUploadParams,
    upload_report_md_to_oss,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class MatMasterFlowAgent(LlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self._chat_agent = DisallowTransferAndContentLimitLlmAgent(
            name='chat_agent',
            model=MatMasterLlmConfig.deepseek_chat,
            description=ChatAgentDescription,
            instruction=ChatAgentInstruction,
            global_instruction=ChatAgentGlobalInstruction,
            after_model_callback=remove_function_call,
        )

        self._handle_upload_agent = HandleUploadAgent(
            name='handle_upload_agent',
        )

        self._intent_agent = DisallowTransferAndContentLimitSchemaAgent(
            name=INTENT_AGENT,
            model=MatMasterLlmConfig.tool_schema_model,
            description='识别用户的意图',
            instruction=INTENT_INSTRUCTION,
            output_schema=IntentSchema,
            state_key='intent',
        )

        self._expand_agent = ExpandAgent(
            name=EXPAND_AGENT,
            model=MatMasterLlmConfig.tool_schema_model,
            description='扩写用户的问题',
            instruction=EXPAND_INSTRUCTION,
            output_schema=ExpandSchema,
            state_key=EXPAND,
        )

        self._scene_agent = DisallowTransferAndContentLimitSchemaAgent(
            name=SCENE_AGENT,
            model=MatMasterLlmConfig.tool_schema_model,
            description='把用户的问题划分到特定的场景',
            instruction=SCENE_INSTRUCTION,
            output_schema=SceneSchema,
            state_key='single_scenes',
        )

        self._plan_make_agent = PlanMakeAgent(
            name=PLAN_MAKE_AGENT,
            model=MatMasterLlmConfig.tool_schema_model,
            description='根据用户的问题依据现有工具执行计划，如果没有工具可用，告知用户，不要自己制造工具或幻想',
            state_key=MULTI_PLANS,
            global_instruction=GLOBAL_INSTRUCTION,
            before_model_callback=filter_plan_make_llm_contents,
        )

        self._memory_writer_agent = MemoryWriterAgent(MatMasterLlmConfig)

        self._execution_agent = None

        self._analysis_agent = DisallowTransferAndContentLimitLlmAgent(
            name='execution_summary_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction='使用 {target_language} 回答',
            description=f'总结本轮的计划执行情况\n格式要求: \n{HUMAN_FRIENDLY_FORMAT_REQUIREMENT}',
            instruction='',
        )

        self._report_agent = DisallowTransferAndContentLimitLlmAgent(
            name='report_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction=ChatAgentGlobalInstruction,
            description='根据完整的上下文，生成markdown总结文档',
            instruction='',
        )

        self.sub_agents = [
            self.chat_agent,
            self.handle_upload_agent,
            self.intent_agent,
            self.expand_agent,
            self.scene_agent,
            self.plan_make_agent,
            self.analysis_agent,
            self.report_agent,
        ]

        return self

    @computed_field
    @property
    def chat_agent(self) -> LlmAgent:
        return self._chat_agent

    @computed_field
    @property
    def handle_upload_agent(self) -> ErrorHandleBaseAgent:
        return self._handle_upload_agent

    @computed_field
    @property
    def intent_agent(self) -> LlmAgent:
        return self._intent_agent

    @computed_field
    @property
    def expand_agent(self) -> LlmAgent:
        return self._expand_agent

    @computed_field
    @property
    def scene_agent(self) -> LlmAgent:
        return self._scene_agent

    @computed_field
    @property
    def plan_make_agent(self) -> LlmAgent:
        return self._plan_make_agent

    @computed_field
    @property
    def memory_writer_agent(self) -> LlmAgent:
        return self._memory_writer_agent

    @computed_field
    @property
    def execution_agent(self) -> LlmAgent:
        return self._execution_agent

    @computed_field
    @property
    def analysis_agent(self) -> LlmAgent:
        return self._analysis_agent

    @computed_field
    @property
    def report_agent(self) -> LlmAgent:
        return self._report_agent

    def _build_execution_agent_for_plan(
        self, ctx: InvocationContext
    ) -> MatMasterSupervisorAgent:
        step_validation_agent = DisallowTransferAndContentLimitSchemaAgent(
            name='step_validation_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='校验步骤执行结果是否合理',
            instruction=STEP_VALIDATION_INSTRUCTION,
            output_schema=StepValidationSchema,
            state_key='step_validation',
            after_model_callback=MatMasterLlmConfig.opik_tracer.after_model_callback,
        )
        step_title_agent = DisallowTransferAndContentLimitSchemaAgent(
            name='step_title_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            global_instruction=GLOBAL_INSTRUCTION,
            description='给出每一步的标题',
            instruction=STEP_TITLE_INSTRUCTION,
            output_schema=StepTitleSchema,
            state_key='step_title',
            before_model_callback=filter_llm_contents,
            after_model_callback=MatMasterLlmConfig.opik_tracer.after_model_callback,
        )
        plan_steps = ctx.session.state.get('plan', {}).get('steps', [])
        agent_names = []
        for step in plan_steps:
            tool_name = step.get('tool_name')
            if not tool_name:
                continue
            belonging_agent = ALL_TOOLS.get(tool_name, {}).get('belonging_agent')
            if belonging_agent and belonging_agent not in agent_names:
                agent_names.append(belonging_agent)

        sub_agents = [
            AGENT_CLASS_MAPPING[agent_name](MatMasterLlmConfig)
            for agent_name in agent_names
            if agent_name in AGENT_CLASS_MAPPING
        ]

        execution_agent = MatMasterSupervisorAgent(
            name='execution_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='根据 materials_plan 返回的计划进行总结',
            instruction='',
            sub_agents=sub_agents + [step_title_agent] + [step_validation_agent],
        )
        track_adk_agent_recursive(execution_agent, MatMasterLlmConfig.opik_tracer)
        return execution_agent

    async def _run_expand_agent(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 1. 检索 ICL 示例
        icl_examples = select_examples(
            ctx.user_content.parts[0].text,
            ctx.session.id,
            CURRENT_ENV,
            logger,
        )
        EXPAND_INPUT_EXAMPLES_PROMPT = expand_input_examples(icl_examples)
        logger.info(f'{ctx.session.id} {EXPAND_INPUT_EXAMPLES_PROMPT}')
        # 2. 动态构造 instruction
        self.expand_agent.instruction = (
            EXPAND_INSTRUCTION + EXPAND_INPUT_EXAMPLES_PROMPT
        )
        # 3. 运行 Agent
        async for expand_event in self.expand_agent.run_async(ctx):
            yield expand_event

    async def _build_icl_prompt(self, ctx: InvocationContext):
        UPDATE_USER_CONTENT = (
            '\nUSER INPUT FOR THIS TASK:\n'
            + ctx.session.state['expand']['update_user_content']
        )
        icl_update_examples = select_update_examples(
            ctx.session.state['expand']['update_user_content'],
            ctx.session.id,
            CURRENT_ENV,
            logger,
        )
        SCENE_EXAMPLES_PROMPT = scene_tags_from_examples(icl_update_examples)
        TOOLCHAIN_EXAMPLES_PROMPT = toolchain_from_examples(icl_update_examples)
        logger.info(f'{ctx.session.id} {SCENE_EXAMPLES_PROMPT}')
        logger.info(f'{ctx.session.id} {TOOLCHAIN_EXAMPLES_PROMPT}')

        return UPDATE_USER_CONTENT, SCENE_EXAMPLES_PROMPT, TOOLCHAIN_EXAMPLES_PROMPT

    async def _run_scene_agent(
        self, ctx: InvocationContext, UPDATE_USER_CONTENT, SCENE_EXAMPLES_PROMPT
    ) -> AsyncGenerator[Event, None]:
        # 2. 动态构造 instruction
        self.scene_agent.instruction = (
            SCENE_INSTRUCTION + UPDATE_USER_CONTENT + SCENE_EXAMPLES_PROMPT
        )
        # 3. 运行 Agent
        async for scene_event in self.scene_agent.run_async(ctx):
            yield scene_event

        # 4. 将之前的场景带到后面的会话中去
        before_scenes = ctx.session.state['scenes']
        single_scene = ctx.session.state['single_scenes']['type']
        scenes = list(set(before_scenes + single_scene + ['universal']))
        logger.info(f'{ctx.session.id} scenes = {scenes}')
        yield update_state_event(ctx, state_delta={'scenes': copy.deepcopy(scenes)})

    async def _run_plan_make_agent(
        self, ctx: InvocationContext, UPDATE_USER_CONTENT, TOOLCHAIN_EXAMPLES_PROMPT
    ) -> AsyncGenerator[Event, None]:
        # 制定计划
        if check_plan(ctx) == FlowStatusEnum.FAILED:
            plan_title = i18n.t('RePlanMake')
        else:
            plan_title = i18n.t('PlanMake')

        scenes = ctx.session.state['scenes']
        available_tools = get_tools_list(ctx, scenes)
        if not available_tools:
            available_tools = ALL_AGENT_TOOLS_LIST
        available_tools_with_info = {
            item: {
                'scene': ALL_TOOLS[item]['scene'],
                'description': ALL_TOOLS[item]['description'],
            }
            for item in available_tools
        }
        available_tools_with_info_str = '\n'.join(
            [
                f"{key}\n    scene: {', '.join(value['scene'])}\n    description: {value['description']}"
                for key, value in available_tools_with_info.items()
            ]
        )
        query_for_memory = ctx.session.state.get('expand', {}).get(
            'update_user_content', ''
        ) or (
            ctx.user_content.parts[0].text
            if ctx.user_content and ctx.user_content.parts
            else ''
        )
        short_term_memory_block = format_short_term_memory(
            query_text=query_for_memory,
            session_id=ctx.session.id,
        )
        self.plan_make_agent.instruction = get_plan_make_instruction(
            available_tools_with_info_str
            + UPDATE_USER_CONTENT
            + TOOLCHAIN_EXAMPLES_PROMPT,
            short_term_memory=short_term_memory_block,
        )
        self.plan_make_agent.output_schema = create_dynamic_multi_plans_schema(
            available_tools
        )
        async for plan_event in self.plan_make_agent.run_async(ctx):
            yield plan_event

        # 记忆写入：用 memory_writer_agent 从当前请求和计划提炼 insights，写入 kernel（不向用户展示）
        plan_info = ctx.session.state.get(MULTI_PLANS) or {}
        intro = plan_info.get('intro', '')
        plans = plan_info.get('plans', [])
        plan_intro = intro
        if plans:
            first = plans[0]
            desc = first.get('plan_description', '')
            steps_brief = '; '.join(
                s.get('step_description', '')[:60] for s in first.get('steps', [])[:5]
            )
            plan_intro = f"{intro}\n\n方案摘要: {desc}\n步骤: {steps_brief}"
        is_long_context = len(UPDATE_USER_CONTENT) >= LONG_CONTEXT_THRESHOLD
        self.memory_writer_agent.instruction = get_memory_writer_instruction(
            UPDATE_USER_CONTENT, plan_intro, is_long_context=is_long_context
        )
        async for _ in self.memory_writer_agent.run_async(ctx):
            pass
        output = ctx.session.state.get('memory_writer_output') or {}
        insights = output.get('insights', []) if isinstance(output, dict) else []
        if insights:
            kernel = get_memory_kernel()
            session_id = ctx.session.id
            written = 0
            for text in insights:
                if isinstance(text, str) and text.strip():
                    kernel.write(text=text.strip(), metadata={}, session_id=session_id)
                    written += 1
            logger.info(
                '%s memory_writer wrote %d insight(s) to kernel',
                ctx.session.id,
                written,
            )
        else:
            logger.debug('%s memory_writer output 0 insights', ctx.session.id)

        # 总结计划
        yield update_state_event(
            ctx,
            state_delta={
                'matmaster_flow_active': {
                    'title': plan_title,
                    'font_color': '#30B37F',
                    'bg_color': '#EFF8F5',
                    'border_color': '#B2E0CE',
                }
            },
        )
        for matmaster_flow_event in context_function_event(
            ctx,
            self.name,
            MATMASTER_FLOW,
            None,
            ModelRole,
            {
                'title': plan_title,
                'status': 'start',
                'font_color': '#30B37F',
                'bg_color': '#EFF8F5',
                'border_color': '#B2E0CE',
            },
        ):
            yield matmaster_flow_event

        plan_make_count = len(ctx.session.state[MULTI_PLANS]['plans'])
        plan_info = ctx.session.state[MULTI_PLANS]
        intro = plan_info['intro']
        plans = plan_info['plans']
        overall = plan_info['overall']

        for matmaster_flow_plans_event in context_function_event(
            ctx,
            self.name,
            MATMASTER_FLOW_PLANS,
            None,
            ModelRole,
            {
                'plans_result': json.dumps(
                    {
                        'invocation_id': ctx.invocation_id,
                        'intro': intro,
                        'plans': plans,
                        'overall': overall,
                    }
                )
            },
        ):
            yield matmaster_flow_plans_event

        for matmaster_flow_event in context_function_event(
            ctx,
            self.name,
            MATMASTER_FLOW,
            None,
            ModelRole,
            {
                'title': plan_title,
                'status': 'end',
                'font_color': '#30B37F',
                'bg_color': '#EFF8F5',
                'border_color': '#B2E0CE',
            },
        ):
            yield matmaster_flow_event
        yield update_state_event(ctx, state_delta={'matmaster_flow_active': None})

        # 更新计划为可执行的计划
        update_multi_plans = copy.deepcopy(ctx.session.state[MULTI_PLANS])
        for update_plan in update_multi_plans['plans']:
            origin_steps = update_plan['steps']
            actual_steps = []
            for step in origin_steps:
                if step.get('tool_name'):
                    actual_steps.append(step)
                else:
                    break
            update_plan['steps'] = actual_steps
        yield update_state_event(ctx, state_delta={'multi_plans': update_multi_plans})

        # 检查是否应该跳过用户确认步骤
        if plan_make_count == 1 and should_bypass_confirmation(ctx):
            # 自动设置计划确认状态
            yield update_state_event(
                ctx,
                state_delta={
                    'plan_confirm': {
                        'flag': True,
                        'selected_plan_id': 0,
                        'reason': 'Auto confirmed for single bypass tool',
                    }
                },
            )

    async def _run_plan_execute_and_summary_agent(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 重置 scenes
        yield update_state_event(ctx, state_delta={'scenes': []})
        # 执行计划
        if ctx.session.state['plan']['feasibility'] in ['full', 'part']:
            self._execution_agent = self._build_execution_agent_for_plan(ctx)
            if self._execution_agent:
                # 使用 name 属性来检查，避免 Pydantic __eq__ 的循环引用问题
                if not any(
                    agent.name == self._execution_agent.name
                    for agent in self.sub_agents
                ):
                    self.sub_agents.append(self._execution_agent)
                async for execution_event in self._execution_agent.run_async(ctx):
                    yield execution_event

        # 全部执行完毕，总结执行情况
        if (
            check_plan(ctx) in [FlowStatusEnum.COMPLETE, FlowStatusEnum.FAILED]
            or ctx.session.state['plan']['feasibility'] == 'null'
        ):
            # Skip summary for single-tool plans
            plan_steps = ctx.session.state['plan'].get('steps', [])
            tool_count = sum(1 for step in plan_steps if step.get('tool_name'))

            is_async_agent = issubclass(
                AGENT_CLASS_MAPPING[
                    ALL_TOOLS[plan_steps[0]['tool_name']]['belonging_agent']
                ],
                BaseAsyncJobAgent,
            )
            logger.info(f'is_async_agent = {is_async_agent}, tool_count = {tool_count}')

            # 渲染总结
            if tool_count > 1 or is_async_agent:
                yield update_state_event(
                    ctx,
                    state_delta={
                        'matmaster_flow_active': {
                            'title': i18n.t('PlanSummary'),
                            'font_color': '#9479F7',
                            'bg_color': '#F5F3FF',
                            'border_color': '#CFC3FC',
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
                        'title': i18n.t('PlanSummary'),
                        'status': 'start',
                        'font_color': '#9479F7',
                        'bg_color': '#F5F3FF',
                        'border_color': '#CFC3FC',
                    },
                ):
                    yield matmaster_flow_event
                self._analysis_agent.instruction = get_analysis_instruction(
                    ctx.session.state['plan']
                )
                async for analysis_event in self.analysis_agent.run_async(ctx):
                    yield analysis_event
                self._report_agent.instruction = get_report_instruction(
                    ctx.session.state.get('plan', {})
                )

                # Collect report Markdown
                report_markdown = ''
                async for report_event in self.report_agent.run_async(ctx):
                    if (cur_text := is_text(report_event)) and not report_event.partial:
                        report_markdown += cur_text

                # matmaster_report_md.md
                upload_result = await upload_report_md_to_oss(
                    ReportUploadParams(
                        report_markdown=report_markdown,
                        session_id=ctx.session.id,
                        invocation_id=ctx.invocation_id,
                    )
                )
                if upload_result:
                    for report_file_event in context_function_event(
                        ctx,
                        self.name,
                        'matmaster_report_md',
                        None,
                        ModelRole,
                        {
                            'url': upload_result.oss_url,
                        },
                    ):
                        yield report_file_event
                for matmaster_flow_event in context_function_event(
                    ctx,
                    self.name,
                    'matmaster_flow',
                    None,
                    ModelRole,
                    {
                        'title': i18n.t('PlanSummary'),
                        'status': 'end',
                        'font_color': '#9479F7',
                        'bg_color': '#F5F3FF',
                        'border_color': '#CFC3FC',
                    },
                ):
                    yield matmaster_flow_event
                yield update_state_event(
                    ctx, state_delta={'matmaster_flow_active': None}
                )

            # 渲染追问组件
            follow_up_list = await get_random_questions(i18n=i18n)
            for generate_follow_up_event in context_function_event(
                ctx,
                self.name,
                'matmaster_generate_follow_up',
                {},
                ModelRole,
                {
                    'follow_up_result': json.dumps(
                        {
                            'invocation_id': ctx.invocation_id,
                            'title': i18n.t('MoreQuestions'),
                            'list': follow_up_list,
                        }
                    )
                },
            ):
                yield generate_follow_up_event

    async def _run_research_flow(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 扩写用户问题
        async for _expand_event in self._run_expand_agent(ctx):
            yield _expand_event

        # 构造 UPDATE_USER_CONTENT, SCENE_EXAMPLES_PROMPT, TOOLCHAIN_EXAMPLES_PROMPT
        UPDATE_USER_CONTENT, SCENE_EXAMPLES_PROMPT, TOOLCHAIN_EXAMPLES_PROMPT = (
            await self._build_icl_prompt(ctx)
        )

        # 划分问题场景
        async for _scene_event in self._run_scene_agent(
            ctx, UPDATE_USER_CONTENT, SCENE_EXAMPLES_PROMPT
        ):
            yield _scene_event

        # 清空 Plan 和 MULTI_PLANS
        if check_plan(ctx) == FlowStatusEnum.COMPLETE:
            yield update_state_event(ctx, state_delta={PLAN: {}, MULTI_PLANS: {}})

        # 制定计划（1. 无计划；2. 计划已完成；3. 计划失败；4. 用户未确认计划）
        if check_plan(ctx) in [
            FlowStatusEnum.NO_PLAN,
            FlowStatusEnum.COMPLETE,
            FlowStatusEnum.FAILED,
        ] or not is_plan_confirmed(ctx):
            async for _plan_make_event in self._run_plan_make_agent(
                ctx, UPDATE_USER_CONTENT, TOOLCHAIN_EXAMPLES_PROMPT
            ):
                yield _plan_make_event

        # 从 MultiPlans 中选择某个计划
        logger.info(f'{ctx.session.id} check_plan = {check_plan(ctx)}')
        if is_plan_confirmed(ctx) and check_plan(ctx) in [FlowStatusEnum.NEW_PLAN]:
            selected_plan_id = ctx.session.state[FRONTEND_STATE_KEY][BIZ].get(
                'selected_plan_id', 0
            )
            logger.info(
                f'{ctx.session.id} biz_state = {ctx.session.state[FRONTEND_STATE_KEY][BIZ]} '
                f'selected_plan_id = {selected_plan_id}'
            )
            plans = ctx.session.state.get(MULTI_PLANS, {}).get('plans', [])
            if (
                selected_plan_id is None
                or not isinstance(selected_plan_id, int)
                or selected_plan_id < 0
                or selected_plan_id >= len(plans)
            ):
                logger.warning(
                    f'{ctx.session.id} invalid selected_plan_id={selected_plan_id}, '
                    f'fallback to 0'
                )
                selected_plan_id = 0
            if not plans:
                logger.warning(f'{ctx.session.id} empty multi_plans, skip plan select')
                return
            selected_plan = plans[selected_plan_id]
            yield update_state_event(ctx, state_delta={PLAN: selected_plan})
            logger.info(
                f'{ctx.session.id} Reset Plan, plan = {ctx.session.state[PLAN]}'
            )

        # 计划未确认，暂停往下执行
        if is_plan_confirmed(ctx):
            async for (
                _plan_execute_and_summary_event
            ) in self._run_plan_execute_and_summary_agent(ctx):
                yield _plan_execute_and_summary_event

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            # 检查是否还有额度
            if not ctx.session.state['quota_remaining']:
                for quota_remaining_event in all_text_event(
                    ctx,
                    self.name,
                    i18n.t('Questionnaire'),
                    ModelRole,
                ):
                    yield quota_remaining_event
                return

            # 上传文件特殊处理
            async for handle_upload_event in self.handle_upload_agent.run_async(ctx):
                yield handle_upload_event

            # 用户意图识别（一旦进入 research 模式，暂时无法退出）
            if ctx.session.state['intent'].get('type', None) != IntentEnum.RESEARCH:
                async for intent_event in self.intent_agent.run_async(ctx):
                    yield intent_event

            # 如果用户上传文件，强制为 research 模式
            if (
                ctx.session.state[UPLOAD_FILE]
                and ctx.session.state['intent']['type'] == IntentEnum.CHAT
            ):
                update_intent = copy.deepcopy(ctx.session.state['intent'])
                update_intent['type'] = IntentEnum.RESEARCH
                yield update_state_event(ctx, state_delta={'intent': update_intent})

            # chat 模式
            if ctx.session.state['intent']['type'] == IntentEnum.CHAT:
                async for chat_event in self.chat_agent.run_async(ctx):
                    yield chat_event
            # research 模式
            else:
                async for _research_event in self._run_research_flow(ctx):
                    yield _research_event
        # 用户触发中止会话
        except CancelledError:
            active_flow = ctx.session.state.get('matmaster_flow_active')
            if active_flow:
                for matmaster_flow_event in context_function_event(
                    ctx,
                    self.name,
                    MATMASTER_FLOW,
                    None,
                    ModelRole,
                    {
                        'title': active_flow.get('title', ''),
                        'status': 'end',
                        'font_color': active_flow.get('font_color', '#0E6DE8'),
                        'bg_color': active_flow.get('bg_color', '#EBF2FB'),
                        'border_color': active_flow.get('border_color', '#B7D3F7'),
                    },
                ):
                    yield matmaster_flow_event
                yield update_state_event(
                    ctx, state_delta={'matmaster_flow_active': None}
                )
            raise
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

        # 评分组件
        for generate_nps_event in context_function_event(
            ctx,
            self.name,
            MATMASTER_GENERATE_NPS,
            {},
            ModelRole,
            {'session_id': ctx.session.id, 'invocation_id': ctx.invocation_id},
        ):
            yield generate_nps_event
