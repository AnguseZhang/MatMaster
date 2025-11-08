from enum import Enum


class PlanStepStatusEnum(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    PROCESS = 'process'
    PLAN = 'plan'
