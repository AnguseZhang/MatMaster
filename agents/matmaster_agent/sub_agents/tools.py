from datetime import date

from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
from agents.matmaster_agent.prompt import (
    DPA_PRIOR_KNOWLEDGE,
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
)
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import LAMMPS_AGENT_NAME
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.constant import (
    BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.prompt import (
    BohriumPublicAgentArgsSetting,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.constant import (
    MOFDB_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.prompt import (
    MofdbAgentArgsSetting,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.constant import (
    OPENLAM_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.prompt import (
    OpenlamAgentArgsSetting,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.constant import (
    OPTIMADE_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.prompt import (
    OptimadeAgentArgsSetting,
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
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.prompt import (
    PiloteyeElectroAgentDescription,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.constant import (
    POLYMER_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.POLYMERkb_agent.prompt import (
    POLYMERKbAgentArgsSetting,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.prompt import (
    PAPER_SEARCH_AGENT_INSTRUCTION,
    WEB_SEARCH_AGENT_INSTRUCTION,
    WEBPAGE_PARSING_AGENT_INSTRUCTION,
)
from agents.matmaster_agent.sub_agents.ssebrain_agent.constant import (
    SSEBRAIN_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.constant import (
    SSE_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.SSEkb_agent.prompt import (
    SSEKbAgentArgsSetting,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.constant import (
    STEEL_PREDICT_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.STEEL_PREDICT_agent.prompt import (
    STEELPredictAgentArgsSetting,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.constant import (
    STEEL_KB_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.STEELkb_agent.prompt import (
    STEELKbAgentArgsSetting,
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
from agents.matmaster_agent.sub_agents.vaspkit_agent.constant import VASPKIT_AGENT_NAME
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
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate formation energy of non-charged vacancy. Only vacancy of metal atoms are supported. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate vacancy formation energy, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. Supercell can be used. The calculated vacancy formation energy will be returned.',
    },
    'abacus_phonon_dispersion': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.PHONON],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate phonon dispersion curve. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate band, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. Used supercell can be setted manually. Support provide high-symmetry points and k-point path. A plot of phonon dispersion band structure and related thermal corrections from vibration will be returned.',
    },
    'abacus_cal_band': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.BAND],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate band. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate band, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. PYATB and ABACUS nscf can be selected to plot the band. Support provide high-symmetry points and k-point path. A plot of band structure and band gap will be returned.',
    },
    'abacus_calculation_scf': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate energy. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment can be setted. ',
    },
    'abacus_dos_run': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.DENSITY_OF_STATES],
        'description': "Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate DOS and PDOS. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate DOS and PDOS, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. PDOS mode can be 'species' (PDOS for a element like 'Pd'), 'species+shell' (PDOS for shell of a element like d shell of 'Pd'), 'species+orbital' (PDOS for orbitals of a element like d_xy of 'Pd'). Two plots for DOS and PDOS will be returned.",
    },
    'abacus_badercharge_run': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.BADER_CHARGE_ANALYSIS],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate Bader charge. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate Bader charge, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. Bader charge for each atom is returned.',
    },
    'abacus_do_relax': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to do relax calculation. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment can be setted. Whether to relax cell, max relaxation steps, relax method and fixed axes during the relaxation can be setted. A file of relaxed structure will be returned.',
    },
    'abacus_cal_work_function': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.WORK_FUNCTION],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate work function of slabs and 2D materials. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate EOS, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. The direction of vacuum, and whether to do dipole correction can be setted. A plot of the average electrostat potential and calculated work function can be returned. For polar slabs, two work function for each of the surface will be calculated.',
    },
    'abacus_run_md': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.MOLECULAR_DYNAMICS],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to do ab-initio molecule dynamics calculation. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate EOS, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. Used ensemble, steps of AIMD, timestep, temperature can be setted. An ASE trajectory file will be returned.',
    },
    'abacus_cal_elf': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate electron localization function. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate EOS, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. A cube file of ELF will be returned.',
    },
    'abacus_eos': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': 'Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate equation of state fitting curve for materials. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate EOS, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. A plot of fitted EOS and fitting parameters will be returned.',
    },
    'abacus_cal_elastic': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS],
        'description': "Use a structure file in cif/VASP POSCAR/ABACUS STRU format as input to calculate elastic properties of materials. DFT parameters including DFT functional,  spin polarization, DFT+U settings and initial magnetic moment calculation can be setted. Support do relax calculation before calculate band, and whether to do relax, whether to relax cell, relax method, and fixed axes during the relaxation can be setted. Full elastic tensor (in Voigt notation), bulk modulus, shear modulus, Young's modulus and possion ratio will be returned.",
    },
    'apex_calculate_vacancy': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.VACANCY_FORMATION_ENERGY],
        'description': 'Evaluate vacancy formation energies by relaxing supercells with one atom removed. Based on DFT(Density functional theory).',
    },
    'apex_optimize_structure': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.OPTIMIZE_STRUCTURE, SceneEnum.APEX],
        'description': 'Perform geometry optimization of a crystal(recommend alloy system), relaxing atomic positions and optionally the unit cell. Based on DFT(Density functional theory).',
    },
    'apex_calculate_interstitial': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.INTERSTITIAL_FORMATION_ENERGY],
        'description': 'Insert interstitial atoms into a host lattice to compute formation energies across candidate sites. Based on DFT(Density functional theory).',
    },
    'apex_calculate_elastic': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.ELASTIC_CONSTANT],
        'description': 'Apply small strains to the lattice to extract elastic constants and derived moduli. Based on DFT(Density functional theory).',
    },
    'apex_calculate_surface': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.SURFACE_ENERGY],
        'description': 'Execute a workflow of surfacce energy calculation. CANNOT build slab structures. Based on DFT(Density functional theory).',
    },
    'apex_calculate_eos': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.EOS],
        'description': 'Scan volumes around equilibrium, relax internal coordinates, and build an equation-of-state energy–volume curve. Based on DFT(Density functional theory).',
    },
    'apex_calculate_phonon': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.PHONON],
        'description': 'Perform supercell finite-displacement calculations, relax configurations, and assemble phonon spectra. Based on DFT(Density functional theory).',
    },
    'apex_calculate_gamma': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.STACKING_FAULT_ENERGY],
        'description': 'Construct and relax sliding slabs to map generalized stacking-fault energies along specified slip paths. Based on DFT(Density functional theory).',
    },
    'get_target_info': {
        'belonging_agent': UniELFAgentName,
        'scene': [SceneEnum.POLYMER],
        'description': (
            'Get target information from configuration settings. '
            'This function retrieves comprehensive configuration information '
            'needed for the Uni-ELF inference system, including background '
            'documentation and available target model mappings.',
        ),
    },
    'unielf_inference': {
        'belonging_agent': UniELFAgentName,
        'scene': [SceneEnum.POLYMER],
        'description': (
            'Run Uni-ELF inference for formulation inputs (components and '
            'ratios), a DP Technology model for predicting formulation '
            'properties. Supports mixtures and pseudo-formulations '
            '(e.g., copolymers with monomer ratios). This function performs '
            'property prediction task.',
        ),
        'summary_prompt': (
            'Summarize the Uni-ELF inference results based on the output:\n'
            '1. Report the url to the full results CSV file (`result_csv`).\n'
            '2. List the top 10 formulations from `top_10_results_dict`. '
            'For each, display the `formulation_id`, the composition '
            '(combine `smiles_i` and `ratio_i`), and the predicted property '
            'value (key ending in `_pred`).\n'
            '3. Highlight the best performing formulation.\n'
        ),
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
        'description': 'Fetch complete schema and descriptive information for the perovskite solar cell database (ALWAYS call this function before sql_database_mcp()).',
    },
    'sql_database_mcp': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': 'Execute SQL queries against the perovskite solar cell database and return the first k rows. (ALWAYS call get_database_info() first to understand the schema and important columns.)',
    },
    'Unimol_Predict_Perovskite_Additive': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': 'Predict the additive effect of a perovskite PCE change with a list of additives molecules.',
    },
    # 'validate_smiles': {
    #     'belonging_agent': CHEMBRAIN_AGENT_NAME,
    #     'scene': [SceneEnum.MOLECULAR],
    #     'description': '',
    # },
    'run_ga': {
        'belonging_agent': COMPDART_AGENT_NAME,
        'scene': [SceneEnum.COMPOSITION_OPTIMIZATION],
        'description': 'CAN DO: composition optimization targeting specific properties; CANNOT DO: build doping structures based on given composition',
    },
    'run_doe_task': {
        'belonging_agent': DOE_AGENT_NAME,
        'scene': [SceneEnum.DOE],
        'description': 'Run a Design of Experiments (DoE) task using one of the supported algorithms (Extreme Vertices, Simplex Centroid, Simplex Lattice, SDC).',
    },
    'extract_material_data_from_pdf': {
        'belonging_agent': DocumentParserAgentName,
        'scene': [SceneEnum.LITERATURE, SceneEnum.UNIVERSAL],
        'description': 'Read and extract contents from PDF-formatted document files. Outputs information of materials involved and methodologies, supporting additional information required by users. CANNOT retrieve data from the internet.',
        'bypass_confirmation': True,
    },
    'optimize_structure': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': 'Perform geometry optimization of a crystal or molecular structure. Supports relaxation of atomic positions and optionally the unit cell. Based on machine learning potential.',
        'args_setting': f"{DPA_PRIOR_KNOWLEDGE}",
    },
    'run_molecular_dynamics': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.MOLECULAR_DYNAMICS],
        'description': 'Run molecular dynamics simulations using ASE interface. CAN DO: run MD with DPA pretrained model or user-uploaded DeePMD mdoel; run NVE, NVT, NPT MD with logging basic thermodynamics and lattice parameters. CANNOT DO: run MD with classical force-field or ab initio (or DFT) methods; nor run complicated MD like shock conditions, or with complicated on-the-fly stastistics like RDF, MSD. Based on machine learning potential.',
        'args_setting': f"{DPA_PRIOR_KNOWLEDGE}",
    },
    'calculate_phonon': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.PHONON],
        'description': 'Compute phonon properties. Generates displaced supercells, calculates interatomic forces, and derives phonon dispersion, thermal properties, and optional total/projected DOS. Outputs band structures, entropy, free energy, heat capacity, and maximum phonon frequencies. Requires optimized structure as input. Based on machine learning potential.',
        'args_setting': f"{DPA_PRIOR_KNOWLEDGE}",
    },
    'calculate_elastic_constants': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.ELASTIC_CONSTANT],
        'description': 'Based on machine learning potential.',
        'args_setting': f"{DPA_PRIOR_KNOWLEDGE}",
    },
    'run_neb': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA],
        'description': 'Based on machine learning potential.',
        'args_setting': f"{DPA_PRIOR_KNOWLEDGE}",
    },
    'finetune_dpa_model': {
        'belonging_agent': FinetuneDPAAgentName,
        'scene': [SceneEnum.DPA],
        'description': 'Fine-tune DPA2 or DPA3 pretrained models using user-provided DFT-labeled data (e.g., energies, forces, stresses) to adapt the potential to specific material systems; CANNOT DO: use DPA model to run calculations for material systems. ',
        'args_setting': 'Do NOT omit parameters that have default values. If the user does not provide a value, you MUST use the default value defined in the input parameters and include that field in the tool call. Only parameters without defaults are truly required and must be filled from user input.',
    },
    'HEA_params_calculator': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'Split the HEA chemical formula into element and corresponding ratios, and calculate VEC(valence electron consentration), delta(atom size factor), Hmix(mix enthalpy), Smix(mix entropy), Lambda parameters of the given composition.',
    },
    'HEA_predictor': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'Use the given High Entropy Alloy composition to construct a dataframe of important features, and Use the dataframe and a pre-trained ML model to predict if the formula can form a solid-solution system, and if so, predict its crystal structure.',
    },
    'HEA_comps_generator': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'Based on a given initial High Entropy Alloy composition, Generate a series of High Entropy Alloy compositions by adjusting the molar ratio of one specific element. Use this tool first for further High Entropy Alloy composition design and optimization.',
    },
    'HEA_data_extract': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'Extract High Entropy Alloy related data from provided literature in PDF format, including compositions, heat treatment processing methods, micro-phasestructures, and mechanical/thermal properties.',
    },
    'HEA_paper_search': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'Search for papers on arXiv by title, author or keywords related to High Entropy Alloys, download the original publications to the server and save basic information. provide search results and save direction for further data extraction and analysis.',
    },
    'HEA_bi_phase_Calc': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'For all binary pairs in the High Entropy Alloy chemical system, calculate formation energies and generate binary phase diagram convex hulls',
    },
    'generate_binary_phase_diagram': {
        'belonging_agent': HEACALCULATOR_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': '',
    },
    'query_heakb_literature': {
        'belonging_agent': HEA_KB_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': 'Query the HEAkb (High-Entropy Alloy) literature knowledge.',
        'args_setting': f"{HEAKbAgentArgsSetting}",
    },
    'query_ssekb_literature': {
        'belonging_agent': SSE_KB_AGENT_NAME,
        'scene': [SceneEnum.Solid_State_Electrolyte],
        'description': 'Query the SSEkb literature knowledge base.',
        'args_setting': f"{SSEKbAgentArgsSetting}",
    },
    'query_polymerkb_literature': {
        'belonging_agent': POLYMER_KB_AGENT_NAME,
        'scene': [SceneEnum.POLYMER],
        'description': 'Query the POLYMERkb polymer literature knowledge base. ',
        'args_setting': f"{POLYMERKbAgentArgsSetting}",
    },
    'query_steelkb_literature': {
        'belonging_agent': STEEL_KB_AGENT_NAME,
        'scene': [SceneEnum.STEEL],
        'description': 'Query the STEELkb literature knowledge base. ',
        'args_setting': f"{STEELKbAgentArgsSetting}",
    },
    'predict_tensile_strength': {
        'belonging_agent': STEEL_PREDICT_AGENT_NAME,
        'scene': [SceneEnum.STEEL],
        'description': 'Predict the ultimate tensile strength (UTS) of steel based on chemical composition using a trained neural network model. Supports batch prediction. Takes a list of chemical formula strings (even for single formula, use a list with one element), validates elements are within allowed set (B, C, N, O, Al, Si, P, S, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Nb, Mo, W), and returns a list of predicted tensile strength values in MPa. Formula format: ElementSymbol followed by numeric value (e.g., ["Fe70Cr20Ni10"] for single or ["Fe70Cr20Ni10", "Fe68Cr22Ni10"] for batch). Batch prediction is recommended for systematic composition variation analysis.',
        'args_setting': f"{STEELPredictAgentArgsSetting}",
    },
    'fetch_structures_with_filter': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Internal database search tool. Retrieve crystal structures from OPTIMADE-compatible providers using full OPTIMADE filter language (logical operators, HAS ALL, HAS ANY, chemical_formula_anonymous, etc.). Supports logical filters and broad searches across multiple external providers (alexandria, cmr, cod, mcloud, mcloudarchive, mp, mpdd, mpds, nmd, odbx, omdb, oqmd, tcod, twodmatpedia). Use when logical filter expressions (OR, NOT, complex boolean logic) or anonymous formulas are required. Cannot combine space group and band gap in a single request. Use as alternative when Bohrium cannot handle the query (e.g., requires logical filters).',
        'args_setting': f"{OptimadeAgentArgsSetting}",
    },
    'fetch_structures_with_spg': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Internal database search tool. Retrieve crystal structures filtered by specific space group numbers (1-230) or mineral/structure types (e.g., rutile, spinel, perovskite) from OPTIMADE-compatible databases. Supports broad searches across multiple external providers. Cannot combine space group and band gap in a single request. Use as alternative when Bohrium cannot handle the query.',
        'args_setting': f"{OptimadeAgentArgsSetting}",
    },
    'fetch_structures_with_bandgap': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Internal database search tool. Retrieve crystal structures filtered by band gap range (min/max in eV) from OPTIMADE-compatible databases that provide band gap data. Supports broad searches across multiple external providers. Cannot combine space group and band gap in a single request. Use as alternative when Bohrium cannot handle the query.',
        'args_setting': f"{OptimadeAgentArgsSetting}",
    },
    'fetch_bohrium_crystals': {
        'belonging_agent': BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Internal database search tool. PREFERRED when both Bohrium and OPTIMADE can handle the query. Retrieve crystal structures from the Bohrium Public database (includes Materials Project / MP dataset). Supports formula, elements, spacegroup_number, atom_count_range, predicted_formation_energy_range, band_gap_range. Supports space group / atom count / band gap / formation energy queries. Supports formula fragment searches via match_mode=0. Can combine space group and band gap in a single request. Faster than OPTIMADE. Cannot handle logical filter expressions (OR, NOT, complex boolean logic).',
        'args_setting': f"{BohriumPublicAgentArgsSetting}",
    },
    'fetch_openlam_structures': {
        'belonging_agent': OPENLAM_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Internal database search tool. Retrieve crystal structures from the OpenLAM internal database. Supports formula, min_energy, max_energy, min_submission_time, max_submission_time filters. Supports energy window searches and time-based filters. No support for space group, band gap, elements list, or logical filters.',
        'args_setting': f"{OpenlamAgentArgsSetting}",
    },
    'fetch_mofs_sql': {
        'belonging_agent': MOFDB_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Internal database search tool. Execute SQL queries against the MOF database. Supports all MOF-related queries via SQL: MOFid, MOFkey, name, database source, void fraction, pore sizes, surface area, element composition analysis, adsorption selectivity calculations, temperature sensitivity analysis, statistical ranking. Supports complex multi-table joins, window functions, CTEs, and statistical analysis. Any request clearly about MOFs should be handled by MOFdb.',
        'args_setting': f"{MofdbAgentArgsSetting}",
    },
    'calculate_reaction_profile': {
        'belonging_agent': ORGANIC_REACTION_AGENT_NAME,
        'scene': [SceneEnum.REACTION],
        'description': '',
    },
    'run_piloteye': {
        'belonging_agent': PILOTEYE_ELECTRO_AGENT_NAME,
        'scene': [SceneEnum.PILOTEYE_ELECTRO],
        'description': PiloteyeElectroAgentDescription
        + (
            ' Piloteye includes a built-in molecule library (thus no SMILES '
            'required for these built-in molecules), a complete modeling '
            'pipeline (structure setup, MD and DFT calculations), and '
            'property post-processing, which means it does not depend on '
            'other tools. With one params json as input, it can automatically'
            ' finish the whole modeling and simulation workflow to get the '
            'target properties.'
        ),
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
        'description': 'Perform global structure search with CALYPSO to generate multiple candidate crystal structures for a given composition. Use this tool when the user asks for "randomly generate many structures“ or "structure search" for a formula (e.g. "help me randomly generate 50 SnTe structures"). It is suitable for exploring different configurations and polymorphs for specified elements. Requires valid element inputs and an accessible CALYPSO environment.',
        'args_setting': 'Parameter guidance: n_tot=10–30 gives reasonable diversity without excessive cost. Elements must be from the supported list (H–Bi, Ac–Pu). Output is a set of POSCAR files; downstream relaxation is strongly recommended.',
    },
    'generate_crystalformer_structures': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.CONDITIONAL_GENERATE],
        'description': 'Generate crystal structures based on specified conditional attributes (bandgap, shear_modulus, bulk_modulus, superconducting critical temperature, sound) and user-provided space groups.',
        'args_setting': 'Parameter guidance: Supported properties: bandgap (eV), shear_modulus, bulk_modulus (both log₁₀ GPa), superconducting ambient_pressure/high_pressure (K), sound (m/s). For target_type="minimize", use small target (e.g., 0.1) and low alpha (0.01); for "equal", "greater", "less", use alpha=1.0. mc_steps=500 balances convergence and speed; increase to 2000 for high-accuracy targets. sample_num=20–100 recommended; distribute across space groups if random_spacegroup_num>0. Critical: Space group must be explicitly specified by the user — no defaults or auto-inference.',
    },
    'make_supercell_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Make supercell expansion based on structure file. Requires valid structure file input.',
        'args_setting': "Parameter guidance: Primarily follow user's instrucution. If not specified, firstly get structure information to understand the raw lattice. An ideal supercell for computation is isotropic. For example, the raw lattice is (4 A, 10 A, 12 A, 90 deg, 90 deg, 90 deg), the supercell should be 5 × 2 × 2. 30-50 angstrom is often appropriate for simulations. Avoid overly large cells unless needed for long-range interactions.",
        'bypass_confirmation': True,
    },
    'build_bulk_structure_by_template': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'CAN ONLY: build structures for elements with packing of sc, fcc, bcc, hcp; and compounds like rhombohedral, orthorhombic, monoclinic, diamond, zincblende, rocksalt, cesiumchloride, fluorite, and wurtzite. CANNOT DO: build structures for complex structures with elements more than two or molecular crystals. ',
        'args_setting': f'Parameter guidance: Lattice constant requirements due to symmetry constraints: sc/fcc/bcc/diamond/rocksalt/cesiumchloride/zincblende/fluorite → only a; hcp/wurtzite → a and c; orthorhombic/monoclinic → a, b, c. Set conventional=True by default unless primitive cell is explicitly required. For elements, use element symbols; for compounds, use chemical formula (e.g., "NaCl"). {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'build_surface_slab': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build surface slab structures based on bulk structure file miller indices. Needs to provide bulk structure file.',
        'args_setting': f'Parameter guidance: Prefer slab_size_mode="layers" with slab_size_value=4–6 for stability; or "thickness" with ≥12 Å for electronic convergence. Use vacuum=15–20 Å to minimize spurious interactions. For polar surfaces or systems with strong dipoles, increase vacuum to ensure the electrostatic potential flattens in the vacuum region. Enable repair=True for covalent materials (e.g., drug-like molecule crystals, oragnic-inorganic hybrids, MOFs); Set false for regular sphrical-like inorganic crystals. Gets slow if set True. Default termination="auto" usually selects the most stoichiometric termination. {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'build_surface_adsorbate': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build a surface–adsorbate structure by placing a molecular adsorbate onto a given surface slab at a specified lateral position (fractional coordinates or site keyword) and height above the surface. Outputs a combined CIF file. Requires valid surface and adsorbate structure files',
        'args_setting': f'Parameter guidance: height=2.0 Å is typical for physisorption; reduce to 1.5–1.8 Å for chemisorption (e.g., CO on Pt). For high-symmetry sites, use string keywords ("ontop", "fcc", "hcp"); for custom placement, supply [x, y] fractional coordinates. {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'build_surface_interface': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build a heterointerface by stacking two slab structures along a chosen axis with specified interlayer distance and lattice-matching tolerance. Performs basic in-plane strain checking and outputs the combined interface as a CIF file. Requires pre-constructed slab inputs.',
        'args_setting': f'Parameter guidance: Keep max_strain=0.05 (5%) for physical relevance; relax only if intentional strain engineering is intended. Try combinding make_supercell and get_structural_info to obtain the appropriate size of the two slabs. interface_distance=2.5 Å is safe for van der Waals gaps; reduce to 1.8–2.0 Å for covalent bonding (e.g., heterostructures with orbital overlap). {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'add_cell_for_molecules': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Add a periodic simulation cell to a molecular structure for isolated-molecule calculations.',
        'args_setting': f'Parameter guidance: For non-periodic system aiming to run calculations with periodic boundary conditions required (e.g., DFT calculations with ABACUS), use add_cell_for_molecules to put the system in a large cell. Default cell [10, 10, 10] Å and vacuum = 5 Å are suitable for most gas-phase molecules; increase to ≥15 Å and ≥8 Å vacuum for polar or diffuse systems (e.g., anions, excited states). {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'build_bulk_structure_by_wyckoff': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build bulk crystal by specifying space group and, for each *distinct* atomic species, exactly one Wyckoff position (e.g., "4a") with its representative coordinates (x, y, z).',
        'args_setting': f'Parameter guidance: Space Group: Integer (e.g., 225) or Symbol (e.g., "Fm-3m"). Wyckoff Consistency: The provided coordinates must mathematically belong to the specific Wyckoff position (e.g., if using position 4a at (0,0,0), do not input (0.5, 0.5, 0) just because it\'s in the same unit cell; only input the canonical generator). Lattice: Angles in degrees, lengths in Å. Fractional Coordinates: Must be in [0, 1). Strictly Use the Asymmetric Unit: You must provide only the generating coordinates for each Wyckoff orbit. Do NOT Pre-calculate Symmetry: The function will automatically apply all space group operators to your input. If you manually input coordinates that are already symmetry-equivalent (e.g., providing both (x, y, z) and (-x, -y, -z) in a centrosymmetric structure), the function will generate them again, causing catastrophic atom overlapping. Redundancy Rule: Before adding a coordinate, check if it can be generated from an existing input coordinate via any operator in the Space Group. If yes, discard it. One Wyckoff letter = One coordinate triplet input. {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'build_molecule_structures_from_smiles': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build a 3D molecular structure from a SMILES string.',
        'args_setting': f'{STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'make_doped_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Generate doped crystal structures by randomly substituting selected atomic sites with specified dopant species at given concentrations. Needs valid host structure input.',
        'args_setting': f'Parameter guidance: Fractions are applied per-site; actual doping % may differ slightly in small cells — recommend ≥2×2×2 supercells for <10% doping. Covalent ions (ammonium, formamidinium, etc.) are supported via built-in library; specify by name (e.g., "ammonium"). {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'make_amorphous_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Generate amorphous molecular structures by randomly filling molecules into a periodic box based on specified box size, density, or molecule count. Supports automatic calculation of missing parameters and avoids overlaps during placement. Produces an initial amorphous configuration for further relaxation or molecular dynamics simulations. Needs valid molecule structure input.',
        'args_setting': f'Parameter guidance: Input Constraint: Specify exactly two of: box_size, density, molecule_numbers. The third is derived. Density Regimes (CRITICAL): Solids/Liquids: Target ~0.9–1.2 g/cm³ (e.g., water ~1.0, polymers ~1.1). Gases/Vapors: Target orders of magnitude lower (e.g., ~0.001–0.002 g/cm³ for STP gases). Warning: Do not apply default liquid densities to gas inputs. If simulating a specific pressure, pre-calculate the required number of molecules N for the given Box Volume V (using Ideal Gas Law), then fix box_size and molecule_numbers. Composition: Use composition for multi-component mixtures; otherwise equal molar ratios are assumed. Packing Geometry: Box Size: For gases, ensure the box is large enough (usually >15 Å) to minimize unphysical periodic self-interactions, even if the density is low. {STRUCTURE_BUILDING_SAVENAME}',
        'bypass_confirmation': True,
    },
    'get_structure_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.UNIVERSAL],
        'description': 'Extract key structural descriptors from a given crystal structure file, including lattice parameters, chemical formula, atomic composition, cell volume, crystallographic density, and molar mass.',
        'args_setting': '',
    },
    'get_molecule_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.UNIVERSAL],
        'description': 'Extract key structural descriptors from a given molecular structure file.',
        'args_setting': '',
    },
    'run_superconductor_optimization': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': 'Perform geometry optimization for a given superconducting structure using DPA under ambient or high-pressure conditions; this tool is only for superconductor geometry relaxation with format of (e.g., CIF or POSCAR).',
    },
    'calculate_superconductor_enthalpy': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': 'Compute the enthalpy of a given superconducting material using DPA under ambient or high-pressure conditions, build a convex hull within the provided superconducting candidates, and identify superconductors with energy-above-hull below a user-specified threshold; this tool is only for enthalpy and stability screening of superconductors and must not be used for generic materials.',
    },
    'predict_superconductor_Tc': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': 'This tool MUST be called whenever the user asks to predict, estimate, or compute the superconducting critical temperature (Tc) of any material. Use this tool to perform Tc prediction under ambient or high-pressure conditions using the DPA model. If the user mentions Tc, superconductivity, critical temperature, or superconducting transition, always invoke this tool.',
    },
    'screen_superconductor': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': 'Given a user-provided list of candidate structures or compounds, this tool predicts their superconducting critical temperatures (Tc) using DPA, checks their stability (energy above hull), and returns an ordered screening result. This tool should ONLY be called when the user explicitly provides multiple candidate materials for Tc screening. It must NOT be used for querying known superconductors, global Tc records, or general Tc questions.',
    },
    'predict_thermoelectric_properties': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': 'Predict thermoelectric-related properties for a given material using DPA , including band gap in eV, Seebeck coefficient in Volt/K, power factor in uW/cm.2K, effective mass, shear modulus GPa, and bulk modulus in GPa; this tool does not compute thermal conductivity and is only for thermoelectric property prediction, not for generic structure optimization or unrelated property queries.',
    },
    'run_pressure_optimization': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': 'Perform geometry optimization for given thermoelectric materials using DPA under a user-specified pressure; this tool is only for structural relaxation of thermoelectric systems and should not be used for thermoelectric property prediction or non-thermoelectric materials.',
    },
    'calculate_thermoele_enthalp': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': 'Compute the enthalpy of given thermoelectric materials using DPA under a specified pressure, construct a convex hull among the thermoelectric candidates, and select structures with energy-above-hull below a user-defined threshold; this tool is only for enthalpy and stability screening of thermoelectric materials and must not be used for non-thermoelectric systems or other property predictions.',
    },
    'screen_thermoelectric_candidate': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': 'Screen potential thermoelectric materials from a user-provided set of candidate structures using DPA under a specified pressure, internally predicting all required thermoelectric properties to identify promising candidates; this tool requires the user to supply multiple input structures and does not perform screening without provided candidates.',
    },
    'traj_analysis_msd': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [],
        'description': '',
    },
    'traj_analysis_rdf': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': '',
    },
    'traj_analysis_solvation': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': '',
    },
    'traj_analysis_bond': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': '',
    },
    'traj_analysis_react': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': '',
    },
    'visualize_data': {
        'belonging_agent': VisualizerAgentName,
        'scene': [SceneEnum.VISUALIZE_DATA, SceneEnum.UNIVERSAL],
        'description': 'Automatically analyze materials science data files (CSV, Excel, JSON, TXT, DAT), identify the data structure with regular expression, and visualize the data with plots.',
        'bypass_confirmation': True,
    },
    'convert_lammps_structural_format': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': 'Convert structure file to LAMMPS format using pymatgen and dpdata.',
    },
    'run_lammps': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': 'Run LAMMPS simulation, capable of multi-stage simulation (including energy minimization and MD simulations) in one job. In this tool, the structure file must be in LAMMPS format. Use `convert_lammps_structural_format` to convert the structure file to LAMMPS format before running unless user explicitly states that the structure file is in LAMMPS format.',
    },
    'orchestrate_lammps_input': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': 'Automatically generate LAMMPS input script based on natural language description using LLM, capable of multi-stage tasks, including energy minimization, MD simulation and on-the-fly property computations (e.g. MSD, RDF, density, stress) within complicated constraints, in one script with appropriate parameters or user-appointed parameters. CAN DO: support recognition of potential file type and generate appropriate formats accordingly, including DeePMD and classical force fields.',
    },
    'search-papers-enhanced': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.LITERATURE],
        'description': 'Search for research papers and recent progress related to a topic',
        'args_setting': f"""
            If not specified, apply start_time=2020-01-01, end_time={TODAY}, page_size not less than 150. When constructing query word list and question: (i) use English to ensure professionalism; (ii) avoid broad keywords like 'materials science', 'chemistry', 'progress'; (iii) extract specific, technically relevant keywords such as material names, molecular identifiers, mechanism names, property names, or application contexts; (iv) if the user's query is broad, decompose the concept into technical terms and generate concrete, research-usable keywords; (v) when translating, no segmenting composite technical noun phrases unless it is an established scientific usage. If ambiguous in Chinese, preserve the maximal-span term and translate it as a whole before considering refinement, including identifying: representative subfields, canonical mechanisms, prototypical material classes, commonly studied performance metrics, key methodologies or application contexts. These keywords must be specific enough to retrieve meaningful literature and avoid domain-level noise.
        """,
        'summary_prompt': PAPER_SEARCH_AGENT_INSTRUCTION,
        'bypass_confirmation': True,
    },
    'build_convex_hull': {
        'belonging_agent': ConvexHullAgentName,
        'scene': [SceneEnum.CONVEXHULL],
        'description': 'Build a convex hull for general materials by optimizing user-provided structures with Deep Potential, predicting their enthalpies, and assessing thermodynamic stability via energy above hull to identify on-hull or near-hull stable candidates.',
    },
    'NMR_search_tool': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': 'Database search for molecules based on NMR(nmr) spectroscopic data.',
    },
    'NMR_predict_tool': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': 'Predict NMR(nmr) spectroscopic properties for molecular structures. Calculates simulated 1H and 13C NMR chemical shifts for given molecular structures (SMILES strings). Useful for validating structural assignments and comparing predicted spectra with reference spectra for similarity scoring. Input SMILES strings to simulate NMR spectra. Returns list of molecules with predicted NMR chemical shifts and spectral similarity scores.',
    },
    'NMR_reverse_predict_tool': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': 'Generates candidate molecular structures from Nuclear Magnetic Resonance (NMR) spectroscopic data.',
    },
    'extract_info_from_webpage': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': 'Extract key information from a given WEBPAGE URL, including scientific facts, data, and research findings.',
        'summary_prompt': WEBPAGE_PARSING_AGENT_INSTRUCTION,
        'bypass_confirmation': True,
    },
    'web-search': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': 'Perform web searches specifically for what, why, and how question types, excluding command- or instruction-type queries. The tool returns only URL, title, and snippet, which makes it suitable for concise factual lookups (what-questions) and simple causal or explanatory lookups (basic why-questions). Should follow up by `extract_info_from_webpage` for completed contents.',
        'summary_prompt': WEB_SEARCH_AGENT_INSTRUCTION,
        'bypass_confirmation': True,
    },
    'xrd_parse_file': {
        'belonging_agent': XRD_AGENT_NAME,
        'scene': [SceneEnum.XRD],
        'description': 'Parse raw XRD data files (e.g., .xrdml, .xy, .csv). Performs preprocessing (baseline correction, smoothing), extracts features (peaks, FWHM, grain size), and saves processed data and visualization configurations to local files. Returns file paths for downstream tasks like phase identification.',
    },
    'xrd_phase_identification': {
        'belonging_agent': XRD_AGENT_NAME,
        'scene': [SceneEnum.XRD],
        'description': 'Identify crystalline phases in an XRD pattern using a processed CSV file (generated by `xrd_parse_file`). Supports filtering candidates by chemical composition (include/exclude elements). Returns the top N matching phases and generates a comparison chart between the experimental data and standard PDF cards.',
    },
    'get_electron_microscope_recognize': {
        'belonging_agent': Electron_Microscope_AGENT_NAME,
        'scene': [SceneEnum.Electron_Microscope],
        'description': 'Analyze electron microscope images (e.g., TEM, SEM) to detect and classify particles, assess morphology, and evaluate image quality. This tool identifies microstructural features such as particle boundaries, occlusions, and invalid regions, while extracting geometric properties like area, perimeter, diameter, and shape factors using advanced computer vision techniques.',
    },
    'llm_tool': {
        'belonging_agent': TOOL_AGENT_NAME,
        'scene': [],
        'description': '',
        'bypass_confirmation': True,
    },
    'physical_adsorption_echart_data': {
        'belonging_agent': Physical_Adsorption_AGENT_NAME,
        'scene': [SceneEnum.PHYSICAL_ADSORPTION],
        'description': 'Analyze physical adsorption (gas adsorption) instrument reports.',
    },
    'file_parse': {
        'belonging_agent': FILE_PARSE_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': 'Universal File Parsing Tool.Used to parse various file contents, including but not limited to TXT, PDF, Word, Excel, and text files, to extract key information and data.',
        'bypass_confirmation': True,
    },
}

AGENT_TOOLSET_CONFIG = {
    ABACUS_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-22618/abacusagenttools-matmaster-new-tool:v0.2.3',
        'machine_type': 'c32_m128_cpu',
    },
    ApexAgentName: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.1',
        'machine_type': 'c2_m4_cpu',
    },
    LAMMPS_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/lammps-agent:9ae769be',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    VASPKIT_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-16664/vaspkit-agent:0.0.1',
        'machine_type': 'c2_m8_cpu',
    },
    DPACalulator_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/dpa-calculator:a86b37cc',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    COMPDART_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/dpa-calculator:50e69ca3',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    PILOTEYE_ELECTRO_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-13375/piloteye:mcpv03',
        'machine_type': 'c2_m8_cpu',
    },
    ORGANIC_REACTION_AGENT_NAME: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-13364/autots:0.1.0',
        'machine_type': 'c32_m128_cpu',
    },
    HEA_assistant_AgentName: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-485756/mcphub:heafinal',
        'machine_type': 'c2_m4_cpu',
    },
    ThermoelectricAgentName: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:20',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    SuperconductorAgentName: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:20',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    FinetuneDPAAgentName: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:20',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    ConvexHullAgentName: {
        'image': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-convexhull:20',
        'machine_type': 'c16_m64_1 * NVIDIA 4090',
    },
    StructureGenerateAgentName: {
        'image': 'registry.dp.tech/dptech/dpa-calculator:46bc2c88',
        'machine_type': 'c8_m32_1 * NVIDIA 4090',
    },
}
