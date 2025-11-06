from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel

from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST


class PlanStepStatusEnum(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    PROCESS = 'process'
    PLAN = 'plan'


class PlanStepSchema(BaseModel):
    tool_name: Optional[Literal[tuple(ALL_AGENT_TOOLS_LIST)]] = None
    description: str
    status: Literal[tuple(PlanStepStatusEnum.__members__.values())] = (
        PlanStepStatusEnum.PLAN
    )


class PlanSchema(BaseModel):
    steps: List[PlanStepSchema]
    feasibility: Optional[Literal['full', 'part']] = None


class FlowStatusEnum(str, Enum):
    NO_PLAN = 'no_plan'
    NEW_PLAN = 'new_plan'
    PROCESS = 'process'
    COMPLETE = 'complete'
