from enum import Enum


class SceneEnum(str, Enum):
    STRUCTURE_GENERATE = 'structure_generate'
    DATABASE_SEARCH = 'database_search'
    OPTIMIZE_STRUCTURE = 'optimize_structure'
    VACANCY_FORMATION_ENERGY = 'vacancy_formation_energy'
    INTERSTITIAL_FORMATION_ENERGY = 'interstitial_formation_energy'
    ELASTIC_CONSTANT = 'elastic_constant'
    MOLECULAR_DYNAMICS = 'molecular_dynamics'
    SURFACE_ENERGY = 'surface_energy'
    STACKING_FAULT_ENERGY = 'stacking_fault_energy'
    EOS = 'eos'
    PHONON = 'phonon'
    CompositionOptimization = 'composition_optimization'
    SMILES = 'smiles'
    LITERATURE = 'literature'
    JobResultRetrieval = 'job_result_retrieval'
    DPA = 'DPA'
    APEX = 'APEX'
    ABACUS = 'ABACUS'
    VISUALIZE_DATA = 'visualize_data'
