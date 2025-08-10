from datetime import datetime
from typing import Optional, Union

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from .tools.database import DatabaseManager
from ..constant import FRONTEND_STATE_KEY


# before_agent_callback
def init_prepare_state_before_agent(llm_config):
    """prepare state before agent runs"""

    def prepare_state_before_agent(callback_context: CallbackContext) -> Union[types.Content, None]:
        callback_context.state[FRONTEND_STATE_KEY] = callback_context.state.get(FRONTEND_STATE_KEY, {})
        callback_context.state[FRONTEND_STATE_KEY]['biz'] = callback_context.state[FRONTEND_STATE_KEY].get('biz', {})

        callback_context.state['target_language'] = "zh"
        callback_context.state['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        callback_context.state['db_name'] = llm_config.solid_electrolyte
        db_manager = DatabaseManager(llm_config.solid_electrolyte)
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

    return prepare_state_before_agent


# before_model_callback
async def before_model(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    return


# after_model_callback
async def after_model(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    return


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
