"""
Memory writer agent: runs after plan_make, extracts insights from context + plan, writes to kernel.

No tools; output is a schema (insights list). Flow code runs this agent and writes each insight.
"""

from agents.matmaster_agent.core_agents.base_agents.schema_agent import (
    DisallowTransferAndContentLimitSchemaAgent,
)
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.memory.constant import MEMORY_WRITER_AGENT_NAME
from agents.matmaster_agent.memory.schema import MemoryWriterSchema


class MemoryWriterAgent(DisallowTransferAndContentLimitSchemaAgent):
    """Agent that outputs a list of insights; the flow writes them to the memory kernel."""

    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            name=MEMORY_WRITER_AGENT_NAME,
            model=llm_config.tool_schema_model,
            description='Extract key insights from user request and plan for session memory.',
            instruction='',  # set dynamically in flow
            output_schema=MemoryWriterSchema,
            state_key='memory_writer_output',
        )
