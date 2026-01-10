from pydantic import BaseModel


class StepTitleSchema(BaseModel):
    title: str
