from enum import Enum


class FlowStatusEnum(str, Enum):
    NO_PLAN = 'no_plan'
    NEW_PLAN = 'new_plan'
    PROCESS = 'process'
    COMPLETE = 'complete'
    FAILED = 'failed'
