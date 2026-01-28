from typing import List

from pydantic import BaseModel


class PlanInfoSinglePlanStepsSchema(BaseModel):
    tool_name: str
    step_description: str


class PlanInfoSinglePlanSchema(BaseModel):
    plan_description: str
    steps: List[PlanInfoSinglePlanStepsSchema]


class PlanInfoSchema(BaseModel):
    intro: str
    plans: List[PlanInfoSinglePlanSchema]
    overall: str
