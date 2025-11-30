import copy
import logging
from typing import AsyncGenerator

from google.adk.agents import InvocationContext, LlmAgent
from google.adk.events import Event
from google.adk.models.lite_llm import LiteLlm
from pydantic import computed_field, model_validator

from agents.matmaster_agent.base_agents.disallow_transfer_agent import (
    DisallowTransferLlmAgent,
)
from agents.matmaster_agent.base_agents.schema_agent import SchemaAgent
from agents.matmaster_agent.base_callbacks.private_callback import remove_function_call
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
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
from agents.matmaster_agent.flow_agents.execution_result_agent.prompt import (
    PLAN_EXECUTION_CHECK_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.expand_agent.agent import ExpandAgent
from agents.matmaster_agent.flow_agents.expand_agent.prompt import EXPAND_INSTRUCTION
from agents.matmaster_agent.flow_agents.expand_agent.schema import ExpandSchema
from agents.matmaster_agent.flow_agents.intent_agent.agent import IntentAgent
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
    PLAN_INFO_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.plan_make_agent.agent import PlanMakeAgent
from agents.matmaster_agent.flow_agents.plan_make_agent.prompt import (
    get_plan_make_instruction,
)
from agents.matmaster_agent.flow_agents.scene_agent.prompt import SCENE_INSTRUCTION
from agents.matmaster_agent.flow_agents.scene_agent.schema import SceneSchema
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum, PlanSchema
from agents.matmaster_agent.flow_agents.style import (
    all_summary_card,
    plan_ask_confirm_card,
)
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    create_dynamic_plan_schema,
    get_tools_list,
)
from agents.matmaster_agent.llm_config import DEFAULT_MODEL, MatMasterLlmConfig
from agents.matmaster_agent.logger import PrefixFilter
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
        self._chat_agent = DisallowTransferLlmAgent(
            name='chat_agent',
            model=MatMasterLlmConfig.deepseek_chat,
            description=ChatAgentDescription,
            instruction=ChatAgentInstruction,
            global_instruction=ChatAgentGlobalInstruction,
            after_model_callback=remove_function_call,
        )

        self._intent_agent = IntentAgent(
            name='intent_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='识别用户的意图',
            instruction=INTENT_INSTRUCTION,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=IntentSchema,
            state_key='intent',
        )

        self._expand_agent = ExpandAgent(
            name='expand_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='扩写用户的问题',
            instruction=EXPAND_INSTRUCTION,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=ExpandSchema,
            state_key='expand',
        )

        self._scene_agent = SchemaAgent(
            name='scene_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='把用户的问题划分到特定的场景',
            instruction=SCENE_INSTRUCTION,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=SceneSchema,
            state_key='single_scenes',
        )

        self._plan_make_agent = PlanMakeAgent(
            name='plan_make_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='根据用户的问题依据现有工具执行计划，如果没有工具可用，告知用户，不要自己制造工具或幻想',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=PlanSchema,
            state_key='plan',
        )

        self._plan_confirm_agent = SchemaAgent(
            name='plan_confirm_agent',
            model=MatMasterLlmConfig.tool_schema_model,
            description='判断用户对计划是否认可',
            instruction=PlanConfirmInstruction,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            output_schema=PlanConfirmSchema,
            state_key='plan_confirm',
        )

        self._plan_info_agent = DisallowTransferLlmAgent(
            name='plan_info_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            description='根据 materials_plan 返回的计划进行总结',
            instruction=PLAN_INFO_INSTRUCTION,
        )

        execution_result_agent = DisallowTransferLlmAgent(
            name='execution_result_agent',
            model=self.model,
            description='汇总计划的执行情况，并根据计划提示下一步的动作',
            instruction=PLAN_EXECUTION_CHECK_INSTRUCTION,
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
            + [execution_result_agent],
        )

        self._analysis_agent = DisallowTransferLlmAgent(
            name='execution_summary_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction='使用 {target_language} 回答',
            description='总结本轮的计划执行情况',
            instruction='',
        )

        # 初始化时不包含 analysis_agent
        self.sub_agents = [
            self.chat_agent,
            self.intent_agent,
            self.expand_agent,
            self.scene_agent,
            self.plan_make_agent,
            self.plan_info_agent,
            self.plan_confirm_agent,
            self.execution_agent,
        ]

        return self

    @computed_field
    @property
    def chat_agent(self) -> LlmAgent:
        return self._chat_agent

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

    def _get_plan_tools_count(self, ctx: InvocationContext) -> int:
        """Count the number of tools in the current plan."""
        if not ctx.session.state.get('plan'):
            return 0

        plan = ctx.session.state['plan']
        if not isinstance(plan, dict) or 'steps' not in plan:
            return 0

        steps = plan['steps']
        if not isinstance(steps, list):
            return 0

        # Count unique tools in the plan steps
        tool_names = set()
        for step in steps:
            if isinstance(step, dict) and step.get('tool_name'):
                tool_names.add(step['tool_name'])

        return len(tool_names)

    def _get_effective_sub_agents(self, ctx: InvocationContext) -> list:
        """Get the list of sub agents, conditionally including analysis_agent."""
        # Start with base sub_agents
        effective_sub_agents = self.sub_agents[:]

        # Check if we should include analysis_agent
        tools_count = self._get_plan_tools_count(ctx)
        if tools_count > 1:
            effective_sub_agents.append(self.analysis_agent)

        return effective_sub_agents

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            if not ctx.session.state['quota_remaining']:
                for quota_remaining_event in all_text_event(
                    ctx, self.name, '每日免费次数不足，请申请后重试', ModelRole
                ):
                    yield quota_remaining_event
                return

            # 用户意图识别（一旦进入 research 模式，暂时无法退出）
            if ctx.session.state['intent'].get('type', None) != IntentEnum.RESEARCH:
                async for intent_event in self.intent_agent.run_async(ctx):
                    yield intent_event

            # 如果用户上传文件，强制为 research 模式
            if (
                ctx.session.state['upload_file']
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
                # 扩写用户问题
                async for expand_event in self.expand_agent.run_async(ctx):
                    yield expand_event

                # 划分问题场景
                async for scene_event in self.scene_agent.run_async(ctx):
                    yield scene_event

                before_scenes = ctx.session.state['scenes']
                single_scene = ctx.session.state['single_scenes']['type']
                scenes = list(set(before_scenes + single_scene))
                logger.info(f'{ctx.session.id} scenes = {scenes}')
                yield update_state_event(
                    ctx, state_delta={'scenes': copy.deepcopy(scenes)}
                )

                # 计划是否确认（1. 上一步计划完成；2. 用户未确认计划）
                if check_plan(ctx) == FlowStatusEnum.COMPLETE or not ctx.session.state[
                    'plan_confirm'
                ].get('flag', False):
                    async for plan_confirm_event in self.plan_confirm_agent.run_async(
                        ctx
                    ):
                        yield plan_confirm_event

                plan_confirm = ctx.session.state['plan_confirm'].get('flag', False)

                # 判断要不要制定计划（1. 无计划；2. 计划未通过；3. 计划已完成）
                if (
                    check_plan(ctx) in [FlowStatusEnum.NO_PLAN, FlowStatusEnum.COMPLETE]
                    or not plan_confirm
                ):
                    # 制定计划
                    available_tools = get_tools_list(scenes)
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
                    self.plan_make_agent.instruction = get_plan_make_instruction(
                        available_tools_with_info_str
                    )
                    self.plan_make_agent.output_schema = create_dynamic_plan_schema(
                        available_tools
                    )
                    async for plan_event in self.plan_make_agent.run_async(ctx):
                        yield plan_event

                    # 总结计划
                    async for plan_summary_event in self.plan_info_agent.run_async(ctx):
                        yield plan_summary_event

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

                    # 询问用户是否确认计划
                    for plan_ask_confirm_event in all_text_event(
                        ctx, self.name, plan_ask_confirm_card(), ModelRole
                    ):
                        yield plan_ask_confirm_event
                    if plan_confirm:
                        yield update_state_event(
                            ctx,
                            state_delta={
                                'plan_confirm': {'flag': False, 'reason': ' New Plan'}
                            },
                        )

                # 计划未确认，暂停往下执行
                if ctx.session.state['plan_confirm']['flag']:
                    # 重置 scenes
                    yield update_state_event(ctx, state_delta={'scenes': []})
                    # 执行计划
                    if ctx.session.state['plan']['feasibility'] in ['full', 'part']:
                        # 使用包含或不包含 analysis_agent 的有效子代理列表
                        original_sub_agents = self.sub_agents
                        self.sub_agents = self._get_effective_sub_agents(ctx)

                        try:
                            async for execution_event in self.execution_agent.run_async(
                                ctx
                            ):
                                yield execution_event
                        finally:
                            # 恢复原始的 sub_agents
                            self.sub_agents = original_sub_agents

                    # 全部执行完毕，总结执行情况
                    if (
                        check_plan(ctx) == FlowStatusEnum.COMPLETE
                        or ctx.session.state['plan']['feasibility'] == 'null'
                    ):
                        for all_summary_event in all_text_event(
                            ctx, self.name, all_summary_card(), ModelRole
                        ):
                            yield all_summary_event
                        self._analysis_agent.instruction = get_analysis_instruction(
                            ctx.session.state['plan']
                        )
                        # 只有当计划中包含多个工具时才运行 analysis_agent
                        tools_count = self._get_plan_tools_count(ctx)
                        if tools_count > 1:
                            async for analysis_event in self.analysis_agent.run_async(
                                ctx
                            ):
                                yield analysis_event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

            error_handel_agent = LlmAgent(
                name='error_handel_agent',
                model=LiteLlm(model=DEFAULT_MODEL),
            )
            # 调用错误处理 Agent
            async for error_handel_event in error_handel_agent.run_async(ctx):
                yield error_handel_event

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
