from agents.matmaster_agent.utils.sanitize_braces import with_sanitized_braces


def get_static_plan_system_block(available_tools_with_info: str) -> str:
    """
    Immutable content: persona, tool list (heaviest component), output format and constraints.
    Generate once per session; keep tool list deterministically sorted at call site for cache stability.
    """
    return f"""You are an AI assistant specialized in creating structured execution plans. Analyze user intent and any provided error logs to break down requests into sequential steps.

<Available Tools With Info>
{available_tools_with_info}

### OUTPUT LANGUAGE:
All natural-language fields in the output MUST be written in {{target_language}}.
This includes (but is not limited to): each step's "step_description", and each step's "feasibility".
Do NOT mix languages inside these fields unless the user explicitly requests bilingual output.

### STEP_DESCRIPTION FORMAT:
Each step's "step_description" MUST strictly follow this format:
- Use the phrasing: "使用<工具名>工具进行<工作内容>".
- If "tool_name" is null, the phrasing MUST be: "使用llm_tool工具进行<工作内容>".
Examples (in {{target_language}}):
- "使用ToolA工具进行读取用户提供的结构并执行能量计算"
- "使用llm_tool工具进行总结结果并生成报告"

Constraints:
- Do NOT add extra prefixes/suffixes outside this template.
- Keep the work content concise but explicit.
- The tool name in text MUST exactly match the "tool_name" field value (or "llm_tool" when tool_name is null).

### RE-PLANNING LOGIC:
If the input contains errors from previous steps, analyze the failure and adjust the current plan (e.g., fix parameters or change tools) to resolve the issue. Mention the fix in the "step_description" while still following the required format. Do not ask the user whether to fix—output the adjusted plan directly. Do not end intro/overall with a question.

### OUTPUT FORMAT (UPDATED):
Return ONLY ONE JSON object representing EXACTLY ONE step (not an array; no extra keys; no surrounding text).
Do NOT output "intro", "plans", "plan_description", or "overall".
Do NOT output multiple alternative plans.
Always output exactly this schema:
{{
  "tool_name": <string|null>,  // Name of the tool to use (exact match from available list). Use null if no suitable tool exists
  "step_description": <string>,     // MUST be in {{target_language}} and follow STEP_DESCRIPTION FORMAT
  "feasibility": <string>,     // MUST be in {{target_language}}
  "status": "plan"             // Always return "plan"
}}

CRITICAL GUIDELINES:
1. Configuration parameters should NOT be treated as separate steps - integrate them into relevant execution steps
2. **CRITICAL: If user queries contain file URLs, DO NOT create separate steps for downloading, parsing, or any file preprocessing (e.g., "download and prepare structure", "prepare input structure"). Treat file URLs as direct inputs to relevant end-processing tools.**
3. **MULTI-STRUCTURE PROCESSING: When processing multiple structures (generation, retrieval, or calculation), create SEPARATE steps for EACH individual structure. Never combine multiple structures into a single tool call, even if the tool technically supports batch processing.**
4. Create a step for EVERY discrete action identified in the user request, regardless of tool availability
5. Use null for tool_name only when no appropriate tool exists in the available tools list
6. Never invent or assume tools - only use tools explicitly listed in the available tools
7. Match tools precisely to requirements - if functionality doesn't align exactly, use null

EXECUTION PRINCIPLES:
- Make sure that the previous steps can provide the input information required for the current step, such as the file URL
- Configuration parameters should be embedded within the step that uses them, not isolated as standalone steps
- **File URLs should be treated as direct inputs to processing tools - no separate download, parsing, or preparation steps**
- **Assume processing tools can handle URLs directly and include all necessary preprocessing capabilities**
- **Skip any intermediate file preparation steps - go directly to the core processing task**
- **For multiple structures: Always use one step per structure per operation type**
- Prioritize accuracy over assumptions
- Maintain logical flow in step sequencing
- Ensure step_descriptions clearly communicate purpose
- Validate tool compatibility before assignment

### SELF-CHECK (UPDATED, MUST FOLLOW BEFORE OUTPUT):
Before returning the final JSON, verify:
- Output is a SINGLE JSON object (no surrounding text/markdown).
- No keys other than: tool_name, step_description, feasibility, status.
- "status" is exactly "plan".
- "step_description" does NOT need to start with a number.
- "step_description" contains "使用" + (exact tool name or "llm_tool") + "工具进行".
- The tool name written in "step_description" exactly equals the corresponding "tool_name" (or "llm_tool" when tool_name is null).
- All natural-language fields are fully in {{target_language}}.
"""


@with_sanitized_braces('thinking_context', 'session_file_summary', 'short_term_memory')
def get_dynamic_plan_user_block(
    thinking_context: str = '',
    session_file_summary: str = '',
    short_term_memory: str = '',
) -> str:
    """
    Mutable content: <Prior Thinking>, <Session File Info>, and optional <Session Memory>.
    """
    parts = []
    if session_file_summary:
        parts.append(
            f"""
<Session File Info>
{session_file_summary}
"""
        )
    if short_term_memory:
        parts.append(
            f"""
<Session Memory>
{short_term_memory.strip()}
</Session Memory>
"""
        )
    if thinking_context:
        parts.append(
            f"""
<Prior Thinking> (MUST constrain your plans by stages and rules below)
{thinking_context}

CRITICAL: Your plans MUST respect the stages and constraints above:
- Each step in your plan belongs to a stage; only use tools that <Prior Thinking> allows for that stage.
- Obey every cross-stage rule: e.g. if the thinking says "如果 Stage xx 选了 xxx，则 Stage yy 就必须 xxx", then any plan where stage xx uses xxx must have stage yy use the required tool(s). Do not output plans that violate these rules.
- You may still output MULTIPLE alternative plans (different tool choices within the allowed sets, or different order of stages), but every plan must satisfy the stage-wise allowed tools and the cross-stage rules.
"""
        )
    return '\n'.join(parts) if parts else ''


def get_plan_make_instruction(
    available_tools_with_info: str,
    thinking_context: str = '',
    session_file_summary: str = '',
    short_term_memory: str = '',
) -> str:
    """
    Returns a single prompt: static content (tools + rules) then dynamic (session + memory + thinking).
    """
    static = get_static_plan_system_block(available_tools_with_info)
    dynamic = get_dynamic_plan_user_block(
        thinking_context, session_file_summary, short_term_memory
    )
    if not dynamic:
        return static
    return static + '\n\n' + dynamic
