from google.adk.agents import InvocationContext

from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.state import CURRENT_STEP, CURRENT_STEP_STATUS


def get_current_step(ctx: InvocationContext):
    return ctx.session.state.get(CURRENT_STEP, {})


def is_job_submitted_step(ctx: InvocationContext) -> bool:
    return (
        get_current_step(ctx).get(CURRENT_STEP_STATUS) == PlanStepStatusEnum.SUBMITTED
    )
