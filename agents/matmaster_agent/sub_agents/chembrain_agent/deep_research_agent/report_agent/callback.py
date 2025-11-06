from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

from agents.matmaster_agent.sub_agents.chembrain_agent.tools.io import save_llm_request


def update_invoke_message(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """save llm request to file"""
    output_file = 'llm_contents_report.json'
    save_llm_request(llm_request, output_file)


def save_response(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
    """save llm response to file"""
    if llm_response.content.parts[0].text:
        original_text = llm_response.content.parts[0].text
        callback_context.state['report_response'] = original_text
        # print(f"response:{original_text}")
        # with open("response.md", "w", encoding="utf-8") as f:
        #     f.write(f"response: {original_text}")
    return
