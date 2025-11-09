from typing import List

from pydantic import BaseModel

from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum


class SceneSchema(BaseModel):
    type: List[SceneEnum]
    reason: str
