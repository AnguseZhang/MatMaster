from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum
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
from agents.matmaster_agent.sub_agents.LAMMPS_agent.constant import LAMMPS_AGENT_NAME
from agents.matmaster_agent.sub_agents.MrDice_agent.bohriumpublic_agent.constant import (
    BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.mofdb_agent.constant import (
    MOFDB_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.openlam_agent.constant import (
    OPENLAM_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.MrDice_agent.optimade_agent.constant import (
    OPTIMADE_DATABASE_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.perovskite_agent.constant import (
    PerovskiteAgentName,
)
from agents.matmaster_agent.sub_agents.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ScienceNavigator_agent.constant import (
    SCIENCE_NAVIGATOR_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.ssebrain_agent.constant import (
    SSEBRAIN_AGENT_NAME,
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
from agents.matmaster_agent.sub_agents.visualizer_agent.constant import (
    VisualizerAgentName,
)

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
        'description': 'Evaluate vacancy formation energies by relaxing supercells with one atom removed',
    },
    'apex_optimize_structure': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.OPTIMIZE_STRUCTURE, SceneEnum.APEX],
        'description': 'Perform geometry optimization of a crystal(recommend alloy system), relaxing atomic positions and optionally the unit cell.',
    },
    'apex_calculate_interstitial': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.INTERSTITIAL_FORMATION_ENERGY],
        'description': 'Insert interstitial atoms into a host lattice to compute formation energies across candidate sites.',
    },
    'apex_calculate_elastic': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.ELASTIC_CONSTANT],
        'description': 'Apply small strains to the lattice to extract elastic constants and derived moduli.',
    },
    'apex_calculate_surface': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.SURFACE_ENERGY],
        'description': 'Execute a workflow of surfacce energy calculation. CANNOT build slab structures',
    },
    'apex_calculate_eos': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.EOS],
        'description': 'Scan volumes around equilibrium, relax internal coordinates, and build an equation-of-state energy–volume curve.',
    },
    'apex_calculate_phonon': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.PHONON],
        'description': 'Perform supercell finite-displacement calculations, relax configurations, and assemble phonon spectra',
    },
    'apex_calculate_gamma': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.STACKING_FAULT_ENERGY],
        'description': 'Construct and relax sliding slabs to map generalized stacking-fault energies along specified slip paths.',
    },
    'get_target_info': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [],
        'description': '',
    },
    'unielf_inference': {
        'belonging_agent': CHEMBRAIN_AGENT_NAME,
        'scene': [SceneEnum.POLYMER],
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
        'description': 'CAN DO: composition optimization targeting specific properties; CANNOT DO: build doping structures based on given composition',
    },
    'extract_material_data_from_pdf': {
        'belonging_agent': DocumentParserAgentName,
        'scene': [SceneEnum.LITERATURE, SceneEnum.STRUCTURAL_INFORMATICS],
        'description': 'Read and extract contents from PDF-formatted document files. Outputs information of materials involved and methodologies, supporting additional information required by users. CANNOT retrieve data from the internet.',
    },
    'optimize_structure': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': 'Perform geometry optimization of a crystal or molecular structure. Supports relaxation of atomic positions and optionally the unit cell.',
    },
    'run_molecular_dynamics': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.MOLECULAR_DYNAMICS],
        'description': 'Run molecular dynamics simulations using ASE interface. CAN DO: run MD with DPA pretrained model or user-uploaded DeePMD mdoel; run NVE, NVT, NPT MD with logging basic thermodynamics and lattice parameters. CANNOT DO: run MD with classical force-field or ab initio (or DFT) methods; nor run complicated MD like shock conditions, or with complicated on-the-fly stastistics like RDF, MSD.',
    },
    'calculate_phonon': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.PHONON],
        'description': 'Compute phonon properties. Generates displaced supercells, calculates interatomic forces, and derives phonon dispersion, thermal properties, and optional total/projected DOS. Outputs band structures, entropy, free energy, heat capacity, and maximum phonon frequencies. Requires optimized structure as input.',
    },
    'calculate_elastic_constants': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.ELASTIC_CONSTANT],
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
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': '',
    },
    'HEA_predictor': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': '',
    },
    'generate_binary_phase_diagram': {
        'belonging_agent': HEACALCULATOR_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': '',
    },
    'fetch_structures_with_filter': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures from multiple OPTIMADE-compatible databases using raw OPTIMADE filter strings (elements, chemical formulas, logical combinations) across providers like alexandria, cod, mp, oqmd, tcod.',
    },
    'fetch_structures_with_spg': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures filtered by specific space group numbers (1-230) or mineral/structure types (e.g., rutile, spinel, perovskite) combined with base filters from OPTIMADE-compatible databases.',
    },
    'fetch_structures_with_bandgap': {
        'belonging_agent': OPTIMADE_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures filtered by band gap range (min/max in eV) combined with base filters (elements, formulas) from OPTIMADE-compatible databases that provide band gap data.',
    },
    'fetch_bohrium_crystals': {
        'belonging_agent': BOHRIUMPUBLIC_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures from the Bohrium Public database (includes Materials Project data) with flexible filtering by formula, elements, space group, atom counts, predicted formation energy range, and band gap range, supporting exact or contains match modes.',
    },
    'fetch_openlam_structures': {
        'belonging_agent': OPENLAM_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Retrieve crystal structures from the OpenLAM database filtered by chemical formula, energy range, and submission time, with output in CIF or JSON format.',
    },
    'fetch_mofs_sql': {
        'belonging_agent': MOFDB_DATABASE_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': 'Execute SQL queries against the MOF database with support for complex multi-table joins, window functions, CTEs, and statistical analysis for advanced MOF property queries and composition analysis.',
    },
    'calculate_reaction_profile': {
        'belonging_agent': ORGANIC_REACTION_AGENT_NAME,
        'scene': [SceneEnum.REACTION],
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
        'description': 'Generate candidate crystal structures based on specified chemical species and number of configurations. Employs particle-swarm algorithms to produce stable crystal candidates. Requires valid element inputs and accessible CALYPSO environment',
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
        'args_setting': 'Parameter guidance: Primarily follow user\'s instrucution. If not specified, firstly get structure information to understand the raw lattice. An ideal supercell for computation is isotropic. For example, the raw lattice is (4 A, 10 A, 12 A, 90 deg, 90 deg, 90 deg), the supercell should be 5 × 2 × 2. 30-50 angstrom is often appropriate for simulations. Avoid overly large cells unless needed for long-range interactions.',
    },
    'build_bulk_structure_by_template': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'CAN ONLY: build structures for elements with packing of sc, fcc, bcc, hcp; and compounds like rhombohedral, orthorhombic, monoclinic, diamond, zincblende, rocksalt, cesiumchloride, fluorite, and wurtzite. CANNOT DO: build structures for complex structures with elements more than two or molecular crystals. ',
        'args_setting': 'Parameter guidance: Lattice constant requirements due to symmetry constraints: sc/fcc/bcc/diamond/rocksalt/cesiumchloride/zincblende/fluorite → only a; hcp/wurtzite → a and c; orthorhombic/monoclinic → a, b, c. Set conventional=True by default unless primitive cell is explicitly required. For elements, use element symbols; for compounds, use chemical formula (e.g., "NaCl").',
    },
    'build_molecule_structure_from_g2database': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build molecule structure from g2 database.',
        'args_setting': 'ASE G2 database molecules include PH3, P2, CH3CHO, H2COH, CS, OCHCHO, C3H9C, CH3COF, CH3CH2OCH3, HCOOH, HCCl3, HOCl, H2, SH2, C2H2, C4H4NH, CH3SCH3, SiH2_s3B1d, CH3SH, CH3CO, CO, ClF3, SiH4, C2H6CHOH, CH2NHCH2, isobutene, HCO, bicyclobutane, LiF, Si, C2H6, CN, ClNO, S, SiF4, H3CNH2, methylenecyclopropane, CH3CH2OH, F, NaCl, CH3Cl, CH3SiH3, AlF3, C2H3, ClF, PF3, PH2, CH3CN, cyclobutene, CH3ONO, SiH3, C3H6_D3h, CO2, NO, trans-butane, H2CCHCl, LiH, NH2, CH, CH2OCH2, C6H6, CH3CONH2, cyclobutane, H2CCHCN, butadiene, C, H2CO, CH3COOH, HCF3, CH3S, CS2, SiH2_s1A1d, C4H4S, N2H4, OH, CH3OCH3, C5H5N, H2O, HCl, CH2_s1A1d, CH3CH2SH, CH3NO2, Cl, Be, BCl3, C4H4O, Al, CH3O, CH3OH, C3H7Cl, isobutane, Na, CCl4, CH3CH2O, H2CCHF, C3H7, CH3, O3, P, C2H4, NCCN, S2, AlCl3, SiCl4, SiO, C3H4_D2d, H, COF2, 2-butyne, C2H5, BF3, N2O, F2O, SO2, H2CCl2, CF3CN, HCN, C2H6NH, OCS, B, ClO, C3H8, HF, O2, SO, NH, C2F4, NF3, CH2_s3B1d, CH3CH2Cl, CH3COCl, NH3, C3H9N, CF4, C3H6_Cs, Si2H6, HCOOCH3, O, CCH, N, Si2, C2H6SO, C5H8, H2CF2, Li2, CH2SCH2, C2Cl4, C3H4_C3v, CH3COCH3, F2, CH4, SH, H2CCO, CH3CH2NH2, Li, N2, Cl2, H2O2, Na2, BeH, C3H4_C2v, NO2',
    },
    'build_surface_slab': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build surface slab structures based on bulk structure file miller indices. Needs to provide bulk structure file.',
        'args_setting': 'Parameter guidance: Prefer slab_size_mode="layers" with slab_size_value=4–6 for stability; or "thickness" with ≥12 Å for electronic convergence. Use vacuum=15–20 Å to minimize spurious interactions. For polar surfaces or systems with strong dipoles, increase vacuum to ensure the electrostatic potential flattens in the vacuum region. Enable repair=True for covalent materials (e.g., drug-like molecule crystals, oragnic-inorganic hybrids, MOFs); Set false for regular sphrical-like inorganic crystals. Gets slow if set True. Default termination="auto" usually selects the most stoichiometric termination.',
    },
    'build_surface_adsorbate': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build a surface–adsorbate structure by placing a molecular adsorbate onto a given surface slab at a specified lateral position (fractional coordinates or site keyword) and height above the surface. Outputs a combined CIF file. Requires valid surface and adsorbate structure files',
        'args_setting': 'Parameter guidance: height=2.0 Å is typical for physisorption; reduce to 1.5–1.8 Å for chemisorption (e.g., CO on Pt). For high-symmetry sites, use string keywords ("ontop", "fcc", "hcp"); for custom placement, supply [x, y] fractional coordinates.',
    },
    'build_surface_interface': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build a heterointerface by stacking two slab structures along a chosen axis with specified interlayer distance and lattice-matching tolerance. Performs basic in-plane strain checking and outputs the combined interface as a CIF file. Requires pre-constructed slab inputs.',
        'args_setting': 'Parameter guidance: Keep max_strain=0.05 (5%) for physical relevance; relax only if intentional strain engineering is intended. Try combinding make_supercell and get_structural_info to obtain the appropriate size of the two slabs. interface_distance=2.5 Å is safe for van der Waals gaps; reduce to 1.8–2.0 Å for covalent bonding (e.g., heterostructures with orbital overlap).',
    },
    'add_cell_for_molecules': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Add a periodic simulation cell to a molecular structure for isolated-molecule calculations.',
        'args_setting': 'Parameter guidance: For non-periodic system aiming to run calculations with periodic boundary conditions required (e.g., DFT calculations with ABACUS), use add_cell_for_molecules to put the system in a large cell. Default cell [10, 10, 10] Å and vacuum = 5 Å are suitable for most gas-phase molecules; increase to ≥15 Å and ≥8 Å vacuum for polar or diffuse systems (e.g., anions, excited states).',
    },
    'build_bulk_structure_by_wyckoff': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build bulk crystal by specifying space group and, for each *distinct* atomic species, exactly one Wyckoff position (e.g., "4a") with its representative coordinates (x, y, z). '
        'CRITICAL RULE: A single Wyckoff position (e.g., "4a") defines a full, closed set of symmetry-equivalent points (an orbit); DO NOT assign multiple atoms to different points *within the same Wyckoff position*, and DO NOT assign atoms to Wyckoff positions that are symmetry-equivalent under the space group. '
        'The multiplicity of each Wyckoff position (the number prefix) gives the count of atoms generated for that species; the total atom count is the sum of all multiplicities.',
        'args_setting': 'Parameter guidance: Space Group: Integer (e.g., 225) or Symbol (e.g., "Fm-3m"). Wyckoff Consistency: The provided coordinates must mathematically belong to the specific Wyckoff position (e.g., if using position 4a at (0,0,0), do not input (0.5, 0.5, 0) just because it\'s in the same unit cell; only input the canonical generator). Lattice: Angles in degrees, lengths in Å. Fractional Coordinates: Must be in [0, 1). Strictly Use the Asymmetric Unit: You must provide only the generating coordinates for each Wyckoff orbit. Do NOT Pre-calculate Symmetry: The function will automatically apply all space group operators to your input. If you manually input coordinates that are already symmetry-equivalent (e.g., providing both (x, y, z) and (-x, -y, -z) in a centrosymmetric structure), the function will generate them again, causing catastrophic atom overlapping. Redundancy Rule: Before adding a coordinate, check if it can be generated from an existing input coordinate via any operator in the Space Group. If yes, discard it. One Wyckoff letter = One coordinate triplet input.',
    },
    'build_molecule_structures_from_smiles': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Build a 3D molecular structure from a SMILES string.',
        'args_setting': '',
    },
    'make_doped_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Generate doped crystal structures by randomly substituting selected atomic sites with specified dopant species at given concentrations. Needs valid host structure input.',
        'args_setting': 'Parameter guidance: Fractions are applied per-site; actual doping % may differ slightly in small cells — recommend ≥2×2×2 supercells for <10% doping. Covalent ions (ammonium, formamidinium, etc.) are supported via built-in library; specify by name (e.g., "ammonium").',
    },
    'make_amorphous_structure': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': 'Generate amorphous molecular structures by randomly filling molecules into a periodic box based on specified box size, density, or molecule count. Supports automatic calculation of missing parameters and avoids overlaps during placement. Produces an initial amorphous configuration for further relaxation or molecular dynamics simulations. Needs valid molecule structure input.',
        'args_setting': 'Parameter guidance: Input Constraint: Specify exactly two of: box_size, density, molecule_numbers. The third is derived. Density Regimes (CRITICAL): Solids/Liquids: Target ~0.9–1.2 g/cm³ (e.g., water ~1.0, polymers ~1.1). Gases/Vapors: Target orders of magnitude lower (e.g., ~0.001–0.002 g/cm³ for STP gases). Warning: Do not apply default liquid densities to gas inputs. If simulating a specific pressure, pre-calculate the required number of molecules N for the given Box Volume V (using Ideal Gas Law), then fix box_size and molecule_numbers. Composition: Use composition for multi-component mixtures; otherwise equal molar ratios are assumed. Packing Geometry: Box Size: For gases, ensure the box is large enough (usually >15 Å) to minimize unphysical periodic self-interactions, even if the density is low.',
    },
    'get_structure_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURAL_INFORMATICS],
        'description': 'Extract key structural descriptors from a given crystal structure file, including lattice parameters, chemical formula, atomic composition, cell volume, crystallographic density, and molar mass.',
        'args_setting': '',
    },
    'get_molecule_info': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURAL_INFORMATICS],
        'description': 'Extract key structural descriptors from a given molecular structure file.',
        'args_setting': '',
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
    'visualize_data': {
        'belonging_agent': VisualizerAgentName,
        'scene': [SceneEnum.VISUALIZE_DATA],
        'description': 'Automatically analyze materials science data files (CSV, Excel, JSON, TXT, DAT), identify the data structure with regular expression, and visualize the data with plots.',
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
    'search-papers-normal': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.LITERATURE],
        'description': 'Standard version of searching academic papers based on author information',
    },
    'search-papers-enhanced': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.LITERATURE],
        'description': 'Intelligent enhanced paper search system based on keywords and research questions',
    },
}
