from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from ...constant import BohriumStorge
from .constant import UniELFAgentName, UniELFServerUrl
from .prompt import instruction_en
from ..base import CalculationLlmAgent
from ...llm_config import MatMasterLlmConfig

# Configure SSE params
sse_params = SseServerParams(url=UniELFServerUrl)
toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=BohriumStorge
)


# Create agent
def init_unielf_agent(llm_config):
    selected_model = llm_config.gpt_4o
    unielf_agent = CalculationLlmAgent(
        name=UniELFAgentName,
        model=selected_model,
        instruction=instruction_en,
        tools=[toolset]
    )
    return unielf_agent


root_agent = init_unielf_agent(MatMasterLlmConfig)
