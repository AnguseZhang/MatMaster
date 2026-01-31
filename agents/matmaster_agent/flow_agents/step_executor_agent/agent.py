import logging

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.flow_agents.step_executor_agent.constant import (
    STEP_EXECUTOR_AGENT,
)
from agents.matmaster_agent.flow_agents.step_executor_agent.prompt import (
    STEP_EXECUTOR_INSTRUCTION,
)
from agents.matmaster_agent.flow_agents.step_executor_agent.schema import (
    StepExecutorOutputSchema,
)
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def create_step_executor_agent(model, instruction: str = None):
    """
    Create the step executor agent. Instruction is typically set at runtime via
    get_step_executor_instruction(goal, prev_outputs_summary, available_tools_str, suggested_tool)
    before calling run_async(ctx).
    """
    return DisallowTransferAndContentLimitSchemaAgent(
        name=STEP_EXECUTOR_AGENT,
        model=model,
        description='根据当前步目标和可用工具选择要执行的工具',
        instruction=instruction or STEP_EXECUTOR_INSTRUCTION,
        output_schema=StepExecutorOutputSchema,
        state_key='step_executor',
    )
