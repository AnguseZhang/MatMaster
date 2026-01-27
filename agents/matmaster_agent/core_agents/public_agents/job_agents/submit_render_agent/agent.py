import json
import logging
from typing import Any, AsyncGenerator, override

from google.adk.agents import InvocationContext
from google.adk.events import Event
from pydantic import model_validator

from agents.matmaster_agent.constant import (
    JOB_LIST_KEY,
    MATMASTER_AGENT_NAME,
    ModelRole,
)
from agents.matmaster_agent.core_agents.comp_agents.error_climit_agent import (
    ErrorHandleAndContentLimitLlmAgent,
)
from agents.matmaster_agent.core_agents.public_agents.job_agents.submit_render_agent.prompt import (
    SubmitRenderAgentDescription,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.event_utils import (
    all_text_event,
    is_text,
    update_state_event,
)

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


class SubmitRenderAgent(ErrorHandleAndContentLimitLlmAgent):
    @model_validator(mode='before')
    @classmethod
    def modify_description(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get('description') is None:
            data['description'] = SubmitRenderAgentDescription

        return data

    @override
    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(
            f"[{MATMASTER_AGENT_NAME}]:[{self.name}] state: {ctx.session.state}"
        )
        async for event in super()._run_events(ctx):
            if is_text(event) and ctx.session.state['render_job_list']:
                for cur_render_job_id in ctx.session.state['render_job_id']:
                    # Render Frontend Job-List Component
                    job_list_comp_data = {
                        'eventType': 1,
                        'eventData': {
                            'contentType': 1,
                            'renderType': '@bohrium-chat/matmodeler/task-message',
                            'content': {
                                JOB_LIST_KEY: ctx.session.state['long_running_jobs'][
                                    cur_render_job_id
                                ]
                            },
                        },
                    }
                    if not ctx.session.state['dflow']:
                        # 同时发送流式消息（聊条的时候可见）和数据库消息（历史记录的时候可见）
                        for event in all_text_event(
                            ctx=ctx,
                            author=self.name,
                            text=f"<bohrium-chat-msg>{json.dumps(job_list_comp_data)}</bohrium-chat-msg>",
                            role=ModelRole,
                        ):
                            yield event

                yield update_state_event(
                    ctx, state_delta={'render_job_list': False, 'render_job_id': []}
                )
