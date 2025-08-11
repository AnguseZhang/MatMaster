import random
import secrets
from typing import ClassVar, List

from google.adk.agents import BaseAgent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event, EventActions
from google.genai import types

from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from .paper_agent.agent import init_paper_agent
from .report_agent.agent import init_report_agent

# 这是一个深度研究代理，它会处理文献阅读和生成科学报告的任务。
def paper_list_before_agent(callback_context: CallbackContext):
    if (
        callback_context.state.get('database_agent_tool_call', None) is None
        or len(callback_context.state['database_agent_tool_call']) == 0
    ):
        callback_context._event_actions.escalate = True
        return
    
    toolcall_infos = callback_context.state['database_agent_tool_call']
    while toolcall_infos[-1]['tool_name'] != 'query_table' or toolcall_infos[-1]['tool_response']['paper_count'] == 0:
        toolcall_infos.pop()
        if len(toolcall_infos) == 0:
            callback_context._event_actions.escalate = True
            return
    query_table_info = toolcall_infos[-1]

    paper_list = query_table_info['tool_response'].get('papers', [])
    if paper_list is None or len(paper_list) == 0:
        callback_context._event_actions.escalate = True
        return
    
    # Remove duplicates from paper_list
    unique_papers = list(set(paper_list))
    print(f"Original paper count: {len(paper_list)}, After deduplication: {len(unique_papers)}")
    
    callback_context.state['paper_list'] = {f'paper{i+1}': paper for i, paper in enumerate(unique_papers)}
    return

# 这是一个组论文代理，它会分配任务并动态创建一个并行代理来处理多个论文阅读任务。
# 它会在运行时生成一个唯一的运行ID，并为每个论文创建
class GroupPaperAgent(BaseAgent):
    """Distributes tasks and dynamically creates a ParallelAgent."""

    def __init__(self, name):
        super().__init__(name=name)

    async def _run_async_impl(self, ctx):
        paper_list = ctx.session.state['paper_list']
        POOL = list(paper_list.keys())
        run_id = secrets.token_hex(2)

        task_delta = {f"task:{run_id}:{name}": random.randint(1, 9)
                      for name in POOL}
        yield Event(
            author=self.name,
            content=types.Content(role=self.name,
                                  parts=[types.Part(text=f"running tasks for {len(POOL)} paper readings")]),
            actions=EventActions(state_delta={"current_run": run_id, **task_delta})
        )
        parallel = ParallelAgent(
            name=f"block_{run_id}",
            sub_agents=[init_paper_agent(MatMasterLlmConfig, name=n, run_id=run_id) for n in POOL]
        )
        async for ev in parallel.run_async(ctx):
            yield ev

# 这个函数是用来初始化组论文代理的
def init_paper_group_agent(llm_config):
    return GroupPaperAgent(name="group_paper")

# 这个函数是用来初始化深度研究代理的，它会创建一个顺序代理，包含组论文代理和报告代理。
def init_deep_research_agent(llm_config):
    paper_group_agent = init_paper_group_agent(llm_config)
    report_agent = init_report_agent(llm_config)

    # 创建一个顺序代理，包含组论文代理和报告代理
    # 在运行前会先执行 paper_list_before_agent 回调函数来检查论文列表
    root_agent = SequentialAgent(
        name="deep_research_agent",
        description="The agent to perform deep research literature review and generate a scientific report",
        sub_agents=[paper_group_agent, report_agent],
        before_agent_callback=paper_list_before_agent
    )
    return root_agent


# Example usage
# llm_config = create_default_config()
# root_agent = init_deep_research_agent(llm_config)
