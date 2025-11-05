from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.llm_config import MatMasterLlmConfig

from ..base import CalculationLlmAgent
from .constant import UniELFAgentName, UniELFServerUrl
from .prompt import description, instruction_en

# Configure SSE params
sse_params = SseServerParams(url=UniELFServerUrl)
uni_elf_toolset = CalculationMCPToolset(
    connection_params=sse_params, storage=BohriumStorge
)


# Create agent
def init_unielf_agent(llm_config):
    selected_model = llm_config.gpt_4o
    unielf_agent = CalculationLlmAgent(
        name=UniELFAgentName,
        model=selected_model,
        instruction=instruction_en,
        description=description,
        tools=[uni_elf_toolset],
    )
    return unielf_agent


root_agent = init_unielf_agent(MatMasterLlmConfig)
