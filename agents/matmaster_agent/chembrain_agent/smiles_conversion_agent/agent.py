from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from ..base import CalculationLlmAgent
from ...llm_config import MatMasterLlmConfig
from agents.matmaster_agent.chembrain_agent.smiles_conversion_agent.callback import smiles_conversion_before_tool, \
    smiles_conversion_after_tool
from agents.matmaster_agent.chembrain_agent.smiles_conversion_agent.constant import SMILESConversionServerUrl, SMILESConversionAgentName
from agents.matmaster_agent.chembrain_agent.smiles_conversion_agent.prompt import description, instruction_en
from ...constant import BohriumStorge

# Configure SSE params
toolset = CalculationMCPToolset(connection_params=SseServerParams(url=SMILESConversionServerUrl),
                                storage=BohriumStorge)


class SMILESConversionAgent(CalculationLlmAgent):
    def __init__(self, llm_config):
        selected_model = llm_config.gpt_4o

        super().__init__(model=selected_model,
                         name=SMILESConversionAgentName,
                         description=description,
                         instruction=instruction_en,
                         tools=[toolset],
                         before_tool_callback=smiles_conversion_before_tool,
                         after_tool_callback=smiles_conversion_after_tool)


def init_smiles_conversion_agent(llm_config):
    return SMILESConversionAgent(llm_config)


root_agent = init_smiles_conversion_agent(MatMasterLlmConfig)
