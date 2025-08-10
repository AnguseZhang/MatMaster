from datetime import datetime
from typing import Optional, Union, Callable

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from .tools.database import DatabaseManager
from ..constant import FRONTEND_STATE_KEY


# 回调组合器函数
def combine_before_model_callbacks(*callbacks) -> Callable:
    """组合多个 before_model_callback 函数为一个回调链
    
    该函数解决了 ADK 框架不直接支持回调列表的问题，通过创建一个组合回调函数，
    按顺序执行多个回调，直到其中一个返回非 None 值或全部执行完毕。
    
    Args:
        *callbacks: 可变数量的回调函数，每个函数应有签名：
                   async def callback(CallbackContext, LlmRequest) -> Optional[LlmResponse]
                   
    Returns:
        Callable: 组合后的回调函数，可直接用于 before_model_callback 参数
        
    Example:
        >>> combined = combine_before_model_callbacks(rate_limit_callback, custom_callback)
        >>> agent = LlmAgent(..., before_model_callback=combined)
    """
    async def combined_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        """按顺序执行所有回调函数，如果任一返回非None值则停止并返回该值"""
        for callback in callbacks:
            if callback is not None:
                result = await callback(callback_context, llm_request)
                if result is not None:
                    return result
        return None
    return combined_callback


def combine_after_model_callbacks(*callbacks) -> Callable:
    """组合多个 after_model_callback 函数为一个回调链
    
    与 before_model_callbacks 类似，但用于模型推理后的回调处理。
    
    Args:
        *callbacks: 可变数量的回调函数，每个函数应有签名：
                   async def callback(CallbackContext, LlmResponse) -> Optional[LlmResponse]
                   
    Returns:
        Callable: 组合后的回调函数，可直接用于 after_model_callback 参数
    """
    async def combined_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
        """按顺序执行所有回调函数，如果任一返回非None值则停止并返回该值"""
        for callback in callbacks:
            if callback is not None:
                result = await callback(callback_context, llm_response)
                if result is not None:
                    return result
        return None
    return combined_callback


# before_agent_callback
def init_chembrain_before_agent(llm_config):
    """prepare state before agent runs"""

    def chembrain_before_agent(callback_context: CallbackContext) -> Union[types.Content, None]:
        callback_context.state[FRONTEND_STATE_KEY] = callback_context.state.get(FRONTEND_STATE_KEY, {})
        callback_context.state[FRONTEND_STATE_KEY]['biz'] = callback_context.state[FRONTEND_STATE_KEY].get('biz', {})

        callback_context.state['target_language'] = 'zh'  # 默认语言
        callback_context.state['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        callback_context.state['db_name'] = 'polymer_db' # 使用默认数据库
        db_manager = DatabaseManager('polymer_db')
        callback_context.state['available_tables'] = db_manager.table_schema

        prompt = ""
        callback_context.state['artifacts'] = callback_context.state.get("artifacts", [])
        if callback_context.user_content and callback_context.user_content.parts:
            for part in callback_context.user_content.parts:
                if part.text:
                    prompt += part.text
                elif part.inline_data:
                    callback_context.state['artifacts'].append(
                        {
                            "artifact_type": "inline_data",
                            "name": part.inline_data.display_name,
                            "mime_type": part.inline_data.mime_type,
                            "data": part.inline_data.data,
                        })
                elif part.file_data:
                    callback_context.state['artifacts'].append(
                        {
                            "artifact_type": "file_data",
                            "file_url": part.file_data.file_uri,
                            "mime_type": part.file_data.mime_type,
                            "name": part.file_data.display_name,
                        }
                    )

    return chembrain_before_agent


# before_model_callback
async def chembrain_before_model(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    # 这个函数目前不做任何处理，保留用于扩展
    _ = callback_context, llm_request  # 避免未使用参数警告
    return None


# after_model_callback
async def chembrain_after_model(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    # 这个函数目前不做任何处理，保留用于扩展
    _ = callback_context, llm_response  # 避免未使用参数警告
    return None


def enforce_single_tool_call(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    after_model_callback to ensure only one tool call is processed per turn.
    Stores remaining calls in state['pending_tool_calls'].
    """
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None  # No response or no parts, proceed normally

    function_call_parts: list[types.Part] = [
        part for part in llm_response.content.parts if part.function_call
    ]

    if len(function_call_parts) > 1:
        print(f"Intercepted {len(function_call_parts)} tool calls. Processing only the first.")

        first_call_part = function_call_parts[0]
        remaining_calls = [
            part.function_call for part in function_call_parts[1:]
        ]
        callback_context.state['pending_tool_calls'] = remaining_calls
        print(f"Stored {len(remaining_calls)} pending calls in state.")

        # Create a new response with only the first call
        new_content = types.Content(
            parts=[first_call_part],
            role=llm_response.content.role  # Keep original role
        )
        modified_response = LlmResponse(
            content=new_content,
        )
        return modified_response

    return None
