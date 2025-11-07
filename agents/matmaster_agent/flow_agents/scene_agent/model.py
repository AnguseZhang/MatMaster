from enum import Enum

from pydantic import BaseModel


class SceneEnum(str, Enum):
    STRUCTURE_GENERATE = 'structure_generate'
    OTHER = 'other'


class SceneSchema(BaseModel):
    scene: SceneEnum
    reason: str
