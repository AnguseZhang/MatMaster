from pydantic import BaseModel


class AllFinishedSchema(BaseModel):
    finished: bool
    reason: str
