"""
Thinking Agent Prompt - Caching Protocol (Static vs Dynamic) and Explicit CoT.

Static content (persona, tools, rules) is separated from dynamic content (session, query)
so that prefix caching (e.g. Anthropic cache_control) can maximize hit rates.
"""

from typing import TypedDict


class ThinkingPromptBlocks(TypedDict):
    """Separated blocks for system (static) and user (dynamic) message assembly."""

    system: str
    user: str


def get_static_system_block(available_tools_with_info: str) -> str:
    """
    Immutable content: persona, thinking protocol, constraints, tool list.
    Generate once per session; keep tools deterministically sorted at call site for cache stability.
    """
    return f"""You are the Planning Engine. Your goal is to design a rigid, executable workflow based on the available tools.
You must follow the Structured Reasoning Protocol below and output your reasoning inside the specified XML tags.

<thinking_protocol>
    <phase_1_analysis>
        Deconstruct user intent into Input Data (Source) and Desired Output (Target).
        Identify key entities (SMILES, chemical formulas, files).
        Determine if the user wants *Learning* (docs/tutorials) or *Execution* (simulations).
    </phase_1_analysis>

    <phase_2_drafting>
        Propose a preliminary tool sequence from the Available Tools list.
        Select tools based STRICTLY on their "What it does" and "Prerequisites / Inputs" descriptions.
    </phase_2_drafting>

    <phase_3_simulation_and_verification>
        CRITICAL — Mental Simulation (Dry Run): Before finalizing the plan, you MUST perform a type-checking simulation.

        1. **Virtual File System Check**: For every proposed step, verify whether the *specific* input file type required by that step exists in the *current* virtual file system at that point in the sequence.
           - Example: Step 3 requires `slab_structure.cif`. After Step 1 and Step 2, does the virtual state contain a slab/structure file, or only a bulk CIF / chemical formula?
           - Output explicitly: "Step N requires Input Type A. Current State provides Type B. [PASS if A matches B; otherwise: Mismatch -> Insert Converter Tool.]"

        2. **Mandatory Dependency Constraints** (you MUST obey these):
           - If a tool requires a **Surface/Slab** (e.g., slab structure, surface model) and you only have a **Bulk** structure or a **chemical formula**, you MUST insert the `surface_cutting` or equivalent tool first (to generate the slab from bulk), or insert `structure_generation` first if you only have a formula.
           - If a tool requires a **structure file** (e.g., CIF, VASP) and you only have **SMILES**, you MUST insert a step that produces structure from SMILES (e.g. `smiles_to_structure` / build_molecule_structures_from_smiles) before that step.
           - If a tool requires a **bulk structure** and you only have a formula or composition, you MUST insert a `structure_generation` (or crystal structure generation) step first.

        3. **Output Format for Each Step** (inside your <simulation> tag):
           For each step N, state exactly:
           - "Step N requires Input Type A. Current State provides Type B. [PASS / FAIL]. [If FAIL: Insert Converter Tool.]"
           No step may be proposed without its inputs being available (Backward Chaining).
    </phase_3_simulation_and_verification>

    <phase_4_final_plan>
        Output the validated linear sequence of steps.
    </phase_4_final_plan>
</thinking_protocol>

### CONSTRAINTS
- **Grounding**: Use ONLY tools listed in `<Available Tools With Info>`. Do not hallucinate tools.
- **Atomic check**: If a step requires `structure_file` and you only have `SMILES`, you MUST insert a step that produces structure from SMILES.
- **Surface/Slab dependency**: If a tool requires a Surface/Slab (e.g., slab structure, surface model), and you only have a Bulk structure or a chemical formula, you MUST insert the `surface_cutting` or `structure_generation` tool first. Do not propose surface/slab steps without the prerequisite bulk or structure.
- **Language**: Use {{target_language}} for the content within tags.

### FINAL TRIGGER
- This is a planning phase. You verify the plan's validity.
- You MUST end your response with exactly one line: `Revision needed` (to trigger the validation loop). Do not output `READY` here.

### STATIC CONTEXT (Tools)
<Available Tools With Info>
{available_tools_with_info}
</Available Tools With Info>

### OUTPUT FORMAT (use these tags)
<analysis>...</analysis>
<simulation>
Step 1: [Tool Name]. Step 1 requires Input Type [A]. Current State provides [B]. [PASS/FAIL]. [If FAIL: Insert Converter Tool.]
Step 2: [Tool Name]. Step 2 requires Input Type [A]. Current State provides [B]. [PASS/FAIL]. [If FAIL: Insert Converter Tool.]
...
</simulation>
<plan_proposal>
1. [Tool Name]: [Brief Description]
2. ...
</plan_proposal>
Revision needed
"""


def get_dynamic_user_block(
    session_file_summary: str,
    original_query: str,
    expanded_query: str,
    short_term_memory: str = '',
) -> str:
    """
    Mutable content: session state and user-specific query. Changes every turn.
    """
    parts = [
        '### DYNAMIC CONTEXT (User Data — not cacheable from here)',
        '<Session File Info>',
        session_file_summary,
        '</Session File Info>',
    ]
    if short_term_memory:
        parts.extend(['', short_term_memory, ''])
    parts.extend(
        [
            '--- Original user message ---',
            original_query,
            '',
            '--- Task from expansion step ---',
            expanded_query,
        ]
    )
    return '\n'.join(parts)


def get_thinking_instruction(
    available_tools_with_info: str,
    session_file_summary: str,
    original_query: str,
    expanded_query: str,
    short_term_memory: str = '',
) -> str:
    """
    Returns a single prompt with static content first (max cache hit).
    For agents that support system/user split, use get_static_system_block + get_dynamic_user_block instead.
    """
    static = get_static_system_block(available_tools_with_info)
    dynamic = get_dynamic_user_block(
        session_file_summary, original_query, expanded_query, short_term_memory
    )
    return static + '\n\n' + dynamic


def get_thinking_instruction_blocks(
    available_tools_with_info: str,
    session_file_summary: str,
    original_query: str,
    expanded_query: str,
    short_term_memory: str = '',
) -> ThinkingPromptBlocks:
    """
    Returns separated system (static) and user (dynamic) blocks for message assembly.
    Use when the LLM API supports system and user roles (e.g. pass system to system param, user to user param).
    """
    return ThinkingPromptBlocks(
        system=get_static_system_block(available_tools_with_info),
        user=get_dynamic_user_block(
            session_file_summary, original_query, expanded_query, short_term_memory
        ),
    )


# --- Revision (Validator) ---


def get_static_revision_system_block(available_tools_with_info: str) -> str:
    """Immutable content for the plan validator: role, checklist, output format, tools."""
    return f"""You are the Plan Validator. Review the previous reasoning for logical flaws, missing dependencies, or hallucinated tools.

### VALIDATION CHECKLIST
1. **Prerequisites**: Does every step have its inputs satisfied by a *previous* step or *user input*?
2. **Type Match**: Does the final step output what the user actually asked for?
3. **Over-extension**: Did the plan invent steps the user didn't ask for (e.g., running a full simulation when asked for a tutorial)?

### OUTPUT FORMAT
If the plan is VALID:
<validation_log>[Explain what you checked and why it passes]</validation_log>
Verification passed.

If the plan is INVALID:
<validation_log>[Explain the specific error found]</validation_log>
<corrected_plan>[Provide the full corrected plan sequence]</corrected_plan>
[Your reasoning for the correction]
Then:
- If you want one more validation round, end with exactly: Revision needed.
- If your corrected plan is final and no further check is needed, do NOT add "Revision needed." (we will use your corrected plan as final).

### STATIC CONTEXT (Tools)
<Available Tools With Info>
{available_tools_with_info}
</Available Tools With Info>

End with "Verification passed." ONLY if all prerequisites are met. Otherwise, provide the correction and optionally "Revision needed." only when you explicitly want another validation round.
"""


def get_dynamic_revision_user_block(
    session_file_summary: str,
    original_query: str,
    expanded_query: str,
    previous_reasoning: str,
    short_term_memory: str = '',
) -> str:
    """Mutable content for the revision round."""
    parts = [
        '### DYNAMIC CONTEXT',
        '<Session File Info>',
        session_file_summary,
        '</Session File Info>',
    ]
    if short_term_memory:
        parts.extend(['', short_term_memory, ''])
    parts.extend(
        [
            '--- Inputs ---',
            f'User Query: {original_query}',
            f'Expanded Task: {expanded_query}',
            '',
            '--- Previous Reasoning to Validate ---',
            previous_reasoning,
        ]
    )
    return '\n'.join(parts)


def get_thinking_revision_instruction(
    available_tools_with_info: str,
    session_file_summary: str,
    original_query: str,
    expanded_query: str,
    previous_reasoning: str,
    short_term_memory: str = '',
) -> str:
    """
    Returns a single prompt with static content first.
    For system/user split, use get_static_revision_system_block + get_dynamic_revision_user_block.
    """
    static = get_static_revision_system_block(available_tools_with_info)
    dynamic = get_dynamic_revision_user_block(
        session_file_summary,
        original_query,
        expanded_query,
        previous_reasoning,
        short_term_memory,
    )
    return static + '\n\n' + dynamic


def get_thinking_revision_instruction_blocks(
    available_tools_with_info: str,
    session_file_summary: str,
    original_query: str,
    expanded_query: str,
    previous_reasoning: str,
    short_term_memory: str = '',
) -> ThinkingPromptBlocks:
    """Returns separated system and user blocks for the revision/validation round."""
    return ThinkingPromptBlocks(
        system=get_static_revision_system_block(available_tools_with_info),
        user=get_dynamic_revision_user_block(
            session_file_summary,
            original_query,
            expanded_query,
            previous_reasoning,
            short_term_memory,
        ),
    )
