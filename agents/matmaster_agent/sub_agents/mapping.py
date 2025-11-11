from enum import Enum

from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.sub_agents.ABACUS_agent.agent import (
    ABACUSCalculatorAgent,
    abacus_toolset,
)
from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.sub_agents.apex_agent.agent import ApexAgent, apex_toolset
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexAgentName
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
    uni_elf_toolset,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.agent import (
    CompDARTAgent,
    compdart_toolset,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.agent import (
    DocumentParserAgentBase,
    document_parser_toolset,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserAgentName,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.agent import (
    DPACalculationsAgent,
    dpa_toolset,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
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
from agents.matmaster_agent.sub_agents.MrDice_agent.agent import MrDice_Agent
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.agent import (
    bohriumpublic_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.agent import (
    mofdb_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.agent import (
    openlam_toolset,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.agent import (
    optimade_toolset,
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
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.agent import (
    PiloteyeElectroAgent,
    piloteye_electro_toolset,
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
from agents.matmaster_agent.sub_agents.traj_analysis_agent.agent import (
    TrajAnalysisAgent,
    traj_analysis_toolset,
)
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
)

ALL_TOOLSET_DICT = {
    'abacus_toolset': abacus_toolset,
    'apex_toolset': apex_toolset,
    'smiles_conversion_toolset': smiles_conversion_toolset,
    'retrosyn_toolset': retrosyn_toolset,
    'uni_elf_toolset': uni_elf_toolset,
    'compdart_toolset': compdart_toolset,
    'document_parser_toolset': document_parser_toolset,
    'dpa_toolset': dpa_toolset,
    'finetune_dpa_toolset': finetune_dpa_toolset,
    'hea_assistant_toolset': hea_assistant_toolset,
    'hea_calculator_toolset': hea_calculator_toolset,
    'optimade_toolset': optimade_toolset,
    'bohriumpublic_toolset': bohriumpublic_toolset,
    'openlam_toolset': openlam_toolset,
    'mofdb_toolset': mofdb_toolset,
    'organic_reaction_toolset': organic_reaction_toolset,
    'perovskite_toolset': perovskite_toolset,
    'piloteye_electro_toolset': piloteye_electro_toolset,
    'structure_generate_toolset': structure_generate_toolset,
    'superconductor_toolset': superconductor_toolset,
    'thermoelectric_toolset': thermoelectric_toolset,
    'traj_analysis_toolset': traj_analysis_toolset,
}

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

ALL_TOOLS = {
    'abacus_modify_input': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_modify_stru': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_collect_data': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_calculation_scf': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_badercharge_run': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_cal_band': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_cal_elf': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_cal_charge_density_difference': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_cal_spin_density': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_dos_run': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_cal_elastic': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_eos': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_phonon_dispersion': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_do_relax': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_vibration_analysis': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'abacus_run_md': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'run_abacus_calculation': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': '',
    },
    'apex_calculate_vacancy': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'apex_optimize_structure': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.OPTIMIZE_STRUCTURE, SceneEnum.APEX],
        'description': 'Perform geometry optimization of a crystal(recommend alloy system), relaxing atomic positions and optionally the unit cell.',
    },
    'apex_calculate_interstitial': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'apex_calculate_elastic': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'apex_calculate_surface': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'apex_calculate_eos': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'apex_calculate_phonon': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'apex_calculate_gamma': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX],
        'description': '',
    },
    'get_target_info': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'unielf_inference': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'plan_and_visualize_reaction': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'convert_smiles_to_png': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [SceneEnum.SMILES],
        'description': '',
    },
    'convert_png_to_smiles': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [SceneEnum.SMILES],
        'description': '',
    },
    'validate_smiles': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [SceneEnum.SMILES],
        'description': '',
    },
    'run_ga': {
        'belonging_agent': COMPDART_AGENT_NAME,
        'scene': [SceneEnum.CompositionOptimization],
        'description': '',
    },
    'extract_material_data_from_pdf': {
        'belonging_agent': DocumentParserAgentName,
        'scene': [],
        'description': '',
    },
    'optimize_structure': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.OPTIMIZE_STRUCTURE, SceneEnum.DPA],
        'description': 'Perform geometry optimization of a crystal or molecular structure. Supports relaxation of atomic positions and optionally the unit cell.',
    },
    'run_molecular_dynamics': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.MOLECULAR_DYNAMICS],
        'description': '',
    },
    'calculate_phonon': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.PHONON],
        'description': 'Compute phonon properties. Generates displaced supercells, calculates interatomic forces, and derives phonon dispersion, thermal properties, and optional total/projected DOS. Outputs band structures, entropy, free energy, heat capacity, and maximum phonon frequencies. Requires optimized structure as input.',
    },
    'calculate_elastic_constants': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA],
        'description': '',
    },
    'run_neb': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA],
        'description': '',
    },
    'finetune_dpa_model': {
        'belonging_agent': FinetuneDPAAgentName,
        'scene': [SceneEnum.DPA],
        'description': 'Fine tune dpa2 or dpa3 pretrained model with provided labeled data',
    },
    'HEA_params_calculator': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [],
        'description': '',
    },
    'HEA_predictor': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [],
        'description': '',
    },
    'generate_binary_phase_diagram': {
        'belonging_agent': HEACALCULATOR_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'fetch_structures_with_filter': {
        'belonging_agent': MrDice_Agent_Name,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures from multiple OPTIMADE-compatible databases using raw OPTIMADE filter strings (elements, chemical formulas, logical combinations) across providers like alexandria, cod, mp, oqmd, tcod.',
    },
    'fetch_structures_with_spg': {
        'belonging_agent': MrDice_Agent_Name,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures filtered by specific space group numbers (1-230) or mineral/structure types (e.g., rutile, spinel, perovskite) combined with base filters from OPTIMADE-compatible databases.',
    },
    'fetch_structures_with_bandgap': {
        'belonging_agent': MrDice_Agent_Name,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures filtered by band gap range (min/max in eV) combined with base filters (elements, formulas) from OPTIMADE-compatible databases that provide band gap data.',
    },
    'fetch_bohrium_crystals': {
        'belonging_agent': MrDice_Agent_Name,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures from the Bohrium Public database (includes Materials Project data) with flexible filtering by formula, elements, space group, atom counts, predicted formation energy range, and band gap range, supporting exact or contains match modes.',
    },
    'fetch_openlam_structures': {
        'belonging_agent': MrDice_Agent_Name,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures from the OpenLAM database filtered by chemical formula, energy range, and submission time, with output in CIF or JSON format.',
    },
    'fetch_mofs_sql': {
        'belonging_agent': MrDice_Agent_Name,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Execute SQL queries against the MOF database with support for complex multi-table joins, window functions, CTEs, and statistical analysis for advanced MOF property queries and composition analysis.',
    },
    'calculate_reaction_profile': {
        'belonging_agent': ORGANIC_REACTION_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'semantic_search': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [],
        'description': '',
    },
    'plot_vs_time': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [],
        'description': '',
    },
    'run_piloteye': {
        'belonging_agent': PILOTEYE_ELECTRO_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'deep_research_agent': {
        'belonging_agent': SSEBRAIN_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'database_agent': {
        'belonging_agent': SSEBRAIN_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'generate_calypso_structures': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'generate_crystalformer_structures': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Generate crystal structures based on specified conditional attributes (bandgap, shear_modulus, bulk_modulus, superconducting critical temperature, sound) and user-provided space groups.',
    },
    'make_supercell_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_bulk_structure_by_template': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_molecule_structure_from_g2database': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_surface_slab': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_surface_adsorbate': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_surface_interface': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'add_cell_for_molecules': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_bulk_structure_by_wyckoff': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'build_molecule_structures_from_smiles': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'make_doped_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'make_amorphous_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': '',
    },
    'get_structure_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [],
        'description': '',
    },
    'run_superconductor_optimization': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [],
        'description': '',
    },
    'calculate_superconductor_enthalpy': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [],
        'description': '',
    },
    'predict_superconductor_Tc': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [],
        'description': '',
    },
    'screen_superconductor': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [],
        'description': '',
    },
    'predict_thermoelectric_properties': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [],
        'description': '',
    },
    'run_pressure_optimization': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [],
        'description': '',
    },
    'calculate_thermoele_enthalp': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [],
        'description': '',
    },
    'screen_thermoelectric_candidate': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [],
        'description': '',
    },
    'traj_analysis_msd': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [],
        'description': '',
    },
    'traj_analysis_rdf': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [],
        'description': '',
    },
    'traj_analysis_solvation': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [],
        'description': '',
    },
    'traj_analysis_bond': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [],
        'description': '',
    },
    'traj_analysis_react': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [],
        'description': '',
    },
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


ALL_AGENT_TOOLS_LIST = list(ALL_TOOLS.keys())
