def gen_recommend_params_agent_instruction():
    return """
Convert the recommended parameters into a user-friendly format for a tool invocation.

Critical Instructions:
- The output language must be {target_language}.
- Present the information in a clear, readable style, such as a list or natural paragraphs.
- Do not end with any question or prompt for user action.
"""
