from pydantic import BaseModel


class PlanConfirmSchema(BaseModel):
    flag: bool
    reason: str
