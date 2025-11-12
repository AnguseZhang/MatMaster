from pydantic import BaseModel

from agents.matmaster_agent.flow_agents.intent_agent.model import IntentEnum


class IntentSchema(BaseModel):
    type: IntentEnum
    reason: str
