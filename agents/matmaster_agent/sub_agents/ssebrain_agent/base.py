import logging
import os
import traceback
from functools import wraps
from typing import AsyncGenerator, Union, override

from dp.agent.adapter.adk import CalculationMCPTool
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import BeforeToolCallback
from google.adk.events import Event, EventActions
from google.adk.tools import BaseTool, ToolContext
from google.genai import types
from mcp.types import CallToolResult, TextContent

from agents.matmaster_agent.constant import FRONTEND_STATE_KEY, TMP_FRONTEND_STATE_KEY
from agents.matmaster_agent.sub_agents.ssebrain_agent.constant import (
    LOADING_DESC,
    LOADING_END,
    LOADING_START,
    LOADING_STATE_KEY,
    LOADING_TITLE,
    Transfer2Agent,
)

logger = logging.getLogger(__name__)


async def default_before_tool_callback(tool, args, tool_context):
    return


class CalculationLlmAgent(LlmAgent):
    """An LLM agent specialized for calculation tasks with built-in error handling and project ID management.

    Extends the base LlmAgent with additional features:
    - Automatic error handling for tool calls
    - Project ID retrieval before tool execution
    - OpikTracer integration for comprehensive operation tracing

    Note: User-provided callbacks will execute before the built-in OpikTracer callbacks.

    Attributes:
        Inherits all attributes from LlmAgent.
    """

    def __init__(
        self,
        model,
        name,
        instruction,
        description='',
        sub_agents=None,
        global_instruction='',
        tools=None,
        output_key=None,
        before_agent_callback=None,
        before_model_callback=None,
        before_tool_callback=default_before_tool_callback,
        after_tool_callback=None,
        after_model_callback=None,
        after_agent_callback=None,
    ):
        """Initialize a CalculationLlmAgent with enhanced tool call capabilities.

        Args:
            model: The language model instance to be used by the agent
            name: Unique identifier for the agent
            instruction: Primary instruction guiding the agent's behavior
            description: Optional detailed description of the agent (default: '')
            sub_agents: List of subordinate agents (default: None)
            global_instruction: Instruction applied across all agent operations (default: '')
            tools: Tools available to the agent (default: None)
            output_key: Key for identifying the agent's output (default: None)
            before_agent_callback: Callback executed before agent runs (default: None)
            before_model_callback: Callback executed before model inference (default: None)
            before_tool_callback: Callback executed before tool execution
                                (default: default_before_tool_callback)
            after_tool_callback: Callback executed after tool execution (default: None)
            after_model_callback: Callback executed after model inference (default: None)
            after_agent_callback: Callback executed after agent completes (default: None)

        Implementation Notes:
            1. Wraps the before_tool_callback with:
               - Error handling (catch_tool_call_error)
               - Project ID retrieval (get_ak_projectId)
            2. Maintains callback execution order: user callbacks → OpikTracer callbacks
            3. Designed specifically for calculation-intensive MCP workflows
        """

        # Todo: support List[before_tool_callback]
        before_tool_callback = catch_tool_call_error(
            get_ak_projectId(before_tool_callback)
        )

        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction,
            global_instruction=global_instruction,
            sub_agents=sub_agents or [],
            tools=tools or [],
            output_key=output_key,
            before_agent_callback=before_agent_callback,
            before_model_callback=before_model_callback,
            before_tool_callback=before_tool_callback,
            after_tool_callback=after_tool_callback,
            after_model_callback=after_model_callback,
            after_agent_callback=after_agent_callback,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            async for event in super()._run_async_impl(ctx):
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].function_call
                ):
                    loading_title_msg = (
                        f"正在调用 {event.content.parts[0].function_call.name}..."
                    )
                    loading_desc_msg = '结果生成中，请稍等片刻...'
                    logger.info(loading_title_msg)
                    yield Event(
                        author=self.name,
                        actions=EventActions(
                            state_delta={
                                TMP_FRONTEND_STATE_KEY: {
                                    LOADING_STATE_KEY: LOADING_START,
                                    LOADING_TITLE: loading_title_msg,
                                    LOADING_DESC: loading_desc_msg,
                                }
                            }
                        ),
                    )
                elif (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].function_response
                ):
                    logger.info(
                        f"{event.content.parts[0].function_response.name} 调用结束"
                    )
                    yield Event(
                        author=self.name,
                        actions=EventActions(
                            state_delta={
                                TMP_FRONTEND_STATE_KEY: {LOADING_STATE_KEY: LOADING_END}
                            }
                        ),
                    )
                yield event
        except BaseExceptionGroup as err:
            # 构建更详细的错误信息
            error_details = [
                f"Exception Group caught with {len(err.exceptions)} exceptions:",
                f"Message: {str(err)}",
                '\nIndividual exceptions:',
            ]

            # 添加每个子异常的详细信息
            for i, exc in enumerate(err.exceptions, 1):
                error_details.append(f"\nException #{i}:")
                error_details.append(f"Type: {type(exc).__name__}")
                error_details.append(f"Message: {str(exc)}")
                error_details.append(
                    f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}"
                )

            # 将所有信息合并为一个字符串
            detailed_error = '\n'.join(error_details)

            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(
                    parts=[types.Part(text=detailed_error)], role='system'
                ),
            )

            async for error_event in ctx.agent.parent_agent.run_async(ctx):
                yield error_event


# 总应该在最后
def catch_tool_call_error(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        try:
            return await tool.run_async(args=args, tool_context=tool_context)
        except Exception as e:
            return {
                'error': str(e),
                'error_type': type(e).__name__,
            }

    return wrapper


def get_ak_projectId(func: BeforeToolCallback) -> BeforeToolCallback:
    @wraps(func)
    async def wrapper(
        tool: BaseTool, args: dict, tool_context: ToolContext
    ) -> Union[dict, None, CallToolResult]:
        # 两步操作：
        # 1. 调用被装饰的 before_tool_callback；
        # 2. 如果调用的 before_tool_callback 有返回值，以这个为准
        if (before_tool_result := await func(tool, args, tool_context)) is not None:
            return before_tool_result

        # 如果 tool 为 Transfer2Agent，不做 ak 和 project_id 设置/校验
        if tool.name == Transfer2Agent:
            return None

        # 如果 tool 不是 CalculationMCPTool，不应该调用这个 callback
        if not isinstance(tool, CalculationMCPTool):
            error_msg = '{"msg": "Current tool does not have <storage>"}'
            return CallToolResult(
                content=[TextContent(type='text', text=error_msg)], isError=True
            )

        # 获取 access_key
        access_key = tool_context.state[FRONTEND_STATE_KEY]['biz'].get('ak', None)
        if access_key is None:
            access_key = os.getenv('BOHRIUM_ACCESS_KEY', None)
        if access_key is not None:
            tool.storage['plugin']['access_key'] = access_key
        else:
            error_msg = '{"msg": "AccessKey was not provided"}'
            return CallToolResult(
                content=[TextContent(type='text', text=error_msg)], isError=True
            )

        # 获取 project_id
        project_id = tool_context.state[FRONTEND_STATE_KEY]['biz'].get(
            'projectId', None
        )
        if project_id is None:
            project_id = os.getenv('BOHRIUM_PROJECT_ID', None)
        if project_id is not None:
            try:
                tool.storage['plugin']['project_id'] = int(project_id)
            except ValueError:
                error_msg = '{"msg": "ProjectId [%s] is invalid"}' % project_id
                return CallToolResult(
                    content=[TextContent(type='text', text=error_msg)], isError=True
                )
        else:
            error_msg = '{"msg": "ProjectId was not provided. Please retry when select the project."}'
            return CallToolResult(
                content=[TextContent(type='text', text=error_msg)], isError=True
            )

    return wrapper
