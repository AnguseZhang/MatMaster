from pydantic import BaseModel


class ReasoningSchema(BaseModel):
    """Reasoning agent output: phase 1 normalized query, phase 2 tool-level reasoning."""

    update_user_content: str
    tool_reasoning: str
