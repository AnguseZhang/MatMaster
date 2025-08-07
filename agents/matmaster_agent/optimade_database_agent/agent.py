from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import (
    LOCAL_EXECUTOR,
    BohriumStorge,
)
from .constant import *
from .prompt import *

load_dotenv()

# Initialize MCP tools and agent
mcp_tools = CalculationMCPToolset(
    connection_params=SseServerParams(url=OPTIMADE_URL),
    storage=BohriumStorge,
    executor=LOCAL_EXECUTOR
)


# root_agent = LlmAgent(
#     model=LiteLlm(model="deepseek/deepseek-chat"),
#     name="Optimade_Agent",
#     description="An agent specialized in materials data retrieval using OPTIMADE.",
#     instruction=(
#         "You are an expert in materials science. "
#         "Help users retrieve crystal structure data using the OPTIMADE API. "
#         "You can search by chemical formula or by element combinations. "
#         "Ask users whether they want results as CIF files or full raw structure data. "
#         "Limit the number of structures based on user request or default to 2 if not specified. "
#         "After retrieving the data, save the results to a directory and return the compressed data folder **as a download link**, "
#         "and also include **the individual file links** if available (such as CIF files). "
#         "Explain briefly what the data represents and suggest how it can be used in simulations, visualization, or materials analysis."
#     ),
#     tools=[mcp_tools],
# )


class Optimade_Agent(LlmAgent):
    def __init__(self, llm_config):
        super().__init__(
            model=llm_config.deepseek_chat,
            name=OptimadeAgentName,
            description=OptimadeAgentDescription,
            instruction=OptimadeAgentInstruction,
            tools=[mcp_tools],
        )


def init_optimade_database_agent(llm_config) -> BaseAgent:
    return Optimade_Agent(llm_config)
