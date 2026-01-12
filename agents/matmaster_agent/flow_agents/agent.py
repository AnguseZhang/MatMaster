import copy
import json
import logging
from typing import AsyncGenerator

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_callbacks.private_callback import (
    remove_function_call,
)
from agents.matmaster_agent.constant import CURRENT_ENV, MATMASTER_AGENT_NAME, ModelRole
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
from agents.matmaster_agent.flow_agents.execution_agent.agent import (
    MatMasterSupervisorAgent,
)
from agents.matmaster_agent.flow_agents.expand_agent.agent import ExpandAgent
from agents.matmaster_agent.flow_agents.expand_agent.prompt import EXPAND_INSTRUCTION
from agents.matmaster_agent.flow_agents.expand_agent.schema import ExpandSchema
from agents.matmaster_agent.flow_agents.handle_upload_agent.agent import (
    HandleUploadAgent,
)
from agents.matmaster_agent.flow_agents.intent_agent.model import IntentEnum
from agents.matmaster_agent.flow_agents.intent_agent.prompt import INTENT_INSTRUCTION
from agents.matmaster_agent.flow_agents.intent_agent.schema import IntentSchema
from agents.matmaster_agent.flow_agents.plan_confirm_agent.prompt import (
    PlanConfirmInstruction,
)
from agents.matmaster_agent.flow_agents.plan_confirm_agent.schema import (
    PlanConfirmSchema,
)
from agents.matmaster_agent.flow_agents.plan_info_agent.prompt import (
    get_plan_info_instruction,
)
from agents.matmaster_agent.flow_agents.plan_make_agent.agent import PlanMakeAgent
from agents.matmaster_agent.flow_agents.plan_make_agent.prompt import (
    get_plan_make_instruction,
)
from agents.matmaster_agent.flow_agents.scene_agent.prompt import SCENE_INSTRUCTION
from agents.matmaster_agent.flow_agents.scene_agent.schema import SceneSchema
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum, PlanSchema
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
from agents.matmaster_agent.flow_agents.style import (
    separate_card,
)
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    create_dynamic_plan_schema,
    get_tools_list,
    should_bypass_confirmation,
)
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.locales import i18n
from agents.matmaster_agent.logger import PrefixFilter
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
from agents.matmaster_agent.state import EXPAND, UPLOAD_FILE
from agents.matmaster_agent.sub_agents.mapping import (
    AGENT_CLASS_MAPPING,
    ALL_AGENT_TOOLS_LIST,
)
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    context_function_event,
    send_error_event,
    update_state_event,
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
            name='intent_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='识别用户的意图',
            instruction=INTENT_INSTRUCTION,
            output_schema=IntentSchema,
            state_key='intent',
        )

        self._expand_agent = ExpandAgent(
            name='expand_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='扩写用户的问题',
            instruction=EXPAND_INSTRUCTION,
            output_schema=ExpandSchema,
            state_key=EXPAND,
        )

        self._scene_agent = DisallowTransferAndContentLimitSchemaAgent(
            name='scene_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='把用户的问题划分到特定的场景',
            instruction=SCENE_INSTRUCTION,
            output_schema=SceneSchema,
            state_key='single_scenes',
        )

        self._plan_make_agent = PlanMakeAgent(
            name='plan_make_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='根据用户的问题依据现有工具执行计划，如果没有工具可用，告知用户，不要自己制造工具或幻想',
            output_schema=PlanSchema,
            state_key='plan',
        )

        self._plan_confirm_agent = DisallowTransferAndContentLimitSchemaAgent(
            name='plan_confirm_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='判断用户对计划是否认可',
            instruction=PlanConfirmInstruction,
            output_schema=PlanConfirmSchema,
            state_key='plan_confirm',
        )

        self._plan_info_agent = DisallowTransferAndContentLimitLlmAgent(
            name='plan_info_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='根据 materials_plan 返回的计划进行总结',
            # instruction=PLAN_INFO_INSTRUCTION,
        )

        # execution_agent
        step_validation_agent = DisallowTransferAndContentLimitSchemaAgent(
            name='step_validation_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='校验步骤执行结果是否合理',
            instruction=STEP_VALIDATION_INSTRUCTION,
            output_schema=StepValidationSchema,
            state_key='step_validation',
        )

        step_title_agent = DisallowTransferAndContentLimitSchemaAgent(
            name='step_title_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            global_instruction=GLOBAL_INSTRUCTION,
            description='给出每一步的标题',
            instruction=STEP_TITLE_INSTRUCTION,
            output_schema=StepTitleSchema,
            state_key='step_title',
        )

        self._execution_agent = MatMasterSupervisorAgent(
            name='execution_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='根据 materials_plan 返回的计划进行总结',
            instruction='',
            sub_agents=[
                sub_agent(MatMasterLlmConfig)
                for sub_agent in AGENT_CLASS_MAPPING.values()
            ]
            + [step_title_agent]
            + [step_validation_agent],
        )

        self._analysis_agent = DisallowTransferAndContentLimitLlmAgent(
            name='execution_summary_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction='使用 {target_language} 回答',
            description=f'总结本轮的计划执行情况\n格式要求: \n{HUMAN_FRIENDLY_FORMAT_REQUIREMENT}',
            instruction='',
        )

        self.sub_agents = [
            self.chat_agent,
            self.handle_upload_agent,
            self.intent_agent,
            self.expand_agent,
            self.scene_agent,
            self.plan_make_agent,
            self.plan_info_agent,
            self.plan_confirm_agent,
            self.execution_agent,
            self.analysis_agent,
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
    def plan_info_agent(self) -> LlmAgent:
        return self._plan_info_agent

    @computed_field
    @property
    def plan_confirm_agent(self) -> LlmAgent:
        return self._plan_confirm_agent

    @computed_field
    @property
    def execution_agent(self) -> LlmAgent:
        return self._execution_agent

    @computed_field
    @property
    def analysis_agent(self) -> LlmAgent:
        return self._analysis_agent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            for _ in range(2):
                loop_continue = False
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
                async for handle_upload_event in self.handle_upload_agent.run_async(
                    ctx
                ):
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
                    # 检索 ICL 示例
                    icl_examples = select_examples(
                        ctx.user_content.parts[0].text,
                        ctx.session.id,
                        CURRENT_ENV,
                        logger,
                    )
                    EXPAND_INPUT_EXAMPLES_PROMPT = expand_input_examples(icl_examples)
                    logger.info(f'{ctx.session.id} {EXPAND_INPUT_EXAMPLES_PROMPT}')
                    # 扩写用户问题
                    self.expand_agent.instruction = (
                        EXPAND_INSTRUCTION + EXPAND_INPUT_EXAMPLES_PROMPT
                    )
                    async for expand_event in self.expand_agent.run_async(ctx):
                        yield expand_event

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
                    SCENE_EXAMPLES_PROMPT = scene_tags_from_examples(
                        icl_update_examples
                    )
                    TOOLCHAIN_EXAMPLES_PROMPT = toolchain_from_examples(
                        icl_update_examples
                    )
                    logger.info(f'{ctx.session.id} {SCENE_EXAMPLES_PROMPT}')
                    logger.info(f'{ctx.session.id} {TOOLCHAIN_EXAMPLES_PROMPT}')

                    # 划分问题场景
                    self.scene_agent.instruction = (
                        SCENE_INSTRUCTION + UPDATE_USER_CONTENT + SCENE_EXAMPLES_PROMPT
                    )
                    async for scene_event in self.scene_agent.run_async(ctx):
                        yield scene_event

                    before_scenes = ctx.session.state['scenes']
                    single_scene = ctx.session.state['single_scenes']['type']
                    scenes = list(set(before_scenes + single_scene + ['universal']))
                    logger.info(f'{ctx.session.id} scenes = {scenes}')
                    yield update_state_event(
                        ctx, state_delta={'scenes': copy.deepcopy(scenes)}
                    )

                    # 计划是否确认（1. 上一步计划完成；2. 用户未确认计划）
                    if check_plan(
                        ctx
                    ) == FlowStatusEnum.COMPLETE or not ctx.session.state[
                        'plan_confirm'
                    ].get(
                        'flag', False
                    ):
                        async for (
                            plan_confirm_event
                        ) in self.plan_confirm_agent.run_async(ctx):
                            yield plan_confirm_event

                        if ctx.user_content.parts[
                            0
                        ].text == '确认计划' and not ctx.session.state[
                            'plan_confirm'
                        ].get(
                            'flag', False
                        ):
                            logger.warning(
                                f'{ctx.session.id} 确认计划 not confirm, manually setting it'
                            )
                            yield update_state_event(
                                ctx, state_delta={'plan_confirm': True}
                            )

                    plan_confirm = ctx.session.state['plan_confirm'].get('flag', False)

                    # 判断要不要制定计划（1. 无计划；2. 计划未通过；3. 计划已完成）
                    if (
                        check_plan(ctx)
                        in [
                            FlowStatusEnum.NO_PLAN,
                            FlowStatusEnum.COMPLETE,
                            FlowStatusEnum.FAILED,
                        ]
                        or not plan_confirm
                    ):
                        # 制定计划
                        if check_plan(ctx) == FlowStatusEnum.FAILED:
                            for replan_event in all_text_event(
                                ctx, self.name, separate_card('重新制定计划'), ModelRole
                            ):
                                yield replan_event

                        available_tools = get_tools_list(ctx, scenes)
                        if not available_tools:
                            available_tools = ALL_AGENT_TOOLS_LIST
                        available_tools_with_info_str = '\n'.join(
                            f"{tool}\n"
                            f"    scene: {', '.join(ALL_TOOLS[tool]['scene'])}\n"
                            f"    description: {ALL_TOOLS[tool]['description']}\n"
                            f"    needs_file_input: {ALL_TOOLS[tool].get('needs_file_input', None)}\n"
                            f"    generates_file_output: {ALL_TOOLS[tool].get('generates_file_output', None)}\n"
                            for tool in available_tools
                        )
                        self.plan_make_agent.instruction = get_plan_make_instruction(
                            available_tools_with_info_str
                            + UPDATE_USER_CONTENT
                            + TOOLCHAIN_EXAMPLES_PROMPT
                        )
                        self.plan_make_agent.output_schema = create_dynamic_plan_schema(
                            available_tools
                        )
                        async for plan_event in self.plan_make_agent.run_async(ctx):
                            yield plan_event

                        # 总结计划
                        for matmaster_flow_event in context_function_event(
                            ctx,
                            self.name,
                            'matmaster_flow',
                            None,
                            ModelRole,
                            {
                                'title': '制定计划',
                                'status': 'start',
                                'font_color': '#30B37F',
                                'bg_color': '#EFF8F5',
                                'border_color': '#B2E0CE',
                            },
                        ):
                            yield matmaster_flow_event
                        plan_steps = ctx.session.state['plan'].get('steps', [])
                        tool_names = [
                            step.get('tool_name')
                            for step in plan_steps
                            if step.get('tool_name')
                        ]
                        self.plan_info_agent.instruction = get_plan_info_instruction(
                            tool_names
                        )
                        async for plan_summary_event in self.plan_info_agent.run_async(
                            ctx
                        ):
                            yield plan_summary_event
                        for matmaster_flow_event in context_function_event(
                            ctx,
                            self.name,
                            'matmaster_flow',
                            None,
                            ModelRole,
                            {
                                'title': '制定计划',
                                'status': 'end',
                                'font_color': '#30B37F',
                                'bg_color': '#EFF8F5',
                                'border_color': '#B2E0CE',
                            },
                        ):
                            yield matmaster_flow_event

                        # 更新计划为可执行的计划
                        update_plan = copy.deepcopy(ctx.session.state['plan'])
                        origin_steps = ctx.session.state['plan']['steps']
                        actual_steps = []
                        for step in origin_steps:
                            if step.get('tool_name'):
                                actual_steps.append(step)
                            else:
                                break
                        update_plan['steps'] = actual_steps
                        yield update_state_event(ctx, state_delta={'plan': update_plan})

                        # 检查是否应该跳过用户确认步骤
                        if should_bypass_confirmation(ctx):
                            # 自动设置计划确认状态
                            yield update_state_event(
                                ctx,
                                state_delta={
                                    'plan_confirm': {
                                        'flag': True,
                                        'reason': 'Auto confirmed for single bypass tool',
                                    }
                                },
                            )
                        else:
                            for generate_plan_confirm_event in context_function_event(
                                ctx,
                                self.name,
                                'matmaster_generate_follow_up',
                                {},
                                ModelRole,
                                {
                                    'follow_up_result': json.dumps(
                                        {
                                            'invocation_id': ctx.invocation_id,
                                            'title': i18n.t('PlanOperation'),
                                            'list': [
                                                i18n.t('ConfirmPlan'),
                                                i18n.t('RePlan'),
                                            ],
                                        }
                                    ),
                                },
                            ):
                                yield generate_plan_confirm_event

                    # 计划未确认，暂停往下执行
                    if ctx.session.state['plan_confirm']['flag']:
                        # 重置 scenes
                        yield update_state_event(ctx, state_delta={'scenes': []})
                        # 执行计划
                        if ctx.session.state['plan']['feasibility'] in ['full', 'part']:
                            async for execution_event in self.execution_agent.run_async(
                                ctx
                            ):
                                yield execution_event

                        # 全部执行完毕，总结执行情况
                        if (
                            check_plan(ctx) == FlowStatusEnum.COMPLETE
                            or ctx.session.state['plan']['feasibility'] == 'null'
                        ):
                            # Skip summary for single-tool plans
                            plan_steps = ctx.session.state['plan'].get('steps', [])
                            tool_count = sum(
                                1 for step in plan_steps if step.get('tool_name')
                            )

                            is_async_agent = issubclass(
                                AGENT_CLASS_MAPPING[
                                    ALL_TOOLS[plan_steps[0]['tool_name']][
                                        'belonging_agent'
                                    ]
                                ],
                                BaseAsyncJobAgent,
                            )
                            logger.info(
                                f'is_async_agent = {is_async_agent}, tool_count = {tool_count}'
                            )

                            # 渲染总结
                            if tool_count > 1 or is_async_agent:
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
                                self._analysis_agent.instruction = (
                                    get_analysis_instruction(ctx.session.state['plan'])
                                )
                                async for (
                                    analysis_event
                                ) in self.analysis_agent.run_async(ctx):
                                    yield analysis_event
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
                        elif check_plan(ctx) == FlowStatusEnum.FAILED:
                            loop_continue = True
                # 退出循环
                if not loop_continue:
                    break
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

        # 评分组件
        for generate_nps_event in context_function_event(
            ctx,
            self.name,
            'matmaster_generate_nps',
            {},
            ModelRole,
            {'session_id': ctx.session.id, 'invocation_id': ctx.invocation_id},
        ):
            yield generate_nps_event
