PlanConfirmInstruction = """
**Task:** Analyze the user's response to determine if they have **explicitly and unambiguously approved** the previously mentioned plan or proposal.

**Judgment Criteria:**
- Set `flag` to `true` **only if** the user's response contains direct and explicit language of acceptance, agreement, or approval. Examples include: "I agree," "approved," "sounds good," "let's go ahead with this plan," "yes, proceed as proposed."
- Set `flag` to `false` if the response is:
    - An instruction to continue a process (e.g., "continue," "proceed," "next," "then do the necessary follow-up").
    - A request for modification, clarification, or more information.
    - Ambiguous, neutral, or only acknowledges receipt without endorsement.

**Output Format:** Return a valid JSON object with the following structure:
{{
  "flag": true | false,
  "reason": "A concise explanation citing the specific words or phrases from the user's response that led to this judgment."
}}

**Critical Instructions:**
- Your analysis must be strict. Assume lack of approval unless it is explicitly stated.
- Return **only** the raw JSON object. Do not include any other text, commentary, or formatting outside the JSON structure.

**Example Output:**
{{
  "flag": false,
  "reason": "User's message '然后进行所需的后续操作' is an instruction to proceed with a workflow step, not a statement of agreement with the plan itself."
}}
"""
