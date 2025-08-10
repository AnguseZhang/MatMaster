import json
import os

from google.genai import types
from typing import Optional

from google.adk.agents import LlmAgent

from .prompt import instructions_v2_zh, instructions_v2_en
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

from ...tools.database import DatabaseManager
from ...tools.io import save_llm_request

# 这个函数是一个回调函数，用于在模型调用后保存响应内容到文件
def save_response(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
    if llm_response.content.parts[0].text:
        original_text = llm_response.content.parts[0].text
        print(f"response:{original_text}")
        with open("raw-response.md", "w", encoding="utf-8") as f:
            f.write(f"response: {original_text}")

# Create a function to update the invoke message with the agent name
def create_update_invoke_message_with_agent_name(agent_name: str):
    def update_invoke_message_with_agent_name(
            callback_context: CallbackContext,
            llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        
        paper_list = callback_context.state['paper_list']
        # 使用传入的 agent_name 参数
        paper_url = paper_list[agent_name]

        # mock get paper content and picture
        # message, picture_mapping = mock_get_paper_content_and_picture(paper_url)

        # query paper content and picture from database
        db_manager = DatabaseManager('solid_electrolyte_db')
        fetch_paper_content = db_manager.init_fetch_paper_content()
        paper_content = fetch_paper_content(paper_url)
        message = paper_content.get('main_txt', '')
        picture_mapping = paper_content.get('figures', [])

        contents = []
        try:
            text = llm_request.contents[-1].parts[0].text
            function_response = llm_request.contents[-1].parts[0].function_response
            if text == "For context:" and function_response is None:
                contents.append(types.Content(role="user", parts=[types.Part(text=f"raw paper content:{message}")]))
                if picture_mapping is not None:
                    contents.append(types.Content(role="user", parts=[types.Part(text=f"picture_mapping:{picture_mapping}")]))
                llm_request.contents = llm_request.contents + contents
        except:
            print(llm_request.contents[-1].role, llm_request.contents[-1].parts[0])
        return None  # 原函数没有返回值，保持一致

    return update_invoke_message_with_agent_name

# Initialize the researcher agent with the given configuration
def init_paper_agent(llm_config, name, run_id):
    """Initialize the researcher agent with the given configuration."""
    # Select the model based on the configuration
    selected_model = llm_config.gpt_4o

    paper_agent = LlmAgent(
        name=f"paper_agent_{name}",
        instruction=instructions_v2_zh,
        model=selected_model,
        description="Paper agent that read one particular paper to extract information about user's query",
        tools=[],
        output_key=f"{name}_finding",
        before_model_callback=create_update_invoke_message_with_agent_name(name),
        after_model_callback=save_response
    )

    return paper_agent


# # Example usage
# llm_config = create_default_config()
# root_agent = init_paper_agent(llm_config)
