from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import SseConnectionParams

from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from ..base import CalculationLlmAgent
from .callback import retrosyn_after_tool_transform_tgz
from .constant import RetrosynAgentName, RetrosynServerUrl
from .prompt import description, instruction_en

# Initialize MCP tools and agent with proper error handling
mcp_tools = CalculationMCPToolset(
    connection_params=SseConnectionParams(url=RetrosynServerUrl), storage=BohriumStorge
)


def init_retrosyn_agent(llm_config):
    selected_model = llm_config.gpt_4o

    retrosyn_agent = CalculationLlmAgent(
        model=selected_model,
        name=RetrosynAgentName,
        description=description,
        instruction=instruction_en,
        tools=[mcp_tools],
        after_tool_callback=[retrosyn_after_tool_transform_tgz],
    )
    return retrosyn_agent


root_agent = init_retrosyn_agent(MatMasterLlmConfig)
