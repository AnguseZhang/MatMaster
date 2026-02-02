from pydantic import BaseModel, Field


class MemoryWriterSchema(BaseModel):
    """Output of the memory writer agent: list of short insights to store."""

    insights: list[str] = Field(
        default_factory=list,
        description=(
            'Short insights, key parameters, or findings to remember for this session. '
            'For normal context: 1-5 items. For literature/long context: up to 25 items '
            'to form a queryable knowledge base for plans and parameters.'
        ),
    )
