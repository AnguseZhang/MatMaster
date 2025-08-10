from google.adk.agents import Agent
from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from .callback import init_prepare_state_before_agent
from .database_agent.agent import init_database_agent
from .deep_research_agent.agent import init_deep_research_agent
# from .data_analysis_agent.agent import init_data_analysis_agent
from dotenv import load_dotenv
from .prompt import *
from google.adk.tools import AgentTool
def init_solid_state_electrolyte_research_agent(llm_config):
    prepare_state_before_agent = init_prepare_state_before_agent(llm_config)
    database_agent = init_database_agent(llm_config)
    deep_research_agent = init_deep_research_agent(llm_config)
    # data_analysis_agent = init_data_analysis_agent(llm_config)
    
    sse_database_tool = AgentTool(agent=database_agent)
    sse_deep_research_tool = AgentTool(agent=deep_research_agent)
    
    root_agent = Agent(
        name="solid_state_electrolyte_research_agent",
        model=llm_config.gpt_4o,
        description="A solid state electrolyte research agent that can understand user's research questions and delegate research tasks to subagents including database queries, literature research.",
        sub_agents=[
            database_agent,
            deep_research_agent,
            # data_analysis_agent,
        ],
        tools=[sse_database_tool, sse_deep_research_tool],
        global_instruction=global_instruction,
        instruction=instruction_en,
        before_agent_callback=prepare_state_before_agent,
    )
    return root_agent

# Example usage
# root_agent = init_solid_state_electrolyte_research_agent()
