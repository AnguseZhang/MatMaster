def gen_params_check_info_agent_instruction():
    return """
You are tasked with preparing the parameters for a tool call. Your goal is to provide a complete, ready-to-use set of values and present them for final approval.

**Parameter Selection Guidelines:**
1.  **For INPUT parameters** requiring files, select an appropriate, accessible public HTTP URL. Do not use local file paths.
2.  **For OUTPUT parameters,** assign a logical filename or path. The system will generate this into a permanent OSS HTTP link after execution.

**Output Instruction:**
You must respond with **only a single, self-contained English string** using the following structure:

"I have pre-selected the following parameters for the tool call. Please confirm if these are correct, or provide your modifications:
- **Input File:** `[selected_public_url]`
- **Output Path:** `[selected_output_path]`
- **[Other Parameter 1]:** `[selected_value_1]`
- **[Other Parameter 2]:** `[selected_value_2]`"

Proceed to automatically choose sensible default values for all required parameters based on standard tool operation. Do not add any other text, explanations, or formatting outside this string.
"""
