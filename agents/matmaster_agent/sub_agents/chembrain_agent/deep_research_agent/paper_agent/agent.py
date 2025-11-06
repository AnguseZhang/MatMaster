import json
import os
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

from ...tools.database import DatabaseManager
from ...tools.io import save_llm_request
from .prompt import instructions_v2_en


def create_save_response(agent_name: str):
    def save_response(
        callback_context: CallbackContext, llm_response: LlmResponse
    ) -> None:
        paper_list = callback_context.state['paper_list']
        # 使用传入的 agent_name 参数
        paper_url = paper_list[agent_name]

        if not callback_context.state.get('paper_response', None):
            callback_context.state['paper_response'] = {}

        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            callback_context.state['paper_response'][paper_url] = original_text
            # print(f"response:{original_text}")
            # with open("raw-response.md", "w", encoding="utf-8") as f:
            #     f.write(f"response: {original_text}")
        return None

    return save_response


def mock_construct_messages(paper_url):
    file_path = paper_url
    with open(file_path, encoding='utf-8') as file:
        raw_content = json.load(file)
    raw_paper_content = raw_content['text']
    paper_str = json.dumps(raw_paper_content, ensure_ascii=False, default=str)
    return paper_str


def mock_construct_picture_mapping(picture_url):
    file_path = picture_url
    with open(file_path, encoding='utf-8') as file:
        raw_content = json.load(file)
    picture_mapping_str = json.dumps(raw_content, ensure_ascii=False, default=str)
    return picture_mapping_str


def mock_get_paper_content_and_picture(paper_url):
    dir_part = os.path.dirname(paper_url)
    picture_url = os.path.join(dir_part, 'figure_mappings.json')
    message = mock_construct_messages(paper_url)
    picture_mapping = mock_construct_picture_mapping(picture_url)
    return message, picture_mapping


def create_update_invoke_message_with_agent_name(agent_name: str):
    async def update_invoke_message_with_agent_name(
        callback_context: CallbackContext, llm_request: LlmRequest
    ) -> Optional[LlmResponse]:
        paper_list = callback_context.state['paper_list']
        # 使用传入的 agent_name 参数
        paper_url = paper_list[agent_name]

        # mock get paper content and picture
        # message, picture_mapping = mock_get_paper_content_and_picture(paper_url)

        # query paper content and picture from database
        db_manager = DatabaseManager(callback_context.state['db_name'])
        await db_manager.async_init()  # Initialize DatabaseManager asynchronously
        fetch_paper_content = db_manager.init_fetch_paper_content()
        print(f"Fetching paper content from database... : {paper_url}")
        paper_content = await fetch_paper_content(paper_url)
        message = paper_content.get('main_txt', '')
        picture_mapping = paper_content.get('figures', [])

        contents = []
        try:
            text = llm_request.contents[-1].parts[0].text
            function_response = llm_request.contents[-1].parts[0].function_response
            if text == 'For context:' and function_response is None:
                contents.append(
                    types.Content(
                        role='user',
                        parts=[types.Part(text=f"raw paper content:{message}")],
                    )
                )
                if picture_mapping is not None:
                    contents.append(
                        types.Content(
                            role='user',
                            parts=[
                                types.Part(text=f"picture_mapping:{picture_mapping}")
                            ],
                        )
                    )
                llm_request.contents = llm_request.contents + contents

            output_file = 'llm_contents_reader.json'
            save_llm_request(llm_request, output_file)
        except BaseException:
            print(llm_request.contents[-1].role, llm_request.contents[-1].parts[0])
        return None  # 原函数没有返回值，保持一致

    return update_invoke_message_with_agent_name


def init_paper_agent(config, name, run_id):
    """Initialize the researcher agent with the given configuration."""
    # Select the model based on the configuration
    selected_model = config.gemini_2_5_pro
    # selected_model = config.gpt_4o

    paper_agent = LlmAgent(
        name=f"poly_paper_agent_{name}",
        instruction=instructions_v2_en,
        model=selected_model,
        description="Paper agent that read one particular paper to extract information about user's query",
        tools=[],
        output_key=f"{name}_finding",
        before_model_callback=create_update_invoke_message_with_agent_name(name),
        after_model_callback=create_save_response(name),
    )

    return paper_agent


# # Example usage
# llm_config = create_default_config()
# root_agent = init_paper_agent(llm_config)
