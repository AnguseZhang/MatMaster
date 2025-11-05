from typing import List, Literal, Optional

from pydantic import BaseModel

from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST


class PlanStepSchema(BaseModel):
    tool_name: Optional[Literal[tuple(ALL_AGENT_TOOLS_LIST)]] = None
    description: str
    status: Literal['success', 'failed', 'process', 'plan'] = 'plan'


class PlanSchema(BaseModel):
    steps: List[PlanStepSchema]
    feasibility: Optional[Literal['full', 'part']] = None
