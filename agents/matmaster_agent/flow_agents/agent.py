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
from agents.matmaster_agent.constant import ModelRole
from agents.matmaster_agent.flow_agents.analysis_agent.prompt import (
    get_analysis_instruction,
)
from agents.matmaster_agent.flow_agents.execution_agent.agent import (
    MatMasterSupervisorAgent,
)
from agents.matmaster_agent.flow_agents.expand_agent.agent import ExpandAgent
from agents.matmaster_agent.flow_agents.expand_agent.prompt import EXPAND_INSTRUCTION
from agents.matmaster_agent.flow_agents.expand_agent.schema import ExpandSchema
from agents.matmaster_agent.flow_agents.intent_agent.model import IntentEnum
from agents.matmaster_agent.flow_agents.intent_agent.prompt import INTENT_INSTRUCTION
from agents.matmaster_agent.flow_agents.intent_agent.schema import IntentSchema
from agents.matmaster_agent.flow_agents.plan_confirm_agent.prompt import (
    PlanConfirmInstruction,
)
from agents.matmaster_agent.flow_agents.plan_confirm_agent.schema import (
    PlanConfirmSchema,
)
from agents.matmaster_agent.flow_agents.plan_execution_check_agent.prompt import (
    PLAN_EXECUTION_CHECK_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.plan_info_agent.prompt import (
    PLAN_INFO_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.plan_make_agent.agent import PlanMakeAgent
from agents.matmaster_agent.flow_agents.plan_make_agent.prompt import (
    get_plan_make_instruction,
)
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.flow_agents.scene_agent.prompt import SCENE_INSTRUCTION
from agents.matmaster_agent.flow_agents.scene_agent.schema import SceneSchema
from agents.matmaster_agent.flow_agents.schema import FlowStatusEnum, PlanSchema
from agents.matmaster_agent.flow_agents.utils import (
    check_plan,
    create_dynamic_plan_schema,
    get_tools_list,
)
from agents.matmaster_agent.llm_config import DEFAULT_MODEL, MatMasterLlmConfig
from agents.matmaster_agent.style import plan_ask_confirm_card, running_job_card
from agents.matmaster_agent.sub_agents.mapping import AGENT_CLASS_MAPPING, ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    send_error_event,
    update_state_event,
)
from agents.matmaster_agent.utils.job_utils import (
    has_job_running,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MatMasterFlowAgent(LlmAgent):
    @model_validator(mode='after')
    def after_init(self):
        self._chat_agent = DisallowTransferLlmAgent(
            name='chat_agent', model=MatMasterLlmConfig.deepseek_chat
        )

        self._intent_agent = SchemaAgent(
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
            state_key='scene',
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

        plan_execution_check_agent = DisallowTransferLlmAgent(
            name='plan_execution_check_agent',
            model=MatMasterLlmConfig.default_litellm_model,
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
            + [plan_execution_check_agent],
        )

        self._analysis_agent = DisallowTransferLlmAgent(
            name='execution_summary_agent',
            model=MatMasterLlmConfig.default_litellm_model,
            global_instruction='使用 {target_language} 回答',
            description='总结本轮的计划执行情况',
            instruction='',
        )

        self.sub_agents = [
            self.chat_agent,
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
            # 用户意图识别（一旦进入 research 模式，暂时无法退出）
            if ctx.session.state['intent'].get('type', None) != IntentEnum.RESEARCH:
                async for intent_event in self.intent_agent.run_async(ctx):
                    yield intent_event

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

                scenes = list(set(ctx.session.state['scene']['type']))
                if (
                    jobs_dict := ctx.session.state['long_running_jobs']
                ) and has_job_running(
                    jobs_dict
                ):  # 确认当前有在运行中的任务
                    for job_running_event in all_text_event(
                        ctx, self.name, running_job_card(), ModelRole
                    ):
                        yield job_running_event

                    update_scenes = copy.deepcopy(ctx.session.state['scene'])
                    update_scenes['type'].insert(0, SceneEnum.JobResultRetrieval)
                    yield update_state_event(ctx, state_delta={'scene': update_scenes})

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
                    available_tools_with_description = {
                        item: ALL_TOOLS[item]['description'] for item in available_tools
                    }
                    available_tools_with_description_str = '\n'.join(
                        [
                            f"{key}:{value}"
                            for key, value in available_tools_with_description.items()
                        ]
                    )
                    self.plan_make_agent.instruction = get_plan_make_instruction(
                        available_tools_with_description_str
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

                # 计划未确认，暂停往下执行
                if not plan_confirm:
                    return

                # 执行计划
                if ctx.session.state['plan']['feasibility'] in ['full', 'part']:
                    async for execution_event in self.execution_agent.run_async(ctx):
                        yield execution_event

                # 全部执行完毕，总结执行情况
                if (
                    check_plan(ctx) == FlowStatusEnum.COMPLETE
                    or ctx.session.state['plan']['feasibility'] == 'null'
                ):
                    self._analysis_agent.instruction = get_analysis_instruction(
                        ctx.session.state['plan']
                    )
                    async for analysis_event in self.analysis_agent.run_async(ctx):
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
