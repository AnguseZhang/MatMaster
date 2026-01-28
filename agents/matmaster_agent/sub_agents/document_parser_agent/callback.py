from typing import Optional
from urllib.parse import urlparse

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types


async def validate_document_url(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    after_model_callback to validate and correct document URLs before tool execution.
    Ensures PDF URLs are routed to document parser and web URLs to web parser.
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
        if (
            function_call.name
            in ['extract_material_data_from_pdf', 'extract_info_from_webpage']
            and function_call.args
        ):
            # Check if arguments contain URL(s)
            args = function_call.args
            if 'url' in args:
                corrected_args = args.copy()
                url = args['url']

                # Validate and correct the tool call based on URL
                corrected_call = _correct_tool_call(function_call.name, url)
                if corrected_call != function_call.name:
                    # Create a new function call with corrected tool name
                    new_function_call = types.FunctionCall(
                        name=corrected_call, args=corrected_args
                    )
                    modified_parts.append(types.Part(function_call=new_function_call))
                    has_modifications = True
                    continue

            elif 'urls' in args:
                corrected_args = args.copy()
                urls = args['urls']
                if isinstance(urls, list) and urls:
                    # For multiple URLs, check if correction is needed
                    url = urls[0] if urls else ''
                    corrected_call = _correct_tool_call(function_call.name, url)
                    if corrected_call != function_call.name:
                        new_function_call = types.FunctionCall(
                            name=corrected_call, args=corrected_args
                        )
                        modified_parts.append(
                            types.Part(function_call=new_function_call)
                        )
                        has_modifications = True
                        continue

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


def _correct_tool_call(current_tool: str, url: str) -> str:
    """
    Determine the correct tool based on URL characteristics.

    Args:
        current_tool: Current tool name
        url: URL to analyze

    Returns:
        Corrected tool name
    """
    if not url:
        return current_tool

    # Parse URL to check its characteristics
    parsed_url = urlparse(url)

    # Check if it's clearly a web URL (no file extension or html-based)
    if parsed_url.scheme in ['http', 'https']:
        path = parsed_url.path.lower()

        # If it has a PDF extension, it should use document parser
        if path.endswith('.pdf'):
            return 'extract_material_data_from_pdf'

        # If it doesn't have a file extension or has HTML-related patterns, use web parser
        if '.' not in path or path.endswith(
            ('.html', '.htm', '.asp', '.aspx', '.jsp', '.php')
        ):
            return 'extract_info_from_webpage'

        # For URLs without clear extensions, check if it looks like a web page
        # (this is a heuristic, could be refined)
        if any(keyword in url.lower() for keyword in ['www', 'http', 'web', 'site']):
            return 'extract_info_from_webpage'

    # Default to current tool if we can't determine
    return current_tool
