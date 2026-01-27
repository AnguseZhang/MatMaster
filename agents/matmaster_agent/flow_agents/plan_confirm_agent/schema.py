from pydantic import BaseModel


class PlanConfirmSchema(BaseModel):
    flag: bool
    selected_plan_id: int
    reason: str
