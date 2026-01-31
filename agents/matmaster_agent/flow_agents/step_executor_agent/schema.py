from pydantic import BaseModel


class StepExecutorOutputSchema(BaseModel):
    """Output of the step executor: chosen tool and brief reason."""

    tool_name: str
    reason: str
