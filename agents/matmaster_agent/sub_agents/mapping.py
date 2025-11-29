from enum import Enum

from agents.matmaster_agent.sub_agents.ABACUS_agent.agent import (
    ABACUSCalculatorAgent,
    abacus_toolset,
)
from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.sub_agents.agent_runtime_config import (
    AGENT_IMAGE_ADDRESS,
)
from agents.matmaster_agent.sub_agents.apex_agent.agent import ApexAgent, apex_toolset
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexAgentName
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.agent import (
    FileParseAgent,
)
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.constant import (
    FILE_PARSE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.built_in_agent.llm_tool_agent.agent import (
    LLMToolAgent,
)
from agents.matmaster_agent.sub_agents.built_in_agent.llm_tool_agent.constant import (
    TOOL_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.agent import ChemBrainAgent
from agents.matmaster_agent.sub_agents.chembrain_agent.constant import (
    CHEMBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.retrosyn_agent.agent import (
    retrosyn_toolset,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.smiles_conversion_agent.agent import (
    smiles_conversion_toolset,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.unielf_agent.agent import (
    UniELFAgent,
    unielf_toolset,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.unielf_agent.constant import (
    UniELFAgentName,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.agent import (
    CompDARTAgent,
    compdart_toolset,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.convexhull_agent.agent import (
    ConvexHullAgent,
    convexhull_toolset,
)
from agents.matmaster_agent.sub_agents.convexhull_agent.constant import (
    ConvexHullAgentName,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.agent import (
    DocumentParserAgentBase,
    document_parser_toolset,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserAgentName,
)
from agents.matmaster_agent.sub_agents.doe_agent.agent import (
    DoEAgent,
    doe_toolset,
)
from agents.matmaster_agent.sub_agents.doe_agent.constant import (
    DOE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.agent import (
    DPACalculationsAgent,
    dpa_toolset,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.Electron_Microscope_agent.agent import (
    ElectronMicroscopeAgent,
    electron_microscope_toolset,
)
from agents.matmaster_agent.sub_agents.Electron_Microscope_agent.constant import (
    Electron_Microscope_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.agent import (
    FinetuneDPAAgent,
    finetune_dpa_toolset,
)
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.constant import (
    FinetuneDPAAgentName,
)
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.agent import (
    HEA_assistant_AgentBase,
    hea_assistant_toolset,
)
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.constant import (
    HEA_assistant_AgentName,
)
from agents.matmaster_agent.sub_agents.HEACalculator_agent.agent import (
    HEACalculatorAgentBase,
    hea_calculator_toolset,
)
from agents.matmaster_agent.sub_agents.HEACalculator_agent.constant import (
    HEACALCULATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.HEAkb_agent.agent import (
    HEAKbAgent,
    hea_kb_toolset,
)
from agents.matmaster_agent.sub_agents.HEAkb_agent.constant import (
    HEA_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.LAMMPS_agent.agent import (
    LAMMPSAgent,
    lammps_toolset,
)
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import LAMMPS_AGENT_NAME
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.agent import (
    Bohriumpublic_AgentBase,
    bohriumpublic_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.constant import (
    BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.agent import (
    Mofdb_AgentBase,
    mofdb_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.constant import (
    MOFDB_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.agent import (
    Openlam_AgentBase,
    openlam_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.constant import (
    OPENLAM_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.agent import (
    Optimade_AgentBase,
    optimade_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.constant import (
    OPTIMADE_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.NMR_agent.agent import (
    NMRAgent,
    nmr_toolset,
)
from agents.matmaster_agent.sub_agents.NMR_agent.constant import (
    NMR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.organic_reaction_agent.agent import (
    OragnicReactionAgent,
    organic_reaction_toolset,
)
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.agent import (
    PerovskiteAgent,
    perovskite_toolset,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.constant import (
    PerovskiteAgentName,
)
from agents.matmaster_agent.sub_agents.Physical_adsorption_agent.agent import (
    PhysicalAdsorptionAgent,
    physical_adsorption_toolset,
)
from agents.matmaster_agent.sub_agents.Physical_adsorption_agent.constant import (
    Physical_Adsorption_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.agent import (
    PiloteyeElectroAgent,
    piloteye_electro_toolset,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.agent import (
    POLYMERKbAgent,
    polymer_kb_toolset,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.constant import (
    POLYMER_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.agent import (
    ScienceNavigatorAgent,
    science_navigator_toolset,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ssebrain_agent.agent import SSEBrainAgent
from agents.matmaster_agent.sub_agents.ssebrain_agent.constant import (
    SSEBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.agent import (
    SSEKbAgent,
    sse_kb_toolset,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.constant import (
    SSE_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.agent import (
    STEELPredictAgent,
    steel_predict_toolset,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.constant import (
    STEEL_PREDICT_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.agent import (
    STEELKbAgent,
    steel_kb_toolset,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.constant import (
    STEEL_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.agent import (
    StructureGenerateAgent,
    structure_generate_toolset,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.constant import (
    StructureGenerateAgentName,
)
from agents.matmaster_agent.sub_agents.superconductor_agent.agent import (
    SuperconductorAgent,
    superconductor_toolset,
)
from agents.matmaster_agent.sub_agents.superconductor_agent.constant import (
    SuperconductorAgentName,
)
from agents.matmaster_agent.sub_agents.task_orchestrator_agent.agent import (
    TaskOrchestratorAgent,
)
from agents.matmaster_agent.sub_agents.task_orchestrator_agent.constant import (
    TASK_ORCHESTRATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.thermoelectric_agent.agent import (
    ThermoAgent,
    thermoelectric_toolset,
)
from agents.matmaster_agent.sub_agents.thermoelectric_agent.constant import (
    ThermoelectricAgentName,
)
from agents.matmaster_agent.sub_agents.tools import AGENT_TOOLSET_CONFIG, ALL_TOOLS
from agents.matmaster_agent.sub_agents.traj_analysis_agent.agent import (
    TrajAnalysisAgent,
    traj_analysis_toolset,
)
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
)
from agents.matmaster_agent.sub_agents.vaspkit_agent.agent import (
    VASPKITAgent,
    vaspkit_toolset,
)
from agents.matmaster_agent.sub_agents.vaspkit_agent.constant import (
    VASPKIT_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.visualizer_agent.agent import (
    VisualizerAgent,
    visualizer_toolset,
)
from agents.matmaster_agent.sub_agents.visualizer_agent.constant import (
    VisualizerAgentName,
)
from agents.matmaster_agent.sub_agents.XRD_agent.agent import (
    XRDAgent,
    xrd_toolset,
)
from agents.matmaster_agent.sub_agents.XRD_agent.constant import (
    XRD_AGENT_NAME,
)

ALL_TOOLSET_DICT = {
    'abacus_toolset': {
        'toolset': abacus_toolset,
        'image': AGENT_TOOLSET_CONFIG[ABACUS_AGENT_NAME]['image'],
    },
    'apex_toolset': {
        'toolset': apex_toolset,
        'image': AGENT_TOOLSET_CONFIG[ApexAgentName]['image'],
    },
    'smiles_conversion_toolset': {'toolset': smiles_conversion_toolset, 'image': ''},
    'retrosyn_toolset': {'toolset': retrosyn_toolset, 'image': ''},
    'uni_elf_toolset': {'toolset': unielf_toolset, 'image': ''},
    'compdart_toolset': {
        'toolset': compdart_toolset,
        'image': AGENT_TOOLSET_CONFIG[COMPDART_AGENT_NAME]['image'],
    },
    'doe_toolset': {'toolset': doe_toolset, 'image': ''},
    'document_parser_toolset': {'toolset': document_parser_toolset, 'image': ''},
    'dpa_toolset': {
        'toolset': dpa_toolset,
        'image': AGENT_TOOLSET_CONFIG[DPACalulator_AGENT_NAME]['image'],
    },
    'finetune_dpa_toolset': {
        'toolset': finetune_dpa_toolset,
        'image': AGENT_TOOLSET_CONFIG[FinetuneDPAAgentName]['image'],
    },
    'hea_assistant_toolset': {
        'toolset': hea_assistant_toolset,
        'image': AGENT_TOOLSET_CONFIG[HEA_assistant_AgentName]['image'],
    },
    'hea_calculator_toolset': {
        'toolset': hea_calculator_toolset,
        'image': AGENT_IMAGE_ADDRESS.get('HEACalculator_agent', ''),
    },
    'hea_kb_toolset': {'toolset': hea_kb_toolset, 'image': ''},
    'sse_kb_toolset': {'toolset': sse_kb_toolset, 'image': ''},
    'polymer_kb_toolset': {'toolset': polymer_kb_toolset, 'image': ''},
    'steel_kb_toolset': {'toolset': steel_kb_toolset, 'image': ''},
    'steel_predict_toolset': {'toolset': steel_predict_toolset, 'image': ''},
    'optimade_toolset': {
        'toolset': optimade_toolset,
        'image': AGENT_IMAGE_ADDRESS.get('Optimade_agent', ''),
    },
    'bohriumpublic_toolset': {
        'toolset': bohriumpublic_toolset,
        'image': AGENT_IMAGE_ADDRESS.get('BohriumPublic_agent', ''),
    },
    'openlam_toolset': {'toolset': openlam_toolset, 'image': ''},
    'mofdb_toolset': {
        'toolset': mofdb_toolset,
        'image': AGENT_IMAGE_ADDRESS.get('Mofdb_agent', ''),
    },
    'organic_reaction_toolset': {
        'toolset': organic_reaction_toolset,
        'image': AGENT_TOOLSET_CONFIG[ORGANIC_REACTION_AGENT_NAME]['image'],
    },
    'perovskite_toolset': {'toolset': perovskite_toolset, 'image': ''},
    'piloteye_electro_toolset': {
        'toolset': piloteye_electro_toolset,
        'image': AGENT_TOOLSET_CONFIG[PILOTEYE_ELECTRO_AGENT_NAME]['image'],
    },
    'structure_generate_toolset': {
        'toolset': structure_generate_toolset,
        'image': AGENT_TOOLSET_CONFIG[StructureGenerateAgentName]['image'],
    },
    'superconductor_toolset': {
        'toolset': superconductor_toolset,
        'image': AGENT_TOOLSET_CONFIG[SuperconductorAgentName]['image'],
    },
    'thermoelectric_toolset': {
        'toolset': thermoelectric_toolset,
        'image': AGENT_TOOLSET_CONFIG[ThermoelectricAgentName]['image'],
    },
    'traj_analysis_toolset': {'toolset': traj_analysis_toolset, 'image': ''},
    'visualizer_toolset': {'toolset': visualizer_toolset, 'image': ''},
    'lammps_toolset': {
        'toolset': lammps_toolset,
        'image': AGENT_TOOLSET_CONFIG[LAMMPS_AGENT_NAME]['image'],
    },
    'vaspkit_toolset': {
        'toolset': vaspkit_toolset,
        'image': AGENT_TOOLSET_CONFIG[VASPKIT_AGENT_NAME]['image'],
    },
    'science_navigator_toolset': {'toolset': science_navigator_toolset, 'image': ''},
    'convexhull_toolset': {
        'toolset': convexhull_toolset,
        'image': AGENT_TOOLSET_CONFIG[ConvexHullAgentName]['image'],
    },
    'nmr_toolset': {'toolset': nmr_toolset, 'image': ''},
    'xrd_toolset': {'toolset': xrd_toolset, 'image': ''},
    'electron_microscope_toolset': {
        'toolset': electron_microscope_toolset,
        'image': '',
    },
    'physical_adsorption_toolset': {
        'toolset': physical_adsorption_toolset,
        'image': '',
    },
}

AGENT_CLASS_MAPPING = {
    ABACUS_AGENT_NAME: ABACUSCalculatorAgent,
    ApexAgentName: ApexAgent,
    CHEMBRAIN_AGENT_NAME: ChemBrainAgent,
    COMPDART_AGENT_NAME: CompDARTAgent,
    DOE_AGENT_NAME: DoEAgent,
    DocumentParserAgentName: DocumentParserAgentBase,
    DPACalulator_AGENT_NAME: DPACalculationsAgent,
    FinetuneDPAAgentName: FinetuneDPAAgent,
    HEA_assistant_AgentName: HEA_assistant_AgentBase,
    HEACALCULATOR_AGENT_NAME: HEACalculatorAgentBase,
    HEA_KB_AGENT_NAME: HEAKbAgent,
    SSE_KB_AGENT_NAME: SSEKbAgent,
    POLYMER_KB_AGENT_NAME: POLYMERKbAgent,
    STEEL_KB_AGENT_NAME: STEELKbAgent,
    STEEL_PREDICT_AGENT_NAME: STEELPredictAgent,
    LAMMPS_AGENT_NAME: LAMMPSAgent,
    OPTIMADE_DATABASE_AGENT_NAME: Optimade_AgentBase,
    BOHRIUMPUBLIC_DATABASE_AGENT_NAME: Bohriumpublic_AgentBase,
    MOFDB_DATABASE_AGENT_NAME: Mofdb_AgentBase,
    OPENLAM_DATABASE_AGENT_NAME: Openlam_AgentBase,
    ORGANIC_REACTION_AGENT_NAME: OragnicReactionAgent,
    PerovskiteAgentName: PerovskiteAgent,
    PILOTEYE_ELECTRO_AGENT_NAME: PiloteyeElectroAgent,
    SSEBRAIN_AGENT_NAME: SSEBrainAgent,
    SCIENCE_NAVIGATOR_AGENT_NAME: ScienceNavigatorAgent,
    StructureGenerateAgentName: StructureGenerateAgent,
    SuperconductorAgentName: SuperconductorAgent,
    TASK_ORCHESTRATOR_AGENT_NAME: TaskOrchestratorAgent,
    ThermoelectricAgentName: ThermoAgent,
    TrajAnalysisAgentName: TrajAnalysisAgent,
    VisualizerAgentName: VisualizerAgent,
    VASPKIT_AGENT_NAME: VASPKITAgent,
    ConvexHullAgentName: ConvexHullAgent,
    NMR_AGENT_NAME: NMRAgent,
    XRD_AGENT_NAME: XRDAgent,
    Electron_Microscope_AGENT_NAME: ElectronMicroscopeAgent,
    TOOL_AGENT_NAME: LLMToolAgent,
    Physical_Adsorption_AGENT_NAME: PhysicalAdsorptionAgent,
    FILE_PARSE_AGENT_NAME: FileParseAgent,
    UniELFAgentName: UniELFAgent,
}


class MatMasterSubAgentsEnum(str, Enum):
    ABACUSAgent = ABACUS_AGENT_NAME
    APEXAgent = ApexAgentName
    ChemBrainAgent = CHEMBRAIN_AGENT_NAME
    DocumentParserAgent = DocumentParserAgentName
    DPACalculatorAgent = DPACalulator_AGENT_NAME
    HEAAssistantAgent = HEA_assistant_AgentName
    HEACalculatorAgent = HEACALCULATOR_AGENT_NAME
    HEAKbAgent = HEA_KB_AGENT_NAME
    SSEKbAgent = SSE_KB_AGENT_NAME
    POLYMERKbAgent = POLYMER_KB_AGENT_NAME
    STEELKbAgent = STEEL_KB_AGENT_NAME
    STEELPredictAgent = STEEL_PREDICT_AGENT_NAME
    LAMMPSAgent = LAMMPS_AGENT_NAME
    CompDARTAgent = COMPDART_AGENT_NAME
    OptimadeDatabaseAgent = OPTIMADE_DATABASE_AGENT_NAME
    BohriumPublicDatabaseAgent = BOHRIUMPUBLIC_DATABASE_AGENT_NAME
    MOFDBDatabaseAgent = MOFDB_DATABASE_AGENT_NAME
    OpenLAMDatabaseAgent = OPENLAM_DATABASE_AGENT_NAME
    OrganicReactionAgent = ORGANIC_REACTION_AGENT_NAME
    PerovskiteAgent = PerovskiteAgentName
    PiloteyeElectroAgent = PILOTEYE_ELECTRO_AGENT_NAME
    SSEBrainAgent = SSEBRAIN_AGENT_NAME
    ScienceNavigatorAgent = SCIENCE_NAVIGATOR_AGENT_NAME
    StructureGenerateAgent = StructureGenerateAgentName
    SuperConductorAgent = SuperconductorAgentName
    ThermoElectricAgent = ThermoelectricAgentName
    TaskOrchestratorAgent = TASK_ORCHESTRATOR_AGENT_NAME
    TrajAnalysisAgent = TrajAnalysisAgentName
    FinetuneDPAAgent = FinetuneDPAAgentName
    VisualizerAgent = VisualizerAgentName
    VASPKITAgent = VASPKIT_AGENT_NAME
    ConvexHullAgent = ConvexHullAgentName
    NMRAgent = NMR_AGENT_NAME
    XRDAgent = XRD_AGENT_NAME
    ElectronMicroscopeAgent = Electron_Microscope_AGENT_NAME
    ToolAgent = TOOL_AGENT_NAME
    FileParseAgent = FILE_PARSE_AGENT_NAME
    PhysicalAdsorptionAgent = Physical_Adsorption_AGENT_NAME
    UniELFAgentNameEnum = UniELFAgentName


ALL_AGENT_TOOLS_LIST = list(ALL_TOOLS.keys())
