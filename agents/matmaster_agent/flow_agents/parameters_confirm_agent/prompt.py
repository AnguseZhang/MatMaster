PARAMETERS_CONFIRM_INSTRUCTION = """
**Task:** Analyze the user's **most recent response** to determine if they have **explicitly approved** the parameters that were just displayed for all tools in the plan.

**IMPORTANT:** Only analyze the user's response that comes **AFTER** the system has displayed the parameter confirmation card asking "请确认上述参数是否正确？确认后将生成参数 JSON 文件。". Do NOT consider responses that were made before the parameter confirmation card was shown (such as responses to plan confirmation).

**Judgment Criteria:**
- Set `flag` to `true` when the user's response contains:
    - Direct language of acceptance or agreement (e.g., "I agree", "approved", "sounds good", "参数确认", "确认参数")
    - Clear authorization to proceed with the parameters (e.g., "let's go ahead", "start", "go for it", "开始执行")
    - Positive confirmation without reservations (e.g., "yes, let's start", "proceed with these parameters", "参数没问题")
- Set `flag` to `false` if the response is:
    - A general instruction to continue a process without reference to the parameters (e.g., "continue", "next")
    - A request for modification, clarification, or more information about the parameters
    - Ambiguous, neutral, or only acknowledges receipt without endorsement
    - Questions or concerns about specific parameters
    - A response that was made BEFORE the parameter confirmation card was shown (e.g., responses to plan confirmation)

**Key Adjustment:** Consider clear action-oriented phrases like "start", "begin", "let's do this", "确认", "开始" as implicit approval **ONLY** when they directly respond to the parameter confirmation card, not to earlier messages.

**Output Format:** Return a valid JSON object with the following structure:
{{
  "flag": true | false,
  "reason": "A concise explanation citing the specific words or phrases from the user's response that led to this judgment."
}}

**Critical Instructions:**
- Your analysis should be reasonable but strict. Assume lack of approval unless there is clear indication of acceptance.
- **Only consider responses made AFTER the parameter confirmation card was displayed.**
- Return **only** the raw JSON object. Do not include any other text, commentary, or formatting outside the JSON structure.
"""
