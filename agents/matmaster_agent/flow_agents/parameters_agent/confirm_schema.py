from pydantic import BaseModel


class ParametersConfirmSchema(BaseModel):
    flag: bool
    reason: str
