from enum import StrEnum

# Special Key
BIZ = 'biz'

# Primary Key
RECOMMEND_PARAMS = 'recommend_params'
EXPAND = 'expand'
PLAN = 'plan'
ERROR_OCCURRED = 'error_occurred'
ERROR_DETAIL = 'error_detail'
UPLOAD_FILE = 'upload_file'
MULTI_PLANS = 'multi_plans'
PLAN_CONFIRM = 'plan_confirm'

CURRENT_STEP = 'current_step'
CURRENT_STEP_STATUS = 'status'
CURRENT_STEP_TOOL_NAME = 'tool_name'
CURRENT_STEP_DESCRIPTION = 'step_description'
CURRENT_STEP_RESULT = 'step_result'
CURRENT_STEP_VALIDATION = 'step_validation'

HISTORY_STEPS = 'history_steps'
FINISHED_STATE = 'finished_state'

# Other Key
STEP_DESCRIPTION = 'step_description'


class StateKey(StrEnum):
    pass


class StepKey(StrEnum):
    STEP_DESCRIPTION = 'step_description'
