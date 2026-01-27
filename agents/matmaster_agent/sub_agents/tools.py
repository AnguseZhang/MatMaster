from datetime import date

from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.prompt import (
    ALIAS_SEARCH_PROMPT,
    DPA_MODEL_BRANCH_SELECTION,
    STRUCTURE_BUILDING_SAVENAME,
)
from agents.matmaster_agent.sub_agents.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.sub_agents.apex_agent.constant import ApexAgentName
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.constant import (
    FILE_PARSE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.built_in_agent.llm_tool_agent.constant import (
    TOOL_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.unielf_agent.constant import (
    UniELFAgentName,
)
from agents.matmaster_agent.sub_agents.CompDART_agent.constant import (
    COMPDART_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.convexhull_agent.constant import (
    ConvexHullAgentName,
)
from agents.matmaster_agent.sub_agents.document_parser_agent.constant import (
    DocumentParserAgentName,
)
from agents.matmaster_agent.sub_agents.doe_agent.constant import (
    DOE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.DPACalculator_agent.constant import (
    DPACalulator_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.Electron_Microscope_agent.constant import (
    Electron_Microscope_AGENT_NAME,
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
from agents.matmaster_agent.sub_agents.HEAkb_agent.constant import (
    HEA_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.HEAkb_agent.prompt import (
    HEAKbAgentArgsSetting,
    HEAKbAgentSummaryPrompt,
    HEAKbAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import LAMMPS_AGENT_NAME
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.constant import (
    BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.prompt import (
    BohriumPublicAgentArgsSetting,
    BohriumPublicAgentSummaryPrompt,
    BohriumPublicAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.constant import (
    MOFDB_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.prompt import (
    MofdbAgentArgsSetting,
    MofdbAgentSummaryPrompt,
    MofdbAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.constant import (
    OPENLAM_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.prompt import (
    OpenlamAgentArgsSetting,
    OpenlamAgentSummaryPrompt,
    OpenlamAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.constant import (
    OPTIMADE_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.prompt import (
    OptimadeAgentSummaryPrompt,
    OptimadeBandgapArgsSetting,
    OptimadeBandgapToolDescription,
    OptimadeFilterArgsSetting,
    OptimadeFilterToolDescription,
    OptimadeSpgArgsSetting,
    OptimadeSpgToolDescription,
)
from agents.matmaster_agent.sub_agents.NMR_agent.constant import (
    NMR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.constant import (
    PerovskiteAgentName,
)
from agents.matmaster_agent.sub_agents.Physical_adsorption_agent.constant import (
    Physical_Adsorption_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.constant import (
    POLYMER_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.prompt import (
    POLYMERKbAgentArgsSetting,
    POLYMERKbAgentSummaryPrompt,
    POLYMERKbAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.prompt import (
    PAPER_SEARCH_AGENT_INSTRUCTION,
    WEB_SEARCH_AGENT_INSTRUCTION,
    WEBPAGE_PARSING_AGENT_INSTRUCTION,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.constant import (
    SSE_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.prompt import (
    SSEKbAgentArgsSetting,
    SSEKbAgentSummaryPrompt,
    SSEKbAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.constant import (
    STEEL_PREDICT_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.prompt import (
    STEELPredictAgentArgsSetting,
    STEELPredictAgentSummaryPrompt,
    STEELPredictAgentToolDescription,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.constant import (
    STEEL_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.prompt import (
    STEELKbAgentArgsSetting,
    STEELKbAgentSummaryPrompt,
    STEELKbAgentToolDescription,
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
from agents.matmaster_agent.sub_agents.TPD_agent.constant import (
    TPD_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
)
from agents.matmaster_agent.sub_agents.visualizer_agent.constant import (
    VisualizerAgentName,
)
from agents.matmaster_agent.sub_agents.XRD_agent.constant import (
    XRD_AGENT_NAME,
)

TODAY = date.today()

ALL_TOOLS = {
    'abacus_vacancy_formation_energy': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.VACANCY_FORMATION_ENERGY],
        'description': (
            'What it does: Calculate formation energy of non-charged vacancy in metal atoms using DFT.\n'
            'When to use: When you need vacancy formation energy for metal structures.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters like functional, spin polarization, DFT+U, magnetic moments.\n'
            'Outputs: Vacancy formation energy.\n'
            'Cannot do / Limits: Only non-charged vacancy of metal atoms; requires supercell for calculation.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': ['apex_calculate_vacancy'],
        'self_check': False,
    },
    'abacus_phonon_dispersion': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.PHONON],
        'description': (
            'What it does: Calculate phonon dispersion curve using DFT.\n'
            'When to use: When you need phonon properties and thermal corrections for a structure.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters; optional supercell, high-symmetry points, k-path.\n'
            'Outputs: Plot of phonon dispersion band structure and thermal corrections.\n'
            'Cannot do / Limits: Requires DFT; may need supercell for accuracy.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': ['apex_calculate_phonon', 'calculate_phonon'],
        'self_check': False,
    },
    'abacus_cal_band': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.BAND],
        'description': (
            'What it does: Calculate electronic band structure using DFT.\n'
            'When to use: When you need band structure and band gap for a material.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters; optional high-symmetry points, k-path.\n'
            'Outputs: Plot of band structure and band gap.\n'
            'Cannot do / Limits: DFT-based; supports PYATB or ABACUS nscf.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'abacus_calculation_scf': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.SCF],
        'description': (
            'What it does: Perform SCF calculation to compute energy using DFT.\n'
            'When to use: When you need ground state energy for a structure.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters.\n'
            'Outputs: Energy.\n'
            'Cannot do / Limits: Basic SCF; no relaxation or other properties.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'abacus_dos_run': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.DENSITY_OF_STATES],
        'description': (
            'What it does: Calculate DOS and PDOS using DFT.\n'
            'When to use: When you need density of states for electronic structure analysis.\n'
            "Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters; PDOS mode ('species', 'species+shell', 'species+orbital').\n"
            'Outputs: Plots for DOS and PDOS.\n'
            'Cannot do / Limits: DFT-based; requires relaxation support.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'abacus_badercharge_run': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.BADER_CHARGE_ANALYSIS],
        'description': (
            'What it does: Calculate Bader charge using DFT.\n'
            'When to use: When you need atomic charge analysis.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters.\n'
            'Outputs: Bader charge for each atom.\n'
            'Cannot do / Limits: DFT-based; requires charge density calculation.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'abacus_do_relax': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': (
            'What it does: Perform geometry optimization (relaxation) using DFT.\n'
            'When to use: When you need optimized structure.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters; relaxation settings (cell, steps, method, axes).\n'
            'Outputs: Relaxed structure file.\n'
            'Cannot do / Limits: DFT-based relaxation.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['apex_optimize_structure', 'optimize_structure'],
        'self_check': False,
    },
    'abacus_cal_work_function': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.WORK_FUNCTION],
        'description': (
            'What it does: Calculate work function of slabs and 2D materials using DFT.\n'
            'When to use: When you need work function for surface materials.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters; vacuum direction, dipole correction.\n'
            'Outputs: Plot of electrostatic potential and work function.\n'
            'Cannot do / Limits: For slabs and 2D materials; polar slabs have two work functions.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'abacus_run_md': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.MOLECULAR_DYNAMICS],
        'description': (
            'What it does: Perform ab-initio molecular dynamics using DFT.\n'
            'When to use: When you need MD simulation with DFT accuracy.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters; ensemble, steps, timestep, temperature.\n'
            'Outputs: ASE trajectory file.\n'
            'Cannot do / Limits: DFT-based MD; expensive for long simulations.\n'
            'Cost / Notes: High DFT cost; supports relaxation before calculation.'
        ),
        'alternative': ['run_molecular_dynamics'],
        'self_check': False,
    },
    'abacus_cal_elf': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.Electron_Localization_Function],
        'description': (
            'What it does: Calculate electron localization function using DFT.\n'
            'When to use: When you need ELF for bonding analysis.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters.\n'
            'Outputs: Cube file of ELF.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'abacus_eos': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.EOS],
        'description': (
            'What it does: Calculate equation of state using DFT.\n'
            'When to use: When you need EOS curve and bulk properties.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters.\n'
            'Outputs: Plot of fitted EOS and fitting parameters.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': ['apex_calculate_eos'],
        'self_check': False,
    },
    'abacus_cal_elastic': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.ELASTIC_CONSTANT],
        'description': (
            'What it does: Calculate elastic properties using DFT.\n'
            'When to use: When you need elastic constants and moduli.\n'
            'Prerequisites / Inputs: Structure file in cif/VASP POSCAR/ABACUS STRU format; DFT parameters.\n'
            'Outputs: Elastic tensor (Voigt notation), bulk/shear/Young’s modulus, Poisson ratio.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': ['apex_calculate_elastic', 'calculate_elastic_constants'],
        'self_check': False,
    },
    'apex_calculate_vacancy': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.VACANCY_FORMATION_ENERGY],
        'description': (
            'What it does: Evaluate vacancy formation energies by relaxing supercells with one atom removed.\n'
            'When to use: When you need vacancy formation energies for materials.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: Vacancy formation energies.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['abacus_vacancy_formation_energy'],
        'self_check': False,
    },
    'apex_optimize_structure': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.OPTIMIZE_STRUCTURE, SceneEnum.APEX],
        'description': (
            'What it does: Perform geometry optimization of a crystal, relaxing atomic positions and optionally the unit cell.\n'
            'When to use: When you need optimized crystal structure, especially for alloy systems.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: Optimized structure.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['abacus_do_relax', 'optimize_structure'],
        'self_check': False,
    },
    'apex_calculate_interstitial': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.INTERSTITIAL_FORMATION_ENERGY],
        'description': (
            'What it does: Insert interstitial atoms into a host lattice to compute formation energies across candidate sites.\n'
            'When to use: When you need interstitial formation energies.\n'
            'Prerequisites / Inputs: Host lattice structure and interstitial atoms.\n'
            'Outputs: Formation energies for candidate sites.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'apex_calculate_elastic': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.ELASTIC_CONSTANT],
        'description': (
            'What it does: Apply small strains to the lattice to extract elastic constants and derived moduli.\n'
            'When to use: When you need elastic constants and moduli.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: Elastic constants and derived moduli.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['abacus_cal_elastic', 'calculate_elastic_constants'],
        'self_check': False,
    },
    'apex_calculate_surface': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.SURFACE_ENERGY],
        'description': (
            'What it does: Execute a workflow of surface energy calculation.\n'
            'When to use: When you need surface energy.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: Surface energy.\n'
            'Cannot do / Limits: Cannot build slab structures; DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'apex_calculate_eos': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.EOS],
        'description': (
            'What it does: Scan volumes around equilibrium, relax internal coordinates, and build an equation-of-state energy–volume curve.\n'
            'When to use: When you need EOS curve.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: EOS energy-volume curve.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['abacus_eos'],
        'self_check': False,
    },
    'apex_calculate_phonon': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.PHONON],
        'description': (
            'What it does: Perform supercell finite-displacement calculations, relax configurations, and assemble phonon spectra.\n'
            'When to use: When you need phonon spectra.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: Phonon spectra.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['abacus_phonon_dispersion', 'calculate_phonon'],
        'self_check': False,
    },
    'apex_calculate_gamma': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.STACKING_FAULT_ENERGY],
        'description': (
            'What it does: Construct and relax sliding slabs to map generalized stacking-fault energies along specified slip paths.\n'
            'When to use: When you need stacking-fault energies.\n'
            'Prerequisites / Inputs: Structure file and specified slip paths.\n'
            'Outputs: Generalized stacking-fault energies.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'get_target_info': {
        'belonging_agent': UniELFAgentName,
        'scene': [SceneEnum.POLYMER],
        'description': (
            'What it does: Get target information from configuration settings for Uni-ELF inference system.\n'
            'When to use: When you need configuration info for Uni-ELF.\n'
            'Prerequisites / Inputs: None.\n'
            'Outputs: Comprehensive configuration information and available target model mappings.\n'
            'Cannot do / Limits: Specific to Uni-ELF system.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'unielf_inference': {
        'belonging_agent': UniELFAgentName,
        'scene': [SceneEnum.POLYMER],
        'description': (
            'What it does: Run Uni-ELF inference for formulation inputs to predict properties.\n'
            'When to use: When you need property prediction for formulations.\n'
            'Prerequisites / Inputs: Components and ratios for formulations.\n'
            'Outputs: Predicted properties.\n'
            'Cannot do / Limits: Supports mixtures and pseudo-formulations.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'summary_prompt': (
            'Summarize the Uni-ELF inference results based on the output:\n'
            '1. Report the url to the full results CSV file (`result_csv`).\n'
            '2. List the top 10 formulations from `top_10_results_dict`. '
            'For each, display the `formulation_id`, the composition '
            '(combine `smiles_i` and `ratio_i`), and the predicted property '
            'value (key ending in `_pred`).\n'
            '3. Highlight the best performing formulation.\n'
        ),
        'self_check': False,
    },
    # 'plan_and_visualize_reaction': {
    #     'belonging_agent': CHEMBRAIN_AGENT_NAME,
    #     'scene': [],
    #     'description': '',
    # },
    # 'convert_smiles_to_png': {
    #     'belonging_agent': CHEMBRAIN_AGENT_NAME,
    #     'scene': [SceneEnum.MOLECULAR],
    #     'description': 'Convert molecular SMILES representation into 2D molecular images',
    # },
    # 'convert_png_to_smiles': {
    #     'belonging_agent': CHEMBRAIN_AGENT_NAME,
    #     'scene': [SceneEnum.MOLECULAR],
    #     'description': 'Convert 2D molecular images to SMILES representation',
    # },
    # Perovskite solar cell literature/database tools
    'get_database_info': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': (
            'What it does: Fetch complete schema and descriptive information for the perovskite solar cell database.\n'
            'When to use: Before querying the perovskite database.\n'
            'Prerequisites / Inputs: None.\n'
            'Outputs: Database schema and descriptions.\n'
            'Cannot do / Limits: Specific to perovskite database.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'sql_database_mcp': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': (
            'What it does: Execute SQL queries against the perovskite solar cell database and return first k rows.\n'
            'When to use: When querying perovskite database after getting schema.\n'
            'Prerequisites / Inputs: SQL query; call get_database_info first.\n'
            'Outputs: First k rows of query results.\n'
            'Cannot do / Limits: Limited to first k rows.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'Unimol_Predict_Perovskite_Additive': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': (
            'What it does: Predict the additive effect on perovskite PCE with a list of additive molecules.\n'
            'When to use: When you need PCE change prediction for additives.\n'
            'Prerequisites / Inputs: List of additive molecules.\n'
            'Outputs: Predicted PCE changes.\n'
            'Cannot do / Limits: Specific to perovskite additives.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    # 'validate_smiles': {
    #     'belonging_agent': CHEMBRAIN_AGENT_NAME,
    #     'scene': [SceneEnum.MOLECULAR],
    #     'description': '',
    # },
    'run_ga': {
        'belonging_agent': COMPDART_AGENT_NAME,
        'scene': [SceneEnum.COMPOSITION_OPTIMIZATION],
        'description': (
            'What it does: Perform composition optimization targeting specific properties using genetic algorithm.\n'
            'When to use: When you need to optimize compositions for properties.\n'
            'Prerequisites / Inputs: Proxy model file prepared.\n'
            'Outputs: Optimized compositions.\n'
            'Cannot do / Limits: Cannot build doping structures; requires proxy model.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'run_doe_task': {
        'belonging_agent': DOE_AGENT_NAME,
        'scene': [SceneEnum.DOE],
        'description': (
            'What it does: Run a Design of Experiments (DoE) task using supported algorithms.\n'
            'When to use: When you need experimental design.\n'
            'Prerequisites / Inputs: Algorithm choice (Extreme Vertices, Simplex Centroid, etc.).\n'
            'Outputs: DoE results.\n'
            'Cannot do / Limits: Limited to supported algorithms.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'extract_material_data_from_pdf': {
        'belonging_agent': DocumentParserAgentName,
        'scene': [SceneEnum.LITERATURE, SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Read and extract material data and methodologies from PDF documents.\n'
            'When to use: When you need to extract info from PDF literature.\n'
            'Prerequisites / Inputs: PDF file.\n'
            'Outputs: Extracted material info and methodologies.\n'
            'Cannot do / Limits: Cannot retrieve from internet; local PDFs only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': ['file_parse', 'extract_material_data_from_webpage'],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'optimize_structure': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': (
            'What it does: Perform geometry optimization of a crystal or molecular structure using ML potential.\n'
            'When to use: When you need fast optimized structure without DFT.\n'
            'Prerequisites / Inputs: Structure file (CIF/POSCAR/ABACUS STRU/LAMMPS data); compatible ML potential.\n'
            'Outputs: Optimized structure file.\n'
            'Cannot do / Limits: ML-based; accuracy depends on potential domain.\n'
            'Cost / Notes: Low relative to DFT.'
        ),
        'args_setting': f"{DPA_MODEL_BRANCH_SELECTION}",
        'alternative': ['apex_optimize_structure', 'abacus_do_relax'],
        'self_check': False,
    },
    'run_molecular_dynamics': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.MOLECULAR_DYNAMICS],
        'description': (
            'What it does: Run molecular dynamics simulations using ML potential.\n'
            'When to use: When you need fast MD without DFT.\n'
            'Prerequisites / Inputs: Structure file; ML potential; ensemble settings.\n'
            'Outputs: MD trajectories and thermodynamics.\n'
            'Cannot do / Limits: NVE/NVT/NPT only; no classical force fields or DFT.\n'
            'Cost / Notes: Medium; scales with system size and steps.'
        ),
        'args_setting': f"{DPA_MODEL_BRANCH_SELECTION}",
        'alternative': ['abacus_run_md'],
        'self_check': False,
    },
    'calculate_phonon': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.PHONON],
        'description': (
            'What it does: Compute phonon properties using ML potential.\n'
            'When to use: When you need phonon dispersion and thermal properties.\n'
            'Prerequisites / Inputs: Optimized structure; ML potential.\n'
            'Outputs: Phonon dispersion, DOS, thermal properties.\n'
            'Cannot do / Limits: Requires finite-displacement supercells.\n'
            'Cost / Notes: High; scales with supercell size.'
        ),
        'args_setting': f"{DPA_MODEL_BRANCH_SELECTION}",
        'alternative': ['abacus_phonon_dispersion', 'apex_calculate_phonon'],
        'self_check': False,
    },
    'calculate_elastic_constants': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.ELASTIC_CONSTANT],
        'description': (
            'What it does: Compute elastic constants (Cij) and derived mechanical properties using a machine-learning interatomic potential.\n'
            'When to use: You have a relaxed structure and want fast elastic properties without running DFT.\n'
            'Prerequisites / Inputs: A structure file (e.g., CIF / POSCAR / ABACUS STRU / LAMMPS data) and a compatible ML potential available to the backend; recommended to relax the structure first.\n'
            'Outputs: Elastic tensor (Cij), bulk/shear/Young’s modulus, Poisson ratio (units reported in the result payload).\n'
            'Cannot do / Limits: Not a DFT calculation; accuracy depends on the ML potential domain; may be unreliable for structures far from training distribution.\n'
            'Cost / Notes: Medium; scales with system size and deformation settings.'
        ),
        'args_setting': f"{DPA_MODEL_BRANCH_SELECTION}",
        'alternative': ['abacus_cal_elastic', 'apex_calculate_elastic'],
        'self_check': False,
    },
    'run_neb': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.Nudged_Elastic_Band],
        'description': (
            'What it does: Run a Nudged Elastic Band (NEB) calculation with a machine-learning potential to estimate minimum energy path and barrier.\n'
            'When to use: You have initial/final states (and optionally an initial guess path) and need a fast barrier estimate.\n'
            'Prerequisites / Inputs: Initial and final structure files; optional intermediate images or image count; a compatible ML potential available to the backend.\n'
            'Outputs: Optimized NEB path, energies along images, estimated barrier and reaction coordinate.\n'
            'Cannot do / Limits: Not DFT-quality by default; may fail if images are too distorted or if the potential is not valid for the chemistry.\n'
            'Cost / Notes: High relative to single relax; cost scales with number of images and system size.'
        ),
        'args_setting': f"{DPA_MODEL_BRANCH_SELECTION}",
        'alternative': [],
        'self_check': False,
    },
    'finetune_dpa_model': {
        'belonging_agent': FinetuneDPAAgentName,
        'scene': [SceneEnum.DPA],
        'description': (
            'What it does: Fine-tune DPA pretrained models using DFT-labeled data.\n'
            'When to use: When you need to adapt DPA potential to specific systems.\n'
            'Prerequisites / Inputs: DFT-labeled data (energies, forces, stresses).\n'
            'Outputs: Fine-tuned DPA model.\n'
            'Cannot do / Limits: Cannot run calculations with the model.\n'
            'Cost / Notes: High.'
        ),
        'args_setting': 'Do NOT omit parameters that have default values. If the user does not provide a value, you MUST use the default value defined in the input parameters and include that field in the tool call. Only parameters without defaults are truly required and must be filled from user input.',
        'alternative': [],
        'self_check': False,
    },
    'HEA_params_calculator': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Calculate HEA parameters like VEC, delta, Hmix, Smix, Lambda from composition.\n'
            'When to use: When you need HEA thermodynamic parameters.\n'
            'Prerequisites / Inputs: HEA chemical formula.\n'
            'Outputs: VEC, delta, Hmix, Smix, Lambda.\n'
            'Cannot do / Limits: Specific to HEA.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'HEA_predictor': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Predict if HEA composition forms solid-solution and its crystal structure.\n'
            'When to use: When you need phase prediction for HEA.\n'
            'Prerequisites / Inputs: HEA composition.\n'
            'Outputs: Solid-solution formation and crystal structure.\n'
            'Cannot do / Limits: Uses pre-trained ML model.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'HEA_comps_generator': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Generate HEA compositions by adjusting molar ratios of one element.\n'
            'When to use: For HEA composition design and optimization.\n'
            'Prerequisites / Inputs: Initial HEA composition.\n'
            'Outputs: Series of modified compositions.\n'
            'Cannot do / Limits: Adjusts one element at a time.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'HEA_data_extract': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Extract HEA data from PDF literature.\n'
            'When to use: When you need HEA data from papers.\n'
            'Prerequisites / Inputs: PDF literature.\n'
            'Outputs: Compositions, processing, microstructures, properties.\n'
            'Cannot do / Limits: PDF format only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'HEA_paper_search': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Search and download HEA papers from arXiv.\n'
            'When to use: When you need HEA literature.\n'
            'Prerequisites / Inputs: Title, author, or keywords.\n'
            'Outputs: Search results and downloaded papers.\n'
            'Cannot do / Limits: arXiv only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [
            'query_heakb_literature',
            'search-papers-enhanced',
            'web-search',
        ],
        'self_check': False,
    },
    'HEA_bi_phase_Calc': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Calculate formation energies and phase diagrams for binary pairs in HEA.\n'
            'When to use: When you need binary phase info for HEA.\n'
            'Prerequisites / Inputs: HEA chemical system.\n'
            'Outputs: Formation energies and convex hulls.\n'
            'Cannot do / Limits: Binary pairs only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'generate_binary_phase_diagram': {
        'belonging_agent': HEACALCULATOR_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            'What it does: Generate a binary phase diagram for a specified A–B system based on available thermodynamic/energy data in the backend workflow.\n'
            'When to use: You want a quick overview of stable/competing phases across composition for a binary alloy/compound system.\n'
            'Prerequisites / Inputs: Element pair (A, B) and optional temperature/pressure range; requires accessible formation-energy/thermo dataset or computation route configured in the backend.\n'
            'Outputs: Phase diagram data (stable phases, tie-lines, composition ranges) and a plot-ready representation.\n'
            'Cannot do / Limits: If no dataset/computation route is available, the tool will return an error; results depend on data coverage and model assumptions.\n'
            'Cost / Notes: Medium; faster with cached datasets.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'query_heakb_literature': {
        'belonging_agent': HEA_KB_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': HEAKbAgentToolDescription,
        'args_setting': f"{HEAKbAgentArgsSetting}",
        'alternative': ['HEA_paper_search', 'search-papers-enhanced', 'web-search'],
        'summary_prompt': HEAKbAgentSummaryPrompt,
        'self_check': False,
    },
    'query_ssekb_literature': {
        'belonging_agent': SSE_KB_AGENT_NAME,
        'scene': [SceneEnum.Solid_State_Electrolyte],
        'description': SSEKbAgentToolDescription,
        'args_setting': f"{SSEKbAgentArgsSetting}",
        'alternative': ['search-papers-enhanced', 'web-search'],
        'summary_prompt': SSEKbAgentSummaryPrompt,
        'self_check': False,
    },
    'query_polymerkb_literature': {
        'belonging_agent': POLYMER_KB_AGENT_NAME,
        'scene': [SceneEnum.POLYMER],
        'description': POLYMERKbAgentToolDescription,
        'args_setting': f"{POLYMERKbAgentArgsSetting}",
        'alternative': ['search-papers-enhanced', 'web-search'],
        'summary_prompt': POLYMERKbAgentSummaryPrompt,
        'self_check': False,
    },
    'query_steelkb_literature': {
        'belonging_agent': STEEL_KB_AGENT_NAME,
        'scene': [SceneEnum.STEEL],
        'description': STEELKbAgentToolDescription,
        'args_setting': f"{STEELKbAgentArgsSetting}",
        'alternative': ['search-papers-enhanced', 'web-search'],
        'summary_prompt': STEELKbAgentSummaryPrompt,
        'self_check': False,
    },
    'predict_tensile_strength': {
        'belonging_agent': STEEL_PREDICT_AGENT_NAME,
        'scene': [SceneEnum.STEEL],
        'description': STEELPredictAgentToolDescription,
        'args_setting': f"{STEELPredictAgentArgsSetting}",
        'alternative': ['search-papers-enhanced', 'web-search'],
        'summary_prompt': STEELPredictAgentSummaryPrompt,
        'self_check': False,
    },
    'fetch_structures_with_filter': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': OptimadeFilterToolDescription,
        'args_setting': f"{OptimadeFilterArgsSetting}",
        'alternative': [
            'fetch_bohrium_crystals',
            'fetch_openlam_structures',
            'web-search',
        ],
        'summary_prompt': OptimadeAgentSummaryPrompt,
        'self_check': True,
    },
    'fetch_structures_with_spg': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': OptimadeSpgToolDescription,
        'args_setting': f"{OptimadeSpgArgsSetting}",
        'alternative': [
            'fetch_bohrium_crystals',
            'fetch_structures_with_filter',
            'web-search',
        ],
        'summary_prompt': OptimadeAgentSummaryPrompt,
        'self_check': True,
    },
    'fetch_structures_with_bandgap': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': OptimadeBandgapToolDescription,
        'args_setting': f"{OptimadeBandgapArgsSetting}",
        'alternative': [
            'fetch_bohrium_crystals',
            'fetch_structures_with_filter',
            'web-search',
        ],
        'summary_prompt': OptimadeAgentSummaryPrompt,
        'self_check': True,
    },
    'fetch_bohrium_crystals': {
        'belonging_agent': BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': BohriumPublicAgentToolDescription,
        'args_setting': f"{BohriumPublicAgentArgsSetting}",
        'alternative': [
            'fetch_structures_with_filter',
            'web-search',
            'fetch_openlam_structures',
        ],
        'summary_prompt': BohriumPublicAgentSummaryPrompt,
        'self_check': True,
    },
    'fetch_openlam_structures': {
        'belonging_agent': OPENLAM_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': OpenlamAgentToolDescription,
        'args_setting': f"{OpenlamAgentArgsSetting}",
        'alternative': [
            'fetch_structures_with_filter',
            'web-search',
            'fetch_openlam_structures',
        ],
        'summary_prompt': OpenlamAgentSummaryPrompt,
        'self_check': True,
    },
    'fetch_mofs_sql': {
        'belonging_agent': MOFDB_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': MofdbAgentToolDescription,
        'args_setting': f"{MofdbAgentArgsSetting}",
        'alternative': ['web-search'],
        'summary_prompt': MofdbAgentSummaryPrompt,
        'self_check': True,
    },
    'calculate_reaction_profile': {
        'belonging_agent': ORGANIC_REACTION_AGENT_NAME,
        'scene': [SceneEnum.REACTION],
        'description': (
            'What it does: Calculate reaction profile.\n'
            'When to use: For organic reaction analysis.\n'
            'Prerequisites / Inputs: Reaction inputs.\n'
            'Outputs: Reaction profile.\n'
            'Cannot do / Limits: Specific to reactions.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'run_piloteye': {
        'belonging_agent': PILOTEYE_ELECTRO_AGENT_NAME,
        'scene': [SceneEnum.PILOTEYE_ELECTRO],
        'description': (
            'What it does: Perform property calculations for lithium-ion battery electrolytes using MD and DFT.\n'
            'When to use: When you need electrolyte property calculations.\n'
            'Prerequisites / Inputs: Params JSON with formulation.\n'
            'Outputs: Target properties from modeling pipeline.\n'
            'Cannot do / Limits: Built-in molecule library; complete workflow.\n'
            'Cost / Notes: High.'
        ),
        'alternative': [],
        'self_check': False,
    },
    # 'deep_research_agent': {
    #     'belonging_agent': SSEBRAIN_AGENT_NAME,
    #     'scene': [],
    #     'description': '',
    # },
    # 'database_agent': {
    #     'belonging_agent': SSEBRAIN_AGENT_NAME,
    #     'scene': [],
    #     'description': '',
    # },
    'generate_calypso_structures': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Perform global structure search with CALYPSO to generate candidate crystal structures.\n'
            'When to use: When you need to explore polymorphs for a composition.\n'
            'Prerequisites / Inputs: Valid element inputs; CALYPSO environment.\n'
            'Outputs: Multiple POSCAR files.\n'
            'Cannot do / Limits: Requires relaxation downstream.\n'
            'Cost / Notes: Medium.'
        ),
        'args_setting': 'Parameter guidance: n_tot=10–30 gives reasonable diversity without excessive cost. Elements must be from the supported list (H–Bi, Ac–Pu). Output is a set of POSCAR files; downstream relaxation is strongly recommended.',
        'alternative': [],
        'self_check': True,
    },
    'generate_crystalformer_structures': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.CONDITIONAL_GENERATE],
        'description': (
            'What it does: Generate crystal structures based on conditional attributes and space groups.\n'
            'When to use: When you need structures with specific properties.\n'
            'Prerequisites / Inputs: Target properties (bandgap, moduli, Tc, sound); space groups.\n'
            'Outputs: Generated structures.\n'
            'Cannot do / Limits: Limited to supported properties; requires space group.\n'
            'Cost / Notes: High; uses generative model.'
        ),
        'args_setting': 'Parameter guidance: Supported properties: bandgap (eV), shear_modulus, bulk_modulus (both log₁₀ GPa), superconducting ambient_pressure/high_pressure (K), sound (m/s). For target_type="minimize", use small target (e.g., 0.1) and low alpha (0.01); for "equal", "greater", "less", use alpha=1.0. mc_steps=500 balances convergence and speed; increase to 2000 for high-accuracy targets. sample_num=20–100 recommended; distribute across space groups if random_spacegroup_num>0. Critical: Space group must be explicitly specified by the user — no defaults or auto-inference.',
        'alternative': [],
        'self_check': True,
    },
    'make_supercell_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Create supercell expansion from structure file.\n'
            'When to use: When you need larger unit cell for simulations.\n'
            'Prerequisites / Inputs: Structure file.\n'
            'Outputs: Supercell structure.\n'
            'Cannot do / Limits: Expansion only; no reduction.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': "Parameter guidance: Primarily follow user's instrucution. If not specified, firstly get structure information to understand the raw lattice. An ideal supercell for computation is isotropic. For example, the raw lattice is (4 A, 10 A, 12 A, 90 deg, 90 deg, 90 deg), the supercell should be 5 × 2 × 2. 30-50 angstrom is often appropriate for simulations. Avoid overly large cells unless needed for long-range interactions.",
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': True,
    },
    'build_bulk_structure_by_template': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Build bulk structures for simple packing types and compounds.\n'
            'When to use: For standard crystal structures like sc, fcc, bcc, hcp, rocksalt, etc.\n'
            'Prerequisites / Inputs: Element symbols or formulas; lattice constants.\n'
            'Outputs: Crystal structure file.\n'
            'Cannot do / Limits: Limited to simple structures; no complex crystals.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: Lattice constant requirements due to symmetry constraints: sc/fcc/bcc/diamond/rocksalt/cesiumchloride/zincblende/fluorite → only a; hcp/wurtzite → a and c; orthorhombic/monoclinic → a, b, c. Set conventional=True by default unless primitive cell is explicitly required. For elements, use element symbols; for compounds, use chemical formula (e.g., "NaCl"). {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [
            'fetch_bohrium_crystals',
            'fetch_structures_with_filter',
            'build_bulk_structure_by_wyckoff',
        ],
        'bypass_confirmation': True,
        'self_check': True,
    },
    'build_surface_slab': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Build surface slab structures from bulk structure.\n'
            'When to use: When you need surface models for calculations.\n'
            'Prerequisites / Inputs: Bulk structure file; Miller indices.\n'
            'Outputs: Slab structure file.\n'
            'Cannot do / Limits: Requires bulk input; vacuum added.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: Prefer slab_size_mode="layers" with slab_size_value=4–6 for stability; or "thickness" with ≥12 Å for electronic convergence. Use vacuum=15–20 Å to minimize spurious interactions. For polar surfaces or systems with strong dipoles, increase vacuum to ensure the electrostatic potential flattens in the vacuum region. Enable repair=True for covalent materials (e.g., drug-like molecule crystals, oragnic-inorganic hybrids, MOFs); Set false for regular sphrical-like inorganic crystals. Gets slow if set True. Default termination="auto" usually selects the most stoichiometric termination. {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': True,
    },
    'build_surface_adsorbate': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Build surface-adsorbate structures by placing molecules on slabs.\n'
            'When to use: For adsorption studies.\n'
            'Prerequisites / Inputs: Surface slab and adsorbate structure files.\n'
            'Outputs: Combined structure file.\n'
            'Cannot do / Limits: Single adsorbate placement.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: height=2.0 Å is typical for physisorption; reduce to 1.5–1.8 Å for chemisorption (e.g., CO on Pt). For high-symmetry sites, use string keywords ("ontop", "fcc", "hcp"); for custom placement, supply [x, y] fractional coordinates. {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': True,
    },
    'build_surface_interface': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Build heterointerface by stacking two slab structures.\n'
            'When to use: For interface studies.\n'
            'Prerequisites / Inputs: Two slab structure files.\n'
            'Outputs: Interface structure file.\n'
            'Cannot do / Limits: Basic strain checking.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: Keep max_strain=0.05 (5%) for physical relevance; relax only if intentional strain engineering is intended. Try combinding make_supercell and get_structural_info to obtain the appropriate size of the two slabs. interface_distance=2.5 Å is safe for van der Waals gaps; reduce to 1.8–2.0 Å for covalent bonding (e.g., heterostructures with orbital overlap). {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'add_cell_for_molecules': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Add periodic cell to molecular structures for calculations.\n'
            'When to use: For isolated molecule calculations requiring periodicity.\n'
            'Prerequisites / Inputs: Molecular structure file.\n'
            'Outputs: Structure with periodic cell.\n'
            'Cannot do / Limits: For gas-phase molecules.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: For non-periodic system aiming to run calculations with periodic boundary conditions required (e.g., DFT calculations with ABACUS), use add_cell_for_molecules to put the system in a large cell. Default cell [10, 10, 10] Å and vacuum = 5 Å are suitable for most gas-phase molecules; increase to ≥15 Å and ≥8 Å vacuum for polar or diffuse systems (e.g., anions, excited states). {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'build_bulk_structure_by_wyckoff': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Build crystal structures by specifying space group and Wyckoff positions.\n'
            'When to use: For custom crystal structures.\n'
            'Prerequisites / Inputs: Space group; Wyckoff positions with coordinates.\n'
            'Outputs: Crystal structure file.\n'
            'Cannot do / Limits: Requires symmetry knowledge.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: Space Group: Integer (e.g., 225) or Symbol (e.g., "Fm-3m"). Wyckoff Consistency: The provided coordinates must mathematically belong to the specific Wyckoff position (e.g., if using position 4a at (0,0,0), do not input (0.5, 0.5, 0) just because it\'s in the same unit cell; only input the canonical generator). Lattice: Angles in degrees, lengths in Å. Fractional Coordinates: Must be in [0, 1). Strictly Use the Asymmetric Unit: You must provide only the generating coordinates for each Wyckoff orbit. Do NOT Pre-calculate Symmetry: The function will automatically apply all space group operators to your input. If you manually input coordinates that are already symmetry-equivalent (e.g., providing both (x, y, z) and (-x, -y, -z) in a centrosymmetric structure), the function will generate them again, causing catastrophic atom overlapping. Redundancy Rule: Before adding a coordinate, check if it can be generated from an existing input coordinate via any operator in the Space Group. If yes, discard it. One Wyckoff letter = One coordinate triplet input. {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [
            'fetch_bohrium_crystals',
            'fetch_structures_with_filter',
            'build_bulk_structure_by_template',
        ],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'build_molecule_structures_from_smiles': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Build 3D molecular structures from SMILES strings.\n'
            'When to use: When you have SMILES and need 3D coordinates.\n'
            'Prerequisites / Inputs: SMILES string.\n'
            'Outputs: Molecular structure file.\n'
            'Cannot do / Limits: Single conformer generation.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'{STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'make_doped_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Generate doped crystal structures by substituting atoms.\n'
            'When to use: For doping studies.\n'
            'Prerequisites / Inputs: Host structure; dopant species and concentrations.\n'
            'Outputs: Doped structure file.\n'
            'Cannot do / Limits: Random substitution; recommend supercells.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f'Parameter guidance: Fractions are applied per-site; actual doping % may differ slightly in small cells — recommend ≥2×2×2 supercells for <10% doping. Covalent ions (ammonium, formamidinium, etc.) are supported via built-in library; specify by name (e.g., "ammonium"). {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'make_defect_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Create a defect structure by removing specific molecular clusters based on spatial relationships.\n'
            'When to use: For creating vacancy defects in molecular crystals by removing specific molecular units based on spatial clustering.\n'
            'Prerequisites / Inputs: Input molecular crystal structure file; optionally target species to remove and starting molecule index.\n'
            'Outputs: Defective structure file.\n'
            'Cannot do / Limits: Specifically designed for molecular crystals where entire molecules need to be removed as clusters rather than individual atoms.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': 'Parameter guidance: structure_path is the input molecular crystal structure file (e.g., CIF); target_spec is an optional dictionary mapping species IDs to counts to remove (e.g., {"C6H14N2_1": 1, "H4N_1": 1}), if None uses the simplest unit in crystal; seed_index is the index of molecule to start removing from, if None picks randomly from rarest species; method is the method to use for selecting molecules to remove; return_removed_cluster: controls whether returns removed clusters; output_file is the path to save the generated defective structure file.',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'make_amorphous_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Generate amorphous molecular structures in periodic boxes.\n'
            'When to use: For amorphous material simulations.\n'
            'Prerequisites / Inputs: Molecule structure; box size/density/count.\n'
            'Outputs: Amorphous structure file.\n'
            'Cannot do / Limits: Avoids overlaps; for further relaxation.\n'
            'Cost / Notes: Medium.'
        ),
        'args_setting': f'Parameter guidance: Input Constraint: Specify exactly two of: box_size, density, molecule_numbers. The third is derived. Density Regimes (CRITICAL): Solids/Liquids: Target ~0.9–1.2 g/cm³ (e.g., water ~1.0, polymers ~1.1). Gases/Vapors: Target orders of magnitude lower (e.g., ~0.001–0.002 g/cm³ for STP gases). Warning: Do not apply default liquid densities to gas inputs. If simulating a specific pressure, pre-calculate the required number of molecules N for the given Box Volume V (using Ideal Gas Law), then fix box_size and molecule_numbers. Composition: Use composition for multi-component mixtures; otherwise equal molar ratios are assumed. Packing Geometry: Box Size: For gases, ensure the box is large enough (usually >15 Å) to minimize unphysical periodic self-interactions, even if the density is low. {STRUCTURE_BUILDING_SAVENAME}',
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': True,
    },
    'get_structure_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Extract structural information from **files**.\n'
            'When to use: Analyze crystal/molecular structures **files**.\n'
            'Prerequisites / Inputs: Structure file path.\n'
            'Outputs: Formula, space group, lattice, atoms.\n'
            'Cannot do / Limits: No modifications; read-only.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': '',
        'alternative': ['file_parse'],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'get_molecule_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Extract molecular structure information from **files**.\n'
            'When to use: Analyze molecular structures **files**.\n'
            'Prerequisites / Inputs: Molecule file path.\n'
            'Outputs: Formula, atoms, bonds, properties.\n'
            'Cannot do / Limits: No modifications; read-only.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': '',
        'alternative': ['file_parse'],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'add_hydrogens': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_SANITIZE, SceneEnum.STRUCTURE_GENERATE],
        'description': (
            'What it does: Add hydrogen atoms to a structure.\n'
            'When to use: Complete structures by adding missing hydrogens.\n'
            'Prerequisites / Inputs: Structure file path; optional bonding or hydrogen-adding rules.\n'
            'Outputs: Structure file with hydrogens added.\n'
            'Cannot do / Limits: No optimization, refinement, or reactions.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': (
            '- target_elements: Optional. Limit hydrogen addition to specific elements.\n'
            '- optimize_torsion: Optional. If True, adjust torsion angles to optimize geometry; default is False.\n'
            '- rules: Optional. **Critical** for special cases (e.g., N in ammonium must remain target_coordination=4 and geometry of tetrahedron). '
            'If not provided, default chemical environment rules are used. For precise control, provide rules to override defaults.\n'
            '- bond_lengths: Optional. Override default bond lengths for specific atom pairs. If None, defaults are used.\n'
            'IMPORTANT: Even though rules are optional, certain functional groups require explicit rules for correctness. '
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': True,
    },
    'generate_ordered_replicas': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.STRUCTURE_SANITIZE],
        'description': (
            'What it does: Process disordered CIF files to generate ordered replica structures.\n'
            'When to use: When you have a disordered structure and need to resolve disorder to create ordered structures.\n'
            'Prerequisites / Inputs: Disordered CIF file path; optional number of structures to generate, method for generation.\n'
            'Outputs: List of paths to the generated ordered structure files.\n'
            'Cannot do / Limits: Only processes disordered structures to ordered ones; requires valid CIF input.\n'
            'Cost / Notes: Medium.'
        ),
        'args_setting': (
            'Parameter guidance: structure_path: Required. Input disordered structure file (CIF format). '
            'generate_count: Optional. Number of ordered structures to generate (default: 1). '
            'method: Optional. Method for generation ("optimal" for single best structure, "random" for ensemble of structures) (default: "random"). '
            'output_file: Optional. Directory to save output files; defaults to subdirectory of input file location.'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'remove_solvents': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.STRUCTURE_SANITIZE],
        'description': (
            'What it does: Remove specified solvent molecules from a molecular crystal structure.\n'
            'When to use: When desolvating molecular crystals to obtain solvent-free or partially desolvated structures for analysis or simulation.\n'
            'Prerequisites / Inputs: CIF structure file containing identifiable solvent molecules; target solvent names or formulas.\n'
            'Outputs: Path to the desolvated structure file.\n'
            'Cannot do / Limits: Only removes whole solvent molecules that can be identified by composition; does not modify framework atoms or resolve disorder.\n'
            'Prior step: It is recommended to call get_structure_info first to inspect molecular components and confirm solvent identities.\n'
            'Cost / Notes: Low. Recommended to inspect molecular components first.'
        ),
        'args_setting': (
            'Parameter guidance: structure_path: Required. Input CIF file containing solvent molecules. '
            'output_file: Required. Path to save the desolvated structure. '
            'targets: Required. List of solvent names or chemical formulas to remove (e.g., "H2O", "DMF"). '
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'run_superconductor_optimization': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            'What it does: Optimize superconducting structures.\n'
            'When to use: Relax superconductor geometries.\n'
            'Prerequisites / Inputs: Structure file (CIF/POSCAR).\n'
            'Outputs: Optimized structure.\n'
            'Cannot do / Limits: Only geometry optimization.\n'
            'Cost / Notes: High (DPA calculations).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'calculate_superconductor_enthalpy': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            'What it does: Calculate enthalpy and stability.\n'
            'When to use: Screen superconductor stability.\n'
            'Prerequisites / Inputs: Structure candidates.\n'
            'Outputs: Enthalpy, convex hull, stable phases.\n'
            'Cannot do / Limits: Superconductor-specific only.\n'
            'Cost / Notes: High (DPA calculations).'
        ),
        'alternative': ['predict_superconductor_Tc'],
        'self_check': False,
    },
    'predict_superconductor_Tc': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            'What it does: Predict superconducting Tc.\n'
            'When to use: Estimate critical temperature.\n'
            'Prerequisites / Inputs: Material structure.\n'
            'Outputs: Tc prediction.\n'
            'Cannot do / Limits: DPA model only.\n'
            'Cost / Notes: High (ML predictions).'
        ),
        'alternative': ['calculate_superconductor_enthalpy'],
        'self_check': False,
    },
    'screen_superconductor': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            'What it does: Screen multiple superconductors.\n'
            'When to use: Compare Tc and stability.\n'
            'Prerequisites / Inputs: List of candidates.\n'
            'Outputs: Ranked Tc and stability.\n'
            'Cannot do / Limits: Multiple candidates only.\n'
            'Cost / Notes: High (batch DPA).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'predict_thermoelectric_properties': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            'What it does: Predict thermoelectric properties.\n'
            'When to use: Estimate band gap, Seebeck, etc.\n'
            'Prerequisites / Inputs: Material structure.\n'
            'Outputs: Band gap, Seebeck, power factor, moduli.\n'
            'Cannot do / Limits: No thermal conductivity.\n'
            'Cost / Notes: High (DPA predictions).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'run_pressure_optimization': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            'What it does: Optimize under pressure.\n'
            'When to use: Relax thermoelectric structures.\n'
            'Prerequisites / Inputs: Structure, pressure.\n'
            'Outputs: Optimized structure.\n'
            'Cannot do / Limits: Thermoelectric-specific.\n'
            'Cost / Notes: High (DPA calculations).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'calculate_thermoele_enthalp': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            'What it does: Calculate enthalpy under pressure.\n'
            'When to use: Screen thermoelectric stability.\n'
            'Prerequisites / Inputs: Candidates, pressure.\n'
            'Outputs: Enthalpy, convex hull.\n'
            'Cannot do / Limits: Thermoelectric-specific.\n'
            'Cost / Notes: High (DPA calculations).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'screen_thermoelectric_candidate': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            'What it does: Screen thermoelectric candidates.\n'
            'When to use: Identify promising materials.\n'
            'Prerequisites / Inputs: Multiple structures.\n'
            'Outputs: Ranked thermoelectric properties.\n'
            'Cannot do / Limits: Requires multiple inputs.\n'
            'Cost / Notes: High (batch DPA).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'traj_analysis_diffusion': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            'What it does: Analyze diffusion from trajectories.\n'
            'When to use: Calculate MSD, diffusion coeffs.\n'
            'Prerequisites / Inputs: MD trajectory file.\n'
            'Outputs: MSD, D, conductivity.\n'
            'Cannot do / Limits: Post-MD analysis only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'traj_analysis_rdf': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            'What it does: Compute RDF from trajectories.\n'
            'When to use: Analyze atomic distributions.\n'
            'Prerequisites / Inputs: MD trajectory.\n'
            'Outputs: Radial distribution function.\n'
            'Cannot do / Limits: Post-MD analysis only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'traj_analysis_solvation': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            'What it does: Analyze solvation structures.\n'
            'When to use: Study solvent-solute interactions.\n'
            'Prerequisites / Inputs: MD trajectory.\n'
            'Outputs: Solvation shells, properties.\n'
            'Cannot do / Limits: Post-MD analysis only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'traj_analysis_bond': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            'What it does: Analyze bond length evolution.\n'
            'When to use: Monitor bond dynamics.\n'
            'Prerequisites / Inputs: MD trajectory.\n'
            'Outputs: Bond length time series.\n'
            'Cannot do / Limits: Post-MD analysis only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'traj_analysis_react': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            'What it does: Analyze reaction networks.\n'
            'When to use: Study chemical reactions.\n'
            'Prerequisites / Inputs: MD trajectory.\n'
            'Outputs: Reaction species, networks.\n'
            'Cannot do / Limits: Post-MD analysis only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'visualize_data_from_file': {
        'belonging_agent': VisualizerAgentName,
        'scene': [SceneEnum.VISUALIZE_DATA, SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Create plots from data files.\n'
            'When to use: Visualize CSV/Excel/JSON data.\n'
            'Prerequisites / Inputs: Data file URL.\n'
            'Outputs: Plots.\n'
            'Cannot do / Limits: Data files only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'visualize_data_from_prompt': {
        'belonging_agent': VisualizerAgentName,
        'scene': [SceneEnum.VISUALIZE_DATA, SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Create plots from prompts.\n'
            'When to use: Quick visualize data embedded in prompt.\n'
            'Outputs: Plots.\n'
            'Cannot do / Limits: Plot requests with valid data only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'convert_lammps_structural_format': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            'What it does: Convert to LAMMPS format.\n'
            'When to use: Prepare structures for LAMMPS.\n'
            'Prerequisites / Inputs: Structure file URL.\n'
            'Outputs: LAMMPS data file.\n'
            'Cannot do / Limits: Format conversion only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'run_lammps': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            'What it does: Run LAMMPS simulations.\n'
            'When to use: Perform MD or minimization.\n'
            'Prerequisites / Inputs: LAMMPS data file.\n'
            'Outputs: Simulation results.\n'
            'Cannot do / Limits: Requires LAMMPS format.\n'
            'Cost / Notes: High (simulation time).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'orchestrate_lammps_input': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            'What it does: Generate LAMMPS scripts.\n'
            'When to use: Create input from description.\n'
            'Prerequisites / Inputs: Natural language task.\n'
            'Outputs: LAMMPS input script.\n'
            'Cannot do / Limits: Script generation only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'search-papers-enhanced': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.LITERATURE],
        'description': (
            'What it does: Search scientific papers.\n'
            'When to use: Find research on topics.\n'
            'Prerequisites / Inputs: Topic keywords.\n'
            'Outputs: Literature summary, abstract information of relevant papers, web link of the papers\n'
            'Cannot do / Limits: Literature search only. No thesis files (.pdf,.doc, etc.) will be downloaded.\n'
            'Cost / Notes: Low.'
        ),
        'args_setting': f"""
            If not specified, apply start_time=2020-01-01, end_time={TODAY}, page_size not less than 150. When constructing query word list and question: (i) use English to ensure professionalism; (ii) avoid broad keywords like 'materials science', 'chemistry', 'progress'; (iii) extract specific, technically relevant keywords such as material names, molecular identifiers, mechanism names, property names, or application contexts; (iv) if the user's query is broad, decompose the concept into technical terms and generate concrete, research-usable keywords; (v) when translating, no segmenting composite technical noun phrases unless it is an established scientific usage. If ambiguous in Chinese, preserve the maximal-span term and translate it as a whole before considering refinement, including identifying: representative subfields, canonical mechanisms, prototypical material classes, commonly studied performance metrics, key methodologies or application contexts. These keywords must be specific enough to retrieve meaningful literature and avoid domain-level noise.

            Must be aware of these prior knowledge:
            - {ALIAS_SEARCH_PROMPT}
        """,
        'alternative': ['web-search'],
        'summary_prompt': PAPER_SEARCH_AGENT_INSTRUCTION,
        'bypass_confirmation': True,
        'self_check': False,
    },
    'web-search': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Perform web searches for what, why, how questions.\n'
            'When to use: For concise factual or explanatory lookups.\n'
            'Prerequisites / Inputs: Search query.\n'
            'Outputs: URL, title, snippet.\n'
            'Cannot do / Limits: No command-type queries; follow up with extract_info_from_webpage.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'summary_prompt': WEB_SEARCH_AGENT_INSTRUCTION,
        'bypass_confirmation': True,
        'self_check': False,
    },
    'build_convex_hull': {
        'belonging_agent': ConvexHullAgentName,
        'scene': [SceneEnum.CONVEXHULL],
        'description': (
            'What it does: Build convex hull diagrams.\n'
            'When to use: Assess thermodynamic stability.\n'
            'Prerequisites / Inputs: Material structures.\n'
            'Outputs: Convex hull, stable phases.\n'
            'Cannot do / Limits: General materials only.\n'
            'Cost / Notes: High (DPA calculations).'
        ),
        'alternative': [],
        'self_check': False,
    },
    'NMR_search_tool': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': (
            'What it does: Search a molecular database by NMR spectroscopic features to retrieve candidate structures.\n'
            'When to use: You have NMR peak/shift patterns and want likely matching molecules.\n'
            'Prerequisites / Inputs: NMR features (e.g., shifts, multiplicities, coupling, nucleus type) in the tool-accepted schema; optional tolerance settings.\n'
            'Outputs: Ranked candidate molecules/structures with match scores and key evidence fields.\n'
            'Cannot do / Limits: Not a definitive identification; results depend on database coverage and feature quality.\n'
            'Cost / Notes: Medium; tighter tolerances increase runtime and reduce recall.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'NMR_predict_tool': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': (
            'What it does: Predict NMR spectroscopic properties for molecular structures.\n'
            'When to use: When you need simulated NMR chemical shifts.\n'
            'Prerequisites / Inputs: SMILES strings.\n'
            'Outputs: Predicted NMR shifts and similarity scores.\n'
            'Cannot do / Limits: 1H and 13C only.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'NMR_reverse_predict_tool': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': (
            'What it does: Generate candidate molecular structures from NMR spectroscopic data.\n'
            'When to use: When you have NMR data and need structure candidates.\n'
            'Prerequisites / Inputs: NMR spectroscopic data.\n'
            'Outputs: Candidate molecular structures.\n'
            'Cannot do / Limits: Based on NMR features.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'extract_info_from_webpage': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Extract key information from a webpage URL.\n'
            'When to use: When you need scientific facts, data, or findings from a webpage.\n'
            'Prerequisites / Inputs: Webpage URL.\n'
            'Outputs: Extracted information in text form.\n'
            'Cannot do / Limits: Only return text and do not support generating files in any format.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'summary_prompt': WEBPAGE_PARSING_AGENT_INSTRUCTION,
        'bypass_confirmation': True,
        'self_check': False,
    },
    'xrd_parse_file': {
        'belonging_agent': XRD_AGENT_NAME,
        'scene': [SceneEnum.XRD],
        'description': (
            'What it does: Parse and preprocess raw XRD data files.\n'
            'When to use: When you have XRD data to analyze.\n'
            'Prerequisites / Inputs: XRD files (.xrdml, .xy, .asc, .txt).\n'
            'Outputs: Processed data and visualization configs.\n'
            'Cannot do / Limits: Not support .raw and .mdi format files.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'xrd_phase_identification': {
        'belonging_agent': XRD_AGENT_NAME,
        'scene': [SceneEnum.XRD],
        'description': (
            'What it does: Identify crystalline phases in XRD pattern.\n'
            'When to use: When you have processed XRD data.\n'
            'Prerequisites / Inputs: Processed CSV file; optional composition filters.\n'
            'Outputs: Top matching phases and comparison chart.\n'
            'Cannot do / Limits: Requires processed data.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'get_electron_microscope_recognize': {
        'belonging_agent': Electron_Microscope_AGENT_NAME,
        'scene': [SceneEnum.Electron_Microscope],
        'description': (
            'What it does: Analyze electron microscope images for particles and morphology.\n'
            'When to use: When you have TEM/SEM images to analyze.\n'
            'Prerequisites / Inputs: Electron microscope images(.tif, .tiff, .png, .jpeg, .jpg).\n'
            'Outputs: Detected particles, morphology, geometric properties.\n'
            'Cannot do / Limits: Only support .tif, .tiff, .png, .jpeg, .jpg format files.\n'
            'Cost / Notes: Medium.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'tpd_parse_and_get_mol': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            'What it does: Parse a single TPD file and extract recognized molecule weights (m/z or labels).\n'
            'When to use: When you need to know which molecule weights are present in a TPD file.\n'
            'Prerequisites / Inputs: Local file path, file name, data type (Signal vs. Temp/Time).\n'
            'Outputs: List of molecule weights (m/z or "*").\n'
            'Cannot do / Limits: Only parses local files; remote URLs must be downloaded first.\n'
            'Cost / Notes: Fast; supports three data types.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'tpd_get_chart': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            'What it does: Generate ECharts visualization config for selected molecule weights in a TPD file.\n'
            'When to use: When you want to plot curves for selected m/z channels from a TPD file.\n'
            'Prerequisites / Inputs: Local file path, file name, selected_weights (list of m/z), data type, line width.\n'
            'Outputs: Path to saved ECharts option JSON file.\n'
            'Cannot do / Limits: Only local files; selected_weights must match available m/z.\n'
            'Cost / Notes: Fast; supports three data types.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'tpd_get_cal': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            'What it does: Perform TPD analysis (peak finding, curve fitting, integration, derivative) for a single molecule weight (m/z) signal from one file.\n'
            'When to use: When you need detailed peak analysis, area calculation, or derivative for a specific m/z channel or total signal.\n'
            'Prerequisites / Inputs: Local file path; target molecule weight (m/z as string like "18", "44", or "*" for total signal); analysis operations (peak finding, fitting, integration range, derivative settings).\n'
            'Outputs: ECharts visualization config, integration area (if calculated), error list for failed operations.\n'
            'Cannot do / Limits: Processes one m/z at a time; call multiple times for multiple molecules; requires local files.\n'
            'Cost / Notes: Medium; each operation is independent; default to total signal (*) if m/z not specified.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'tpd_peak_integrate': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            'What it does: For a single TPD file and m/z, detect peaks and integrate each peak within a local window; visualize raw curve, peak markers, and baseline segments.\n'
            'When to use: Quickly estimate peak areas for one channel.\n'
            'Prerequisites / Inputs: Local file path, file name, mol_weight (m/z or "*"), data type, baseline_mode, window_halfwidth, line width.\n'
            'Outputs: Path to ECharts option JSON, peaks list, integrations per peak, llm_context summary.\n'
            'Cannot do / Limits: Only local files; window-based integration may overlap for dense peaks.\n'
            'Cost / Notes: Fast; supports horizontal/trend baseline.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'llm_tool': {
        'belonging_agent': TOOL_AGENT_NAME,
        'scene': [],
        'description': (
            'What it does: Use LLM for general tasks.\n'
            'When to use: For LLM-based assistance.\n'
            'Prerequisites / Inputs: Query or task.\n'
            'Outputs: LLM response.\n'
            'Cannot do / Limits: General purpose.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'physical_adsorption_echart_data': {
        'belonging_agent': Physical_Adsorption_AGENT_NAME,
        'scene': [SceneEnum.PHYSICAL_ADSORPTION],
        'description': (
            'What it does: Analyze physical adsorption instrument reports.\n'
            'When to use: When you have gas adsorption data.\n'
            'Prerequisites / Inputs: Instrument reports.\n'
            'Outputs: Analyzed data.\n'
            'Cannot do / Limits: Specific to physical adsorption.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'file_parse': {
        'belonging_agent': FILE_PARSE_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            'What it does: Parse various file contents to extract key information.\n'
            'When to use: When you need to extract information from a file but there is no dedicated information extraction tool available.\n'
            'Prerequisites / Inputs: File (TXT, PDF, Word, Excel, PNG, JPG, etc.).\n'
            'Outputs: Extracted information in text form.\n'
            'Cannot do / Limits: Only return text and do not support generating files in any format.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
}
