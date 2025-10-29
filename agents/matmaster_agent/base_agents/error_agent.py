from typing import AsyncGenerator, final

from google.adk.agents import BaseAgent, InvocationContext, LlmAgent
from google.adk.events import Event

from agents.matmaster_agent.base_agents.abc_agent import BaseMixin
from agents.matmaster_agent.utils.event_utils import send_error_event


class ErrorHandlerMixin(BaseMixin):
    """错误处理混入类"""

    @final
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            async for event in self._process_events(ctx):
                yield event
        except BaseException as err:
            async for error_event in send_error_event(err, ctx, self.name):
                yield error_event

    @final
    async def _process_events(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """可重写的方法，专门处理事件循环"""
        async for run_event in self._run_events(ctx):
            yield run_event

        async for after_event in self._after_events(ctx):
            yield after_event

    async def _run_events(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """可重写的方法，专门处理事件循环"""
        # 调用父类的实现，这里会根据实际的继承关系调用正确的方法
        async for event in super()._run_async_impl(ctx):
            yield event

    async def _after_events(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        return
        yield


class ErrorHandleBaseAgent(ErrorHandlerMixin, BaseAgent):
    pass


class ErrorHandleLlmAgent(ErrorHandlerMixin, LlmAgent):
    pass
