THINKING_AGENT = (
    'reasoning_agent'  # 原 thinking_agent，为避免前端 thinking 渲染报错而改名
)

# Model is asked to end first-round output with exactly one of these (no hardcoded hint lists)
FIRST_ROUND_READY = 'READY.'  # reasoning is definitive, ready for plan_make
FIRST_ROUND_NEED_REVISION = 'Revision needed.'
# Revision round: model outputs this when prior reasoning is fine (user-facing, so readable)
REVISION_OK = 'Verification passed.'

# Shown to user when verification passes, for smooth transition between thinking and next phase
REVISION_OK_USER_MESSAGE = '校验通过，采用当前规划。'

# At least 1 planning + 1 verification; if not READY keep revising; cap at 5 rounds
MAX_THINKING_ROUNDS = 5
