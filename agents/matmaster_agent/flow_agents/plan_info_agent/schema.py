from typing import List

from pydantic import BaseModel


class PlanInfoSchema(BaseModel):
    intro: str
    plans: List[str]
    overall: str
