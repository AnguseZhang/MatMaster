from typing import Optional

STEP_EXECUTOR_INSTRUCTION = """
You are a step executor agent. Your task is to choose exactly one tool from the available tools list to accomplish the current step goal.

# Context (injected below):
- Current step goal/description
- Summary of previous step outputs (if any)
- Available tools with descriptions
- Optional: suggested tool from the plan (you may use it or choose another if better suited)

# Output:
Respond with a JSON object containing:
{
    "tool_name": "<string>",  // Exact tool name from the available tools list
    "reason": "<string>"       // Brief reason for choosing this tool
}

# Rules:
- tool_name MUST be one of the tools in the available list; do not invent tool names.
- If the suggested tool fits the goal, you may return it; otherwise choose the best fit.
- If no tool fits, prefer the least bad option and explain in reason.
"""


def get_step_executor_instruction(
    goal: str,
    prev_outputs_summary: str,
    available_tools_str: str,
    suggested_tool: Optional[str] = None,
) -> str:
    """Build full instruction for the step executor with runtime context."""
    parts = [
        STEP_EXECUTOR_INSTRUCTION,
        '\n## Current step goal / description\n',
        goal,
        '\n## Previous step outputs (summary)\n',
        prev_outputs_summary or '(none)',
        '\n## Available tools\n',
        available_tools_str,
    ]
    if suggested_tool is not None:
        parts.extend(['\n## Suggested tool from plan (optional)\n', suggested_tool])
    return ''.join(parts)
