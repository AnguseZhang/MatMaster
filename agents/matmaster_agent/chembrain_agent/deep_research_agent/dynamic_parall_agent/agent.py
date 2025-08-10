import random, secrets
from typing import ClassVar, List
from google.adk.events import Event, EventActions
from google.adk.agents import BaseAgent, ParallelAgent, SequentialAgent
from google.genai import types


class Worker(BaseAgent):
    """Simple worker that calculates n²."""

    def __init__(self, *, name: str, run_id: str):
        super().__init__(name=name);
        self._run_id = run_id

    async def _run_async_impl(self, ctx):
        n = ctx.session.state.get(f"task:{self._run_id}:{self.name}", 0)
        result = n * n
        yield Event(
            author=self.name,
            content=types.Content(role=self.name,
                                  parts=[types.Part(text=f"{n}² = {result}")]),
            actions=EventActions(
                state_delta={f"result:{self._run_id}:{self.name}": result})
        )


class PlannerAndRunner(BaseAgent):
    """Distributes tasks and dynamically creates a ParallelAgent."""
    POOL: ClassVar[List[str]] = ["w0", "w1", "w2"]

    async def _run_async_impl(self, ctx):
        run_id = secrets.token_hex(2)
        picked = random.sample(self.POOL,
                               k=random.randint(1, len(self.POOL)))
        task_delta = {f"task:{run_id}:{name}": random.randint(1, 9)
                      for name in picked}
        yield Event(
            author=self.name,
            content=types.Content(role=self.name,
                                  parts=[types.Part(text=f"Run {run_id} tasks {task_delta}")]),
            actions=EventActions(state_delta={"current_run": run_id, **task_delta})
        )
        parallel = ParallelAgent(
            name=f"block_{run_id}",
            sub_agents=[Worker(name=n, run_id=run_id) for n in picked]
        )
        async for ev in parallel.run_async(ctx):
            yield ev


class Aggregator(BaseAgent):
    """Aggregates results from workers."""

    async def _run_async_impl(self, ctx):
        run_id = ctx.session.state.get("current_run")
        vals = [v for k, v in ctx.session.state.items()
                if run_id and k.startswith(f"result:{run_id}:")]
        yield Event(
            author=self.name,
            content=types.Content(role=self.name,
                                  parts=[types.Part(text=f"Sum = {sum(vals)}")]),
            actions=EventActions(escalate=True)
        )


root_agent = SequentialAgent(
    name="root",
    sub_agents=[PlannerAndRunner(name="planner"), Aggregator(name="collector")]
)
