from pydantic import BaseModel


class StepValidationSchema(BaseModel):
    is_valid: bool
    reason: str
    confidence: str  # "high", "medium", "low"
    suggestion: str
