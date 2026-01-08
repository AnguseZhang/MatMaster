import logging
from typing import AsyncGenerator, Optional, override

from google.adk.agents import InvocationContext, SequentialAgent
from google.adk.events import Event
from pydantic import Field, computed_field, model_validator

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.core_agents.comp_agents.recommend_summary_agent.agent import (
    BaseAgentWithRecAndSum,
)
from agents.matmaster_agent.core_agents.comp_agents.validator_agent import (
    ValidatorAgent,
)
from agents.matmaster_agent.core_agents.public_agents.job_agents.result_core_agent.agent import (
    ResultMCPAgent,
)
from agents.matmaster_agent.core_agents.public_agents.job_agents.submit_core_agent.agent import (
    SubmitCoreMCPAgent,
)
from agents.matmaster_agent.core_agents.public_agents.job_agents.submit_render_agent.agent import (
    SubmitRenderAgent,
)
from agents.matmaster_agent.flow_agents.model import PlanStepStatusEnum
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class BaseAsyncJobAgent(BaseAgentWithRecAndSum):
    """
    Base agent class for handling asynchronous job submissions.

    Agents that need to submit asynchronous tasks should inherit from this class.
    It provides a complete workflow for job submission, result retrieval, and
    parameter validation through specialized sub-agents.
    """

    dflow_flag: bool = Field(
        False,
        description='Indicates if this agent is related to dflow workflows',
        exclude=True,
    )
    sync_tools: Optional[list] = Field(
        None,
        description='List of tools that will be executed synchronously on the server',
    )

    @model_validator(mode='after')
    def after_init(self):
        self = self._after_init()
        agent_prefix = self.name.replace('_agent', '')

        # Create submission workflow agents
        submit_core_agent = SubmitCoreMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_submit_core_agent",
            tools=self.tools,
            enable_tgz_unpack=self.enable_tgz_unpack,
            cost_func=self.cost_func,
            enforce_single_function_call=True,
            after_tool_callback=self.after_tool_callback,
            before_tool_callback=self.before_tool_callback,
        )

        submit_render_agent = SubmitRenderAgent(
            model=self.model, name=f"{agent_prefix}_submit_render_agent"
        )

        submit_validator_agent = ValidatorAgent(
            name=f"{agent_prefix}_submit_validator_agent",
            validator_key='long_running_jobs_count',
        )

        # Create sequential agent for submission process
        self._submit_agent = SequentialAgent(
            name=f"{agent_prefix}_submit_agent",
            description=f"Coordinates {agent_prefix} job submission and frontend task queue display",
            sub_agents=[submit_core_agent, submit_render_agent, submit_validator_agent],
        )

        # Create result retrieval agent
        result_core_agent = ResultMCPAgent(
            model=self.model,
            name=f"{agent_prefix}_result_core_agent",
            tools=self.tools,
            enable_tgz_unpack=self.enable_tgz_unpack,
        )

        self._result_agent = SequentialAgent(
            name=f"{agent_prefix}_result_agent",
            description='Query status and retrieve results',
            sub_agents=[result_core_agent],
        )

        self.sub_agents += [self.submit_agent, self.result_agent]

        return self

    @computed_field
    @property
    def submit_agent(self) -> SequentialAgent:
        return self._submit_agent

    @computed_field
    @property
    def result_agent(self) -> SequentialAgent:
        return self._result_agent

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        yield update_state_event(
            ctx,
            state_delta={
                'dflow': self.dflow_flag,
                'sync_tools': self.sync_tools,
            },
        )
        yield Event(
            author=self.name, invocation_id=ctx.invocation_id
        )  # 发送一个空消息，尝试不让消息列表消失

        # 更新任务状态
        async for result_event in self.result_agent.run_async(ctx):
            yield result_event

        current_step = ctx.session.state['plan']['steps'][
            ctx.session.state['plan_index']
        ]
        current_step_status = current_step['status']
        if current_step_status in [
            PlanStepStatusEnum.SUCCESS,
            PlanStepStatusEnum.FAILED,
        ]:
            # Only Query Job Result
            pass
        elif current_step_status == PlanStepStatusEnum.SUBMITTED:
            for submit_event in all_text_event(
                ctx,
                self.name,
                '任务进行中，请等待右侧任务列表状态更新为完成后重新发起提问',
                ModelRole,
            ):
                yield submit_event
        else:
            async for run_event in super()._run_events(ctx):
                yield run_event
