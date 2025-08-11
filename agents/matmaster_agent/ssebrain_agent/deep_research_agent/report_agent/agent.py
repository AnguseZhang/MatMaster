from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

from .prompt import instructions_v2_zh, instructions_v2_en


def save_response(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
    """save llm response to file"""
    if llm_response.content.parts[0].text:
        original_text = llm_response.content.parts[0].text
        #print(f"response:{original_text}")
        # Disabled file output to avoid generating unwanted files
        # with open("response.md", "w", encoding="utf-8") as f:
        #     f.write(f"response: {original_text}")


def init_report_agent(llm_config):
    """Initialize the researcher agent with the given configuration."""
    # Select the model based on the configuration
    selected_model = llm_config.gemini_2_5_pro

    root_agent = LlmAgent(
        name="report_agent",
        model=selected_model,
        instruction=instructions_v2_en,
        description="Merge results from multiple paper agents in parallel and generate a deep research literature report.",
        output_key="deep_research_report",
        after_model_callback=save_response
    )
    return root_agent
