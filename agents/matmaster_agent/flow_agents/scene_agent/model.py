from enum import Enum


class DescriptiveEnum(str, Enum):
    """带有描述的枚举基类"""

    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    def __str__(self):
        return self.value


class SceneEnum(DescriptiveEnum):
    # Special Scene
    UNIVERSAL = ('universal', 'Applicable to all scenarios')
    NEED_UPLOAD_FILE = ('need_upload_file', '')

    # literature
    LITERATURE = (
        'literature',
        'Involving research papers retrieval, content extraction, or progress/trends analysis. e.g. Search for research papers on [topic], extract key findings from the abstract of papers, analyze research progress/trends in [field], and finalize by in-depth discussion/summary',
    )
    WEB_SEARCH = (
        'general_web_search',
        'Involving concept query or procedure query. e.g. `What is [concept]`, `How to do [procedure]`, `Why is [phenomena]`. Not suitable for final research progress search tasks unless user requests.',
    )
    WEB_PARSING = (
        'webpage_parsing',
        'Involving extracting specific information from a given webpage URL.e.g. `Extract key information from the webpage at [URL]`, `Summarize the main points from the article at [URL]` Suitable for detail retrieval tasks after WEB_SEARCH, but usually no need for literature search tasks unless user requests.',
    )

    # database
    DATABASE_SEARCH = ('database_search', '')

    # generate
    STRUCTURE_GENERATE = ('structure_generate', '')
    CONDITIONAL_GENERATE = ('conditional_generate', '')

    # sanitize
    STRUCTURE_SANITIZE = (
        'structure_sanitize',
        'Cleanup experimental crystal structures for computational modeling',
    )

    # calc
    DPA = ('DPA', 'Involving machine learning potentials and DPA')
    APEX = ('APEX', 'Involving first-principles calculation methods using APEX.')
    ABACUS = ('ABACUS', 'Involving first-principles calculation methods using ABACUS.')
    LAMMPS = ('LAMMPS', 'involving LAMMPS-based methods.')
    OPTIMIZE_STRUCTURE = (
        'optimize_structure',
        '3D structure optimization and relaxation',
    )
    VACANCY_FORMATION_ENERGY = ('vacancy_formation_energy', '')
    INTERSTITIAL_FORMATION_ENERGY = ('interstitial_formation_energy', '')
    ELASTIC_CONSTANT = ('elastic_constant', '')
    MOLECULAR_DYNAMICS = ('molecular_dynamics', '')
    SURFACE_ENERGY = ('surface_energy', '')
    STACKING_FAULT_ENERGY = ('stacking_fault_energy', '')
    EOS = ('eos', '')
    Electron_Localization_Function = ('electron_localization_function', '')
    Nudged_Elastic_Band = ('nudged_elastic_band', '')
    PHONON = ('phonon', '')
    SCF = ('scf', 'Self-Consistent Field')
    BAND = ('band', '')
    DENSITY_OF_STATES = ('density_of_states', '')
    REACTION = ('reaction', '')
    BADER_CHARGE_ANALYSIS = ('bader_charge_analysis', '')
    WORK_FUNCTION = ('work_function', '')
    COMPOSITION_OPTIMIZATION = (
        'composition_optimization',
        'Search for optimized multi-component compositions (e.g. alloys) for target properties via genetic algorithm or run_dart_ga.',
    )
    CONVEXHULL = ('convexhull', '')
    DOE = ('doe', '')

    # postprocess
    VISUALIZE_DATA = (
        'data_visualization',
        'Involves visualization or charting requirements',
    )
    POST_MD_ANALYSIS = (
        'post_md_analysis',
        'Use after MD simulations with DPA or LAMMPS, or when user manually upload trajectories.',
    )

    # experiments
    NMR = (
        'NMR',
        'Involves predicting the NMR spectra of organic molecules or deducing molecular structures from NMR spectra',
    )
    XRD = ('XRD', 'Involving XRD raw data analysis and phase identification')
    TPD = ('TPD', 'Involving Temperature Programmed Desorption (TPD) data analysis')
    PHYSICAL_ADSORPTION = ('physical_adsorption', '')
    Electron_Microscope = (
        'electron_microscope',
        'Involving microscopic image analysis',
    )

    # research scene
    MOLECULAR = (
        'MOLECULE',
        'Involving the generation, analysis, and SMILES representation of organic molecules',
    )
    HIGH_ENTROPY_ALLOY = ('high_entropy_alloy', 'Involving high-entropy alloys')
    POLYMER = ('polymer', 'Involving polymers')
    SUPERCONDUCTOR = ('superconductor', 'Involving superconducting materials')
    THERMOELECTRIC = ('thermoelectric', 'Involving thermoelectric materials')
    Solid_State_Electrolyte = (
        'solid_state_electrolyte',
        'Involving solid-state electrolyte materials',
    )
    STEEL = (
        'steel',
        'Scenarios for predicting properties of steel materials or conducting literature research.',
    )
    PILOTEYE_ELECTRO = (
        'piloteye_electro',
        'Liquid electrolyte calculations for conductivity, rdf, diffusion coefficient and redox properties.',
    )
    PEROVSKITE_RESEARCH = (
        'perovskite_research',
        'Research, literature/database search, and semantic mining focused on perovskite solar cells (efficiency, stability, additives, architectures, new molecules).',
    )

    # job/task status only (no planning/thinking needed)
    QUERY_JOB_STATUS = (
        'query_job_status',
        'User only asks to check task/job status or get task results. e.g. 查看任务状态, 查看任务结果, check task status, check task results. Use this when the sole intent is to query status or retrieve results of submitted jobs, not to create a new plan.',
    )
