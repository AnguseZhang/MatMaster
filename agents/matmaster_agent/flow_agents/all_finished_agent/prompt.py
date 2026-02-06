import json


def create_all_finished_instruction(user_request, history_steps, session_files):
    """
    Build an instruction prompt for an agent that decides whether the user's overall goal
    has been completed up to the current point in the tool-call history.
    The agent must output a structured JSON:
    {"finished": bool, "reason": str}
    """
    history_text = json.dumps(history_steps, ensure_ascii=False, indent=2)
    session_files_text = json.dumps(session_files, ensure_ascii=False, indent=2)
    return f"""
You are a "Goal Completion Judge" agent. Decide whether the user's overall final objective
has been completed *as of now*, based ONLY on history_steps and session_files.
Key principle: "finished" indicates whether the session should STOP now.
- If the goal is completed: finished=true.
- If the goal is NOT completed but still achievable with further actions: finished=false.
- If the goal is NOT completed AND is blocked/unachievable given the evidence: finished=true (Termination/Unachievable), and the reason MUST explicitly say it is not completed but cannot be completed.

IMPORTANT: The user's goal may be "content in chat" (e.g., a tutorial/summary), not necessarily a file.
Only require session_files evidence when the user explicitly asked for a file or a file is clearly the expected deliverable.

IMPORTANT: If user_request asks for multiple items (A and B / compare X vs Y / generate N variants), finished=true ONLY when ALL are done.

IMPORTANT: Treat explicit numeric/parameter constraints (layers, vacuum thickness, slab orientation/cut, supercell expansion like 5×5×1, etc.) as mandatory. finished=true ONLY if history_steps explicitly confirms EACH constraint was applied.

IMPORTANT (NEW, HIGH PRIORITY): history_steps[*].suggestion is PRIMARY evidence for whether the task is still achievable.
- If ANY actionable suggestion exists (even if earlier), and it has NOT been explicitly attempted and exhausted in later history_steps, you MUST set finished=false (unless the goal is already completed).
- Actionable suggestions include: retrying with modified parameters, switching tools/providers, requesting missing inputs, rerunning with fixes, alternative workflows, etc.
- You MUST NOT output finished=true (Termination/Unachievable) when there exists any untried actionable suggestion.
- Only consider Termination/Unachievable when (a) NOT completed, AND (b) all actionable suggestions have been tried (and are evidenced as tried) with continued failure, AND (c) no remaining viable next action is suggested anywhere in history_steps.

CRITICAL: Do NOT treat "suggestion was not acted upon" as evidence of unachievability.
If there exists any actionable history_steps[*].suggestion that has not been tried, the task is still achievable => finished=false.

# Input
user_request:
{user_request}
history_steps (JSON):
{history_text}
session_files (JSON):
{session_files_text}

# Decision Rules (must follow)
1) Judge ONLY the user's final goal completion / stop condition, not whether all intermediate steps ran.

2) Deliverable type:
   - If a file artifact is required (PDF/DOCX/ZIP/code project/structure file, etc.), you MUST verify an appropriate OSS link exists in session_files; otherwise finished=false (unless Termination/Unachievable applies).
   - If in-chat content is required, verify the complete requested content already exists in history_steps outputs; otherwise finished=false (unless Termination/Unachievable applies).

3) If any critical step is failed/missing/running OR outputs are insufficient to prove completion, set finished=false (unless Termination/Unachievable applies).

4) Insufficient evidence => finished=false and state exactly what is missing (unless Termination/Unachievable applies).

5) Contradictions: prefer later entries; if still unclear => finished=false and explain contradiction (unless Termination/Unachievable applies).

6) Do NOT assume results not explicitly supported by history_steps/session_files.

6.1) For explicit parameter constraints, if ANY constraint is not explicitly evidenced, finished=false (unless Termination/Unachievable applies).

7) Suggestion-first achievability check (MUST APPLY BEFORE declaring finished=true for Termination/Unachievable):
   - Scan ALL history_steps for actionable suggestions.
   - If any actionable suggestion is not explicitly shown as attempted and exhausted, output finished=false.

8) Termination/Unachievable (STOP even though not done):
   You may output finished=true for Termination/Unachievable ONLY if:
   - The goal is NOT completed, AND
   - history_steps provide concrete evidence that no viable next action exists, AND
   - EVERY actionable history_steps[*].suggestion has been explicitly tried in later history_steps and still failed, leaving no remaining options.
   If ANY unresolved suggestion proposes a viable next action (e.g., change parameters, switch provider/tool, request missing info),
   you MUST output finished=false (the session should continue), unless the goal is already completed.

   If you output finished=true (Termination/Unachievable), the reason MUST include:
   - "NOT completed" and
   - "cannot be completed / unachievable" and
   - the blocking evidence (specific failed steps / missing inputs).

   You MUST NOT output finished=true (Termination/Unachievable) when the only blocking evidence is that a tool failed once and the agent has not yet tried actionable suggestions (e.g., switching provider/tool, changing parameters). In that case, output finished=false.

# Output Format
Output ONLY ONE JSON object exactly:
{{
  "finished": true|false,
  "reason": "Brief, specific English explanation citing concrete evidence from history_steps and/or session_files. If using Termination/Unachievable, explicitly state: NOT completed but cannot be completed, and cite the blocking evidence."
}}

# Output Constraints
- Output ONLY valid JSON (no Markdown / code fences / extra text).
""".strip()
