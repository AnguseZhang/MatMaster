from enum import Enum
from typing import Dict, List

from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexAgentName
from agents.matmaster_agent.sub_agents.chembrain_agent.constant import (
    CHEMBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserAgentName,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.constant import (
    FinetuneDPAAgentName,
)
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.constant import (
    HEA_assistant_AgentName,
)
from agents.matmaster_agent.sub_agents.HEACalculator_agent.constant import (
    HEACALCULATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.agent import MrDice_Agent
from agents.matmaster_agent.sub_agents.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.constant import (
    PerovskiteAgentName,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ssebrain_agent.constant import (
    SSEBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.agent import (
    StructureGenerateAgent,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.constant import (
    StructureGenerateAgentName,
)
from agents.matmaster_agent.sub_agents.superconductor_agent.constant import (
    SuperconductorAgentName,
)
from agents.matmaster_agent.sub_agents.thermoelectric_agent.constant import (
    ThermoelectricAgentName,
)
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
)


class StructureGenerateAgentToolEnum(str, Enum):
    BuildBulkStructureByTemplate = 'build_bulk_structure_by_template'


class MrDiceAgentToolEnum(str, Enum):
    FetchStructuresWithFilter = 'fetch_structures_with_filter'
    FetchStructuresWithSpg = 'fetch_structures_with_spg'
    FetchStructuresWithBandgap = 'fetch_structures_with_bandgap'
    FetchBohriumCrystals = 'fetch_bohrium_crystals'
    FetchOpenlamStructures = 'fetch_openlam_structures'
    FetchMofsSql = 'fetch_mofs_sql'


AGENT_CLASS_MAPPING = {
    StructureGenerateAgentName: StructureGenerateAgent,
    MrDice_Agent_Name: MrDice_Agent,
}

AGENT_TOOLS_MAPPING = {
    StructureGenerateAgentName: StructureGenerateAgentToolEnum,
    MrDice_Agent_Name: MrDiceAgentToolEnum,
}


class MatMasterSubAgentsEnum(str, Enum):
    ABACUSAgent = ABACUS_AGENT_NAME
    APEXAgent = ApexAgentName
    ChemBrainAgent = CHEMBRAIN_AGENT_NAME
    DocumentParserAgent = DocumentParserAgentName
    DPACalculatorAgent = DPACalulator_AGENT_NAME
    HEAAssistantAgent = HEA_assistant_AgentName
    HEACalculatorAgent = HEACALCULATOR_AGENT_NAME
    CompDARTAgent = COMPDART_AGENT_NAME
    MrDiceAgent = MrDice_Agent_Name
    OrganicReactionAgent = ORGANIC_REACTION_AGENT_NAME
    PerovskiteAgent = PerovskiteAgentName
    PiloteyeElectroAgent = PILOTEYE_ELECTRO_AGENT_NAME
    SSEBrainAgent = SSEBRAIN_AGENT_NAME
    StructureGenerateAgent = StructureGenerateAgentName
    SuperConductorAgent = SuperconductorAgentName
    ThermoElectricAgent = ThermoelectricAgentName
    TrajAnalysisAgent = TrajAnalysisAgentName
    FinetuneDPAAgent = FinetuneDPAAgentName

    # 第二层：具体的工具枚举映射
    @property
    def tools(self):
        return AGENT_TOOLS_MAPPING.get(self.value)

    @classmethod
    def get_all_tools_list(cls) -> List[str]:
        """获取所有agent和工具的对应字典"""
        result = []
        for category in cls:
            if category.tools:
                result += [tool.value for tool in category.tools]
        return result

    @classmethod
    def get_all_tools_dict(cls) -> Dict[str, Dict[str, str]]:
        """获取所有agent和工具的对应字典"""
        result = {}
        for category in cls:
            if category.tools:
                result[category.value] = [tool.value for tool in category.tools]
        return result


ALL_AGENT_TOOLS_DICT = MatMasterSubAgentsEnum.get_all_tools_dict()
ALL_AGENT_TOOLS_LIST = MatMasterSubAgentsEnum.get_all_tools_list()
