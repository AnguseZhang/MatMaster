import copy
import logging
from typing import AsyncGenerator, List, Optional, Union, override

from google.adk.agents import InvocationContext
from google.adk.agents.llm_agent import (
    AfterModelCallback,
    AfterToolCallback,
    BeforeToolCallback,
)
from google.adk.events import Event
from google.adk.models import BaseLlm
from google.genai.types import FunctionDeclaration
from pydantic import computed_field

from agents.matmaster_agent.base_callbacks.private_callback import (
    inject_function_declarations,
    remove_function_call,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME, ModelRole
from agents.matmaster_agent.core_agents.base_agents.error_agent import (
    ErrorHandleBaseAgent,
)
from agents.matmaster_agent.core_agents.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.core_agents.base_agents.subordinate_agent import (
    SubordinateFeaturesMixin,
)
from agents.matmaster_agent.core_agents.comp_agents.dntransfer_climit_agent import (
    DisallowTransferAndContentLimitLlmAgent,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.recommend_params_agent.prompt import (
    gen_recommend_params_agent_instruction,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.recommend_params_agent.schema import (
    create_tool_args_schema,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.subagent_summary_agent.callback import (
    filter_summary_llm_contents,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.subagent_summary_agent.prompt import (
    get_subagent_summary_prompt,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.tool_call_info_agent.prompt import (
    gen_tool_call_info_instruction,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.tool_call_info_agent.utils import (
    update_tool_call_info_with_function_declarations,
    update_tool_call_info_with_recommend_params,
)
from agents.matmaster_agent.core_agents.comp_agents.tool_connect_agent import (
    ToolConnectAgent,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.model import ToolCallInfoSchema
from agents.matmaster_agent.prompt import (
    GLOBAL_INSTRUCTION,
    GLOBAL_SCHEMA_INSTRUCTION,
    get_vocabulary_enforce_prompt,
)
from agents.matmaster_agent.state import (
    CURRENT_STEP,
    CURRENT_STEP_DESCRIPTION,
    RECOMMEND_PARAMS,
)
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import (
    context_function_event,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class BaseAgentWithRecAndSum(
    SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleBaseAgent
):
    model: Union[str, BaseLlm]
    instruction: str
    tools: list
    doc_summary: bool = False
    after_tool_callback: Optional[AfterToolCallback] = None
    after_model_callback: Optional[AfterModelCallback] = None
    before_tool_callback: Optional[BeforeToolCallback] = None

    def _after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        self._tool_connect_agent = ToolConnectAgent(
            model=self.model,
            name=f"{agent_prefix}_tool_connect_agent",
            tools=self.tools,
            before_model_callback=inject_function_declarations,
            after_model_callback=remove_function_call,
        )

        self._tool_call_info_agent = DisallowTransferAndContentLimitSchemaAgent(
            model=MatMasterLlmConfig.tool_schema_model,
            name=f"{agent_prefix}_tool_call_info_agent",
            output_schema=ToolCallInfoSchema,
            state_key='tool_call_info',
        )

        self._recommend_params_agent = DisallowTransferAndContentLimitLlmAgent(
            model=self.model,
            name=f"{agent_prefix}_recommend_params_agent",
            instruction=gen_recommend_params_agent_instruction(),
            tools=self.tools,
            after_model_callback=remove_function_call,
        )

        self._recommend_params_schema_agent = (
            DisallowTransferAndContentLimitSchemaAgent(
                model=MatMasterLlmConfig.tool_schema_model,
                name=f"{agent_prefix}_recommend_params_schema_agent",
                global_instruction=GLOBAL_SCHEMA_INSTRUCTION,
                state_key=RECOMMEND_PARAMS,
            )
        )
        if self.doc_summary:
            self._summary_agent = DisallowTransferAndContentLimitLlmAgent(
                model=MatMasterLlmConfig.gemini_3_flash,
                name=f"{agent_prefix}_summary_agent",
                description=self.description,
                global_instruction=GLOBAL_INSTRUCTION,
                instruction=self.instruction,
                before_model_callback=filter_summary_llm_contents,
            )
        else:
            self._summary_agent = DisallowTransferAndContentLimitLlmAgent(
                model=MatMasterLlmConfig.default_litellm_model,
                name=f"{agent_prefix}_summary_agent",
                description='You are an assistant to summarize the task to aware the user.',
                global_instruction=GLOBAL_INSTRUCTION,
                instruction=get_subagent_summary_prompt(),
            )

        self.sub_agents = [
            self.tool_connect_agent,
            self.tool_call_info_agent,
            self.recommend_params_agent,
            self.recommend_params_schema_agent,
            self.summary_agent,
        ]

        return self

    @computed_field
    @property
    def tool_connect_agent(self) -> ToolConnectAgent:
        return self._tool_connect_agent

    @computed_field
    @property
    def tool_call_info_agent(self) -> DisallowTransferAndContentLimitSchemaAgent:
        return self._tool_call_info_agent

    @computed_field
    @property
    def recommend_params_agent(self) -> DisallowTransferAndContentLimitLlmAgent:
        return self._recommend_params_agent

    @computed_field
    @property
    def recommend_params_schema_agent(
        self,
    ) -> DisallowTransferAndContentLimitSchemaAgent:
        return self._recommend_params_schema_agent

    @computed_field
    @property
    def summary_agent(self) -> DisallowTransferAndContentLimitLlmAgent:
        return self._summary_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 根据计划来
        current_step = ctx.session.state[CURRENT_STEP]
        current_step_tool_name = current_step['tool_name']

        # 连接 tool-server，获取doc和函数声明
        async for tool_connect_evenet in self.tool_connect_agent.run_async(ctx):
            yield tool_connect_evenet

        # 根据用户问题先推荐一轮
        function_declarations: List[FunctionDeclaration] = ctx.session.state[
            'function_declarations'
        ]
        logger.info(
            f'{ctx.session.id} function_declarations = {function_declarations}, current_step_tool_name = {current_step_tool_name}'
        )
        current_function_declaration = [
            item
            for item in function_declarations
            if item['name'] == current_step_tool_name
        ]

        tool_doc = current_function_declaration[0]['description']
        tool_schema = current_function_declaration[0]['parameters']

        # 如果字符串里包含 {}，替换为 []
        if isinstance(tool_doc, str):
            tool_doc = tool_doc.replace('{', '[').replace('}', ']')
        if isinstance(tool_schema, str):
            tool_schema = tool_schema.replace('{', '[').replace('}', ']')

        tool_args_recommend_prompt = ALL_TOOLS[current_step_tool_name].get(
            'args_setting', ''
        )

        self.tool_call_info_agent.instruction = gen_tool_call_info_instruction(
            user_prompt=current_step[CURRENT_STEP_DESCRIPTION],
            agent_prompt=self.instruction,
            tool_doc=tool_doc,
            tool_schema=tool_schema,
            tool_args_recommend_prompt=tool_args_recommend_prompt,
        )
        logger.info(
            f'{ctx.session.id} current_function_declaration = {current_function_declaration}'
        )
        current_function_declaration[0]['parameters']['required'] = (
            current_function_declaration[0]['parameters'].get('required', [])
        )
        _, self.tool_call_info_agent.output_schema = create_tool_args_schema(
            current_function_declaration[0]['parameters']['required'],
            current_function_declaration,
        )
        async for tool_call_info_event in self.tool_call_info_agent.run_async(ctx):
            yield tool_call_info_event

        update_tool_call_info = copy.deepcopy(ctx.session.state['tool_call_info'])
        update_tool_call_info['tool_name'] = update_tool_call_info.get('tool_name', '')
        update_tool_call_info['tool_args'] = update_tool_call_info.get('tool_args', {})
        update_tool_call_info['missing_tool_args'] = update_tool_call_info.get(
            'missing_tool_args', []
        )

        # modify tool_name
        if (
            ctx.session.state['tool_call_info']['tool_name']
            != current_step['tool_name']
        ):
            update_tool_call_info['tool_name'] = current_step_tool_name

        # remove functions. prefix
        if ctx.session.state['tool_call_info']['tool_name'].startswith('functions.'):
            logger.warning(
                f'{ctx.session.id} Detect wrong tool_name: {ctx.session.state['tool_call_info']['tool_name']}'
            )
            update_tool_call_info['tool_name'] = update_tool_call_info[
                'tool_name'
            ].replace('functions.', '')

        yield update_state_event(
            ctx, state_delta={'tool_call_info': update_tool_call_info}
        )

        tool_call_info = ctx.session.state['tool_call_info']
        logger.info(
            f'{ctx.session.id} tool_call_info = {tool_call_info}, '
            f'current_function_declaration = {current_function_declaration}'
        )
        tool_call_info = update_tool_call_info_with_function_declarations(
            tool_call_info, current_function_declaration
        )
        yield update_state_event(ctx, state_delta={'tool_call_info': tool_call_info})

        logger.info(
            f'{ctx.session.id} tool_call_info_with_function_declarations = {tool_call_info}'
        )

        missing_tool_args = tool_call_info.get('missing_tool_args', None)
        # 过滤 executor，storage 参数
        missing_tool_args = [
            item for item in missing_tool_args if item not in ['executor', 'storage']
        ]
        if missing_tool_args:
            async for recommend_params_event in self.recommend_params_agent.run_async(
                ctx
            ):
                yield recommend_params_event

            self.recommend_params_schema_agent.instruction = (
                tool_doc + '\n' + tool_args_recommend_prompt
            )
            self.recommend_params_schema_agent.output_schema, _ = (
                create_tool_args_schema(missing_tool_args, current_function_declaration)
            )
            async for (
                recommend_params_schema_event
            ) in self.recommend_params_schema_agent.run_async(ctx):
                yield recommend_params_schema_event

            recommend_params = ctx.session.state[RECOMMEND_PARAMS]
            tool_call_info = update_tool_call_info_with_recommend_params(
                tool_call_info, recommend_params
            )
            yield update_state_event(
                ctx, state_delta={'tool_call_info': tool_call_info}
            )
            logger.info(
                f'{ctx.session.id} tool_call_info_with_recommend_params = {ctx.session.state['tool_call_info']}'
            )

        # 前置 tool_hallucination 为 False
        yield update_state_event(ctx, state_delta={'tool_hallucination': False})
        for _ in range(2):
            async for submit_event in self.submit_agent.run_async(ctx):
                yield submit_event

            if not ctx.session.state['tool_hallucination']:
                break

        step_title = ctx.session.state.get('step_title', {}).get(
            'title',
            current_step_tool_name,
        )
        for matmaster_flow_event in context_function_event(
            ctx,
            self.name,
            'matmaster_flow',
            None,
            ModelRole,
            {
                'title': step_title,
                'status': 'end',
                'font_color': '#0E6DE8',
                'bg_color': '#EBF2FB',
                'border_color': '#B7D3F7',
            },
        ):
            yield matmaster_flow_event
        yield update_state_event(ctx, state_delta={'matmaster_flow_active': None})

        # TODO: needs a better way to handle customized summary prompt
        if ALL_TOOLS[current_step_tool_name].get('summary_prompt') is not None:
            custom_prompt = ALL_TOOLS[current_step_tool_name].get('summary_prompt')
            self.summary_agent.instruction = (
                f"{custom_prompt}\n\n{get_vocabulary_enforce_prompt()}"
            )

        if current_step['status'] != PlanStepStatusEnum.SUBMITTED:
            async for summary_event in self.summary_agent.run_async(ctx):
                yield summary_event
