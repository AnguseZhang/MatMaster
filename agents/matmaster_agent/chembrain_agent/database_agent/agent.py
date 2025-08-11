from typing import Dict, Any

from google.adk.agents import LlmAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from .prompt import instructions_v1
from ...llm_config import MatMasterLlmConfig
from ..tools.database import DatabaseManager


def save_query_results(
        tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Any
) -> None:
    """Callback to modify state parameters for search tools"""
    tool_info = {}
    tool_info['tool_name'] = tool.name
    tool_info['tool_args'] = args
    tool_info['tool_response'] = tool_response
    if tool_context.state.get('database_agent_tool_call', None) is None:
        tool_context.state['database_agent_tool_call'] = [tool_info]
    else:
        toolcall = tool_context.state['database_agent_tool_call']
        toolcall.append(tool_info)
        tool_context.state['database_agent_tool_call'] = toolcall
    return


def init_database_agent(config):
    """Initialize the database agent with the given configuration."""
    selected_model = config.gpt_4o
    db_manager = DatabaseManager('polymer_db')
    get_table_field_info = db_manager.init_get_table_field_info()
    query_table = db_manager.init_query_table()

    database_agent = LlmAgent(
        name="database_agent",
        model=selected_model,
        instruction=instructions_v1,
        description="Construct database queries based on user's question and summarize the results.",
        tools=[get_table_field_info, query_table],
        output_key="query_result",
        # before_model_callback=update_invoke_message,
        after_tool_callback=save_query_results,
    )
    return database_agent


#root_agent = init_database_agent(MatMasterLlmConfig)
