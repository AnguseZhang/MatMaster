import copy
import logging
from typing import AsyncGenerator, Optional, Union, override

from google.adk.agents import InvocationContext
from google.adk.agents.llm_agent import AfterModelCallback
from google.adk.events import Event
from google.adk.models import BaseLlm
from pydantic import computed_field
from agents.matmaster_agent.base_callbacks.private_callback import (
    inject_function_declarations,
    remove_function_call,
)
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.base_agents.error_agent import ErrorHandleBaseAgent
from agents.matmaster_agent.core_agents.base_agents.mcp_agent import MCPInitMixin
from agents.matmaster_agent.core_agents.base_agents.schema_agent import SchemaAgent, \
    DisallowTransferAndContentLimitSchemaAgent
from agents.matmaster_agent.core_agents.base_agents.subordinate_agent import SubordinateFeaturesMixin
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.recommend_params_agent.prompt import \
    gen_recommend_params_agent_instruction
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.recommend_params_agent.schema import \
    create_tool_args_schema
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.tool_call_info_agent.prompt import \
    gen_tool_call_info_instruction
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.tool_call_info_agent.utils import \
    update_tool_call_info_with_function_declarations, update_tool_call_info_with_recommend_params
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.model import ToolCallInfoSchema
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.utils.event_utils import update_state_event

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class BaseAgentWithParamsRecommendation(
    SubordinateFeaturesMixin, MCPInitMixin, ErrorHandleBaseAgent
):
    model: Union[str, BaseLlm]
    instruction: str
    tools: list
    after_model_callback: Optional[AfterModelCallback] = None

    def _after_init(self):
        agent_prefix = self.name.replace('_agent', '')

        self._tool_call_info_agent = DisallowTransferAndContentLimitSchemaAgent(
            model=self.model,
            name=f"{agent_prefix}_tool_call_info_agent",
            tools=self.tools,
            before_model_callback=inject_function_declarations,
            after_model_callback=remove_function_call,
            output_schema=ToolCallInfoSchema,
            state_key='tool_call_info',
        )

        self._recommend_params_agent = DisallowTransferAndContentLimitSchemaAgent(
            model=self.model,
            name=f"{agent_prefix}_recommend_params_agent",
            instruction=gen_recommend_params_agent_instruction(),
            tools=self.tools,
            after_model_callback=remove_function_call,
        )

        self._recommend_params_schema_agent = SchemaAgent(
            model=MatMasterLlmConfig.tool_schema_model,
            name=f"{agent_prefix}_recommend_params_schema_agent",
            state_key='recommend_params',
        )

        return self

    @computed_field
    @property
    def tool_call_info_agent(self) -> SchemaAgent:
        return self._tool_call_info_agent

    @computed_field
    @property
    def recommend_params_agent(self) -> DisallowTransferAndContentLimitSchemaAgent:
        return self._recommend_params_agent

    @computed_field
    @property
    def recommend_params_schema_agent(self) -> SchemaAgent:
        return self._recommend_params_schema_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 根据计划来
        current_step_tool = ctx.session.state['plan']['steps'][
            ctx.session.state['plan_index']
        ]['tools'][ctx.session.state['tool_index']]
        current_step_tool_name = current_step_tool['tool_name']
        self.tool_call_info_agent.instruction = gen_tool_call_info_instruction(
            user_prompt=current_step_tool['description'],
            agent_prompt=self.instruction,
            tool_args_recommend_prompt=ALL_TOOLS[current_step_tool_name].get(
                'args_setting', ''
            ),
        )
        async for tool_call_info_event in self.tool_call_info_agent.run_async(ctx):
            yield tool_call_info_event

        if ctx.session.state['error_occurred']:
            return

        if (
            not ctx.session.state['tool_call_info']
            or ctx.session.state['tool_call_info']['tool_name']
            != current_step_tool['tool_name']
        ):
            update_tool_call_info = copy.deepcopy(ctx.session.state['tool_call_info'])
            update_tool_call_info['tool_name'] = current_step_tool_name
            update_tool_call_info['tool_args'] = {}
            update_tool_call_info['missing_tool_args'] = []
            yield update_state_event(
                ctx, state_delta={'tool_call_info': update_tool_call_info}
            )

        if ctx.session.state['tool_call_info']['tool_name'].startswith('functions.'):
            logger.warning(
                f'{ctx.session.id} Detect wrong tool_name: {ctx.session.state['tool_call_info']['tool_name']}'
            )
            update_tool_call_info = copy.deepcopy(ctx.session.state['tool_call_info'])
            update_tool_call_info['tool_name'] = update_tool_call_info[
                'tool_name'
            ].replace('functions.', '')
            yield update_state_event(
                ctx, state_delta={'tool_call_info': update_tool_call_info}
            )

        tool_call_info = ctx.session.state['tool_call_info']
        function_declarations = ctx.session.state['function_declarations']
        tool_call_info, current_function_declaration = (
            update_tool_call_info_with_function_declarations(
                tool_call_info, function_declarations
            )
        )

        yield update_state_event(ctx, state_delta={'tool_call_info': tool_call_info})

        logger.info(
            f'{ctx.session.id} tool_call_info_with_function_declarations = {tool_call_info}'
        )

        missing_tool_args = tool_call_info.get('missing_tool_args', None)
        if missing_tool_args:
            async for recommend_params_event in self.recommend_params_agent.run_async(
                ctx
            ):
                yield recommend_params_event

            # 过滤 executor，storage 参数
            missing_tool_args = [
                item
                for item in missing_tool_args
                if item not in ['executor', 'storage']
            ]
            self.recommend_params_schema_agent.output_schema = create_tool_args_schema(
                missing_tool_args, current_function_declaration
            )
            async for (
                recommend_params_schema_event
            ) in self.recommend_params_schema_agent.run_async(ctx):
                yield recommend_params_schema_event

            recommend_params = ctx.session.state['recommend_params']
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
