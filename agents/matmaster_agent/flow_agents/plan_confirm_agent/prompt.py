PlanConfirmInstruction = """
**Task:** Analyze the user's response to determine if they have **explicitly approved** the previously mentioned plan or proposal.

**Judgment Criteria:**
- Set `flag` to `true` when the user's response contains:
    - Direct language of acceptance or agreement (e.g., "I agree", "approved", "sounds good")
    - Clear authorization to proceed with the specific plan (e.g., "let's go ahead", "start", "go for it")
    - Positive confirmation without reservations (e.g., "yes, let's start", "proceed as planned")
- Set `flag` to `false` if the response is:
    - A general instruction to continue a process without reference to the plan (e.g., "continue", "next")
    - A request for modification, clarification, or more information
    - Ambiguous, neutral, or only acknowledges receipt without endorsement

**Key Adjustment:** Consider clear action-oriented phrases like "start", "begin", "let's do this" as implicit approval when they directly respond to a specific plan proposal.

**Output Format:** Return a valid JSON object with the following structure:
{{
  "flag": true | false,
  "selected_plan_id": 0,
  "reason": "A concise explanation citing the specific words or phrases from the user's response that led to this judgment."
}}

**Critical Instructions:**
- Your analysis should be reasonable but strict. Assume lack of approval unless there is clear indication of acceptance.
- `selected_plan_id` must be a **0-based index** into the presented plans:
  - If the user says "方案1" / "plan 1" / "option 1", then `selected_plan_id` = 0
  - If the user says "方案2" / "plan 2" / "option 2", then `selected_plan_id` = 1
  - And so on.
- If `flag` is `false` or no plan is clearly selected, set `selected_plan_id` to 0.
- Return **only** the raw JSON object. Do not include any other text, commentary, or formatting outside the JSON structure.
"""
