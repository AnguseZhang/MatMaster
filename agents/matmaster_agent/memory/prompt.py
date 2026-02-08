from agents.matmaster_agent.utils.sanitize_braces import (
    with_sanitized_braces,
)

# Threshold (chars) above which we treat user context as "literature / long context".
LONG_CONTEXT_THRESHOLD = 2500

# Max insights for long context (literature / expert intuition).
LONG_CONTEXT_MAX_INSIGHTS = 25


@with_sanitized_braces('user_context', 'plan_intro')
def get_memory_writer_instruction(
    user_context: str,
    plan_intro: str,
    is_long_context: bool = False,
) -> str:
    """Build instruction for the memory writer agent with current context and plan summary.

    When is_long_context is True (e.g. user pasted literature), ask for more insights
    (up to LONG_CONTEXT_MAX_INSIGHTS) to form a queryable knowledge base for plans and parameters.
    """
    if is_long_context:
        return f"""You are a memory writer for computational materials research. The user has provided literature or long context below. Extract key findings, parameters, methods, and themes that should support later plans and parameter decisions in this session. Output up to {LONG_CONTEXT_MAX_INSIGHTS} short insights (one concise sentence each). Put them in the "insights" array. This forms a queryable "expert intuition" for the session. If nothing is worth remembering, return an empty "insights" array.

<User request / context (literature or long)>
{user_context}

<Plan summary>
{plan_intro}
"""
    return f"""You are a memory writer. Based on the user request and plan below, output 1-5 short insights or key parameters to remember for this session. Each insight should be one concise sentence. Put them in the "insights" array. If there is nothing worth remembering, return an empty "insights" array.

<User request / context>
{user_context}

<Plan summary>
{plan_intro}
"""
