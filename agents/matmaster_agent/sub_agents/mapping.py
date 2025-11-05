from enum import Enum
from typing import Dict, List

from agents.matmaster_agent.sub_agents.ABACUS_agent.agent import ABACUSCalculatorAgent
from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.sub_agents.apex_agent.agent import ApexAgent
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexAgentName
from agents.matmaster_agent.sub_agents.chembrain_agent.agent import ChemBrainAgent
from agents.matmaster_agent.sub_agents.chembrain_agent.constant import (
    CHEMBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.agent import CompDARTAgent
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.agent import (
    DocumentParserAgentBase,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserAgentName,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.agent import (
    DPACalculationsAgent,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.agent import FinetuneDPAAgent
from agents.matmaster_agent.sub_agents.finetune_dpa_agent.constant import (
    FinetuneDPAAgentName,
)
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.agent import (
    HEA_assistant_AgentBase,
)
from agents.matmaster_agent.sub_agents.HEA_assistant_agent.constant import (
    HEA_assistant_AgentName,
)
from agents.matmaster_agent.sub_agents.HEACalculator_agent.agent import (
    HEACalculatorAgentBase,
)
from agents.matmaster_agent.sub_agents.HEACalculator_agent.constant import (
    HEACALCULATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.agent import MrDice_Agent
from agents.matmaster_agent.sub_agents.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.sub_agents.organic_reaction_agent.agent import (
    OragnicReactionAgent,
)
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.agent import PerovskiteAgent
from agents.matmaster_agent.sub_agents.perovskite_agent.constant import (
    PerovskiteAgentName,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.agent import (
    PiloteyeElectroAgent,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ssebrain_agent.agent import SSEBrainAgent
from agents.matmaster_agent.sub_agents.ssebrain_agent.constant import (
    SSEBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.agent import (
    StructureGenerateAgent,
)
from agents.matmaster_agent.sub_agents.structure_generate_agent.constant import (
    StructureGenerateAgentName,
)
from agents.matmaster_agent.sub_agents.superconductor_agent.agent import (
    SuperconductorAgent,
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
from agents.matmaster_agent.sub_agents.thermoelectric_agent.agent import ThermoAgent
from agents.matmaster_agent.sub_agents.thermoelectric_agent.constant import (
    ThermoelectricAgentName,
)
from agents.matmaster_agent.sub_agents.traj_analysis_agent.agent import (
    TrajAnalysisAgent,
)
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
)

AGENT_CLASS_MAPPING = {
    ABACUS_AGENT_NAME: ABACUSCalculatorAgent,
    ApexAgentName: ApexAgent,
    CHEMBRAIN_AGENT_NAME: ChemBrainAgent,
    COMPDART_AGENT_NAME: CompDARTAgent,
    DocumentParserAgentName: DocumentParserAgentBase,
    DPACalulator_AGENT_NAME: DPACalculationsAgent,
    FinetuneDPAAgentName: FinetuneDPAAgent,
    HEA_assistant_AgentName: HEA_assistant_AgentBase,
    HEACALCULATOR_AGENT_NAME: HEACalculatorAgentBase,
    MrDice_Agent_Name: MrDice_Agent,
    ORGANIC_REACTION_AGENT_NAME: OragnicReactionAgent,
    PerovskiteAgentName: PerovskiteAgent,
    PILOTEYE_ELECTRO_AGENT_NAME: PiloteyeElectroAgent,
    SSEBRAIN_AGENT_NAME: SSEBrainAgent,
    StructureGenerateAgentName: StructureGenerateAgent,
    SuperconductorAgentName: SuperconductorAgent,
    TASK_ORCHESTRATOR_AGENT_NAME: TaskOrchestratorAgent,
    ThermoelectricAgentName: ThermoAgent,
    TrajAnalysisAgentName: TrajAnalysisAgent,
}


class ABACUSAgentToolEnum(str, Enum):
    Prepare = 'abacus_prepare'
    ModifyInput = 'abacus_modify_input'
    ModifyStructure = 'abacus_modify_stru'
    CollectData = 'abacus_collect_data'
    CalculationSCF = 'abacus_calculation_scf'
    BaderChargeRun = 'abacus_badercharge_run'
    CalculateBand = 'abacus_cal_band'
    CalculateELF = 'abacus_cal_elf'
    CalculateChargeDensityDifference = 'abacus_cal_charge_density_difference'
    CalculateSpinDensity = 'abacus_cal_spin_density'
    DOSRun = 'abacus_dos_run'
    CalculateElastic = 'abacus_cal_elastic'
    EOS = 'abacus_eos'
    PhononDispersion = 'abacus_phonon_dispersion'
    DoRelax = 'abacus_do_relax'
    VibrationAnalysis = 'abacus_vibration_analysis'
    RunMD = 'abacus_run_md'


class APEXAgentToolEnum(str, Enum):
    CalculateVacancy = 'apex_calculate_vacancy'
    OptimizeStructure = 'apex_optimize_structure'
    CalculateInterstitial = 'apex_calculate_interstitial'
    CalculateElastic = 'apex_calculate_elastic'
    CalculateSurface = 'apex_calculate_surface'
    CalculateEOS = 'apex_calculate_eos'
    CalculatePhonon = 'apex_calculate_phonon'
    CalculateGamma = 'apex_calculate_gamma'


class ChemBrainAgentToolEnum(str, Enum):
    GetTargetInfo = 'get_target_info'
    UniELFInference = 'unielf_inference'
    PlanAndVisualizeReaction = 'plan_and_visualize_reaction'
    ConvertSMILESToPNG = 'convert_smiles_to_png'
    ConvertPNGToSMILES = 'convert_png_to_smiles'
    ValidateSMILES = 'validate_smiles'


class CompDartAgentToolEnum(str, Enum):
    RunGA = 'run_ga'


class DocumentParserAgentToolEnum(str, Enum):
    ExtractMaterialDataFromPDF = 'extract_material_data_from_pdf'


class DPAAgentToolEnum(str, Enum):
    OptimizeStructure = 'optimize_structure'
    RunMolecularDynamics = 'run_molecular_dynamics'
    CalculatePhonon = 'calculate_phonon'
    CalculateElasticConstants = 'calculate_elastic_constants'
    RunNEB = 'run_neb'


class FinetuneDPAAgentToolEnum(str, Enum):
    FinetuneDPAModel = 'finetune_dpa_model'


class HEAAssistantAgentToolEnum(str, Enum):
    ParamsCalculator = 'HEA_params_calculator'
    Predictor = 'HEA_predictor'


class HEACalculatorAgentToolEnum(str, Enum):
    GenerateBinaryPhaseDiagram = 'generate_binary_phase_diagram'


class MrDiceAgentToolEnum(str, Enum):
    FetchStructuresWithFilter = 'fetch_structures_with_filter'
    FetchStructuresWithSpg = 'fetch_structures_with_spg'
    FetchStructuresWithBandgap = 'fetch_structures_with_bandgap'
    FetchBohriumCrystals = 'fetch_bohrium_crystals'
    FetchOpenlamStructures = 'fetch_openlam_structures'
    FetchMofsSql = 'fetch_mofs_sql'


class OrganicReactionAgentToolEnum(str, Enum):
    CalculateReactionProfile = 'calculate_reaction_profile'


class PerovskiteAgentToolEnum(str, Enum):
    SemanticSearch = 'semantic_search'
    PlotVsTime = 'plot_vs_time'


class PilotEyeElectroAgentToolEnum(str, Enum):
    RunPilotEye = 'run_piloteye'


class SSEBrainAgentToolEnum(str, Enum):
    DeepResearchAgent = 'deep_research_agent'
    DatabaseAgent = 'database_agent'


class StructureGenerateAgentToolEnum(str, Enum):
    GenerateCalypsoStructures = 'generate_calypso_structures'
    GenerateCrystalformerStructures = 'generate_crystalformer_structures'
    MakeSupercellStructure = 'make_supercell_structure'
    BuildBulkStructureByTemplate = 'build_bulk_structure_by_template'
    BuildMoleculeStructureFromG2Database = 'build_molecule_structure_from_g2database'
    BuildSurfaceSlab = 'build_surface_slab'
    BuildSurfaceAdsorbate = 'build_surface_adsorbate'
    BuildSurfaceInterface = 'build_surface_interface'
    AddCellForMolecules = 'add_cell_for_molecules'
    BuildBulkStructureByWyckoff = 'build_bulk_structure_by_wyckoff'
    BuildMoleculeStructuresFromSMILES = 'build_molecule_structures_from_smiles'
    MakeDopedStructure = 'make_doped_structure'
    MakeAmorphousStructure = 'make_amorphous_structure'
    GetStructureInfo = 'get_structure_info'


class SuperconductorAgentToolEnum(str, Enum):
    RunSuperconductorOptimization = 'run_superconductor_optimization'
    CalculateSuperconductorEnthalpy = 'calculate_superconductor_enthalpy'
    PredictSuperconductorTc = 'predict_superconductor_Tc'
    ScreenSuperconductor = 'screen_superconductor'


class ThermoelectricAgentToolEnum(str, Enum):
    PredictThermoelectricProperties = 'predict_thermoelectric_properties'
    RunPressureOptimization = 'run_pressure_optimization'
    CalculateThermoelectricEnthalpy = 'calculate_thermoele_enthalp'
    ScreenThermoelectricCandidate = 'screen_thermoelectric_candidate'


class TrajAnalysisAgentToolEnum(str, Enum):
    TrajAnalysisMSD = 'traj_analysis_msd'
    TrajAnalysisRDF = 'traj_analysis_rdf'
    TrajAnalysisSolvation = 'traj_analysis_solvation'
    TrajAnalysisBond = 'traj_analysis_bond'
    TrajAnalysisReact = 'traj_analysis_react'


AGENT_TOOLS_MAPPING = {
    ABACUS_AGENT_NAME: ABACUSAgentToolEnum,
    ApexAgentName: APEXAgentToolEnum,
    CHEMBRAIN_AGENT_NAME: ChemBrainAgentToolEnum,
    COMPDART_AGENT_NAME: CompDartAgentToolEnum,
    DocumentParserAgentName: DocumentParserAgentToolEnum,
    DPACalulator_AGENT_NAME: DPAAgentToolEnum,
    FinetuneDPAAgentName: FinetuneDPAAgentToolEnum,
    HEA_assistant_AgentName: HEAAssistantAgentToolEnum,
    HEACALCULATOR_AGENT_NAME: HEACalculatorAgentToolEnum,
    MrDice_Agent_Name: MrDiceAgentToolEnum,
    ORGANIC_REACTION_AGENT_NAME: OrganicReactionAgentToolEnum,
    PerovskiteAgentName: PerovskiteAgentToolEnum,
    PILOTEYE_ELECTRO_AGENT_NAME: PilotEyeElectroAgentToolEnum,
    SSEBRAIN_AGENT_NAME: SSEBrainAgentToolEnum,
    StructureGenerateAgentName: StructureGenerateAgentToolEnum,
    SuperconductorAgentName: SuperconductorAgentToolEnum,
    ThermoelectricAgentName: ThermoelectricAgentToolEnum,
    TrajAnalysisAgentName: TrajAnalysisAgentToolEnum,
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
    TaskOrchestratorAgent = TASK_ORCHESTRATOR_AGENT_NAME
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
