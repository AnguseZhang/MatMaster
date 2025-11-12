from typing import Optional
from urllib.parse import urlparse

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types


def validate_visualization_url(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    after_model_callback to validate visualization URLs.
    Ensures that only URLs with .png extension are processed.
    """
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None

    function_call_parts = [
        part for part in llm_response.content.parts if part.function_call
    ]

    if not function_call_parts:
        return None

    # Process each function call
    modified_parts = []
    has_modifications = False

    for part in function_call_parts:
        function_call = part.function_call
        # Check if this is a visualization function call with URL arguments
        if function_call.name == 'visualize_data' and function_call.args:
            args = function_call.args
            if 'output_url' in args:
                url = args['output_url']
                if not _is_valid_png_url(url):
                    # If URL is not valid PNG, remove the function call
                    has_modifications = True
                    continue  # Skip this function call

        # Keep the original part if no modifications
        modified_parts.append(part)

    # Return modified response if changes were made
    if has_modifications:
        new_content = types.Content(
            parts=modified_parts, role=llm_response.content.role
        )
        modified_response = LlmResponse(
            content=new_content,
        )
        return modified_response

    return None


def _is_valid_png_url(url: str) -> bool:
    """
    Check if the URL has a valid PNG extension.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL ends with .png (case insensitive), False otherwise
    """
    if not url:
        return False
        
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    
    # Check if the path ends with .png
    return path.endswith('.png')