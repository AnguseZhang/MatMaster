from pydantic import BaseModel


class ExpandSchema(BaseModel):
    origin_user_content: str
    update_user_content: str
