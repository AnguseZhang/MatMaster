from enum import Enum


class SceneEnum(str, Enum):
    STRUCTURE_GENERATE = 'structure_generate'
    DATABASE_SEARCH = 'database_search'
    OPTIMIZE_STRUCTURE = 'optimize_structure'
    MOLECULAR_DYNAMICS = 'molecular_dynamics'
    PHONON = 'phonon'
    CompositionOptimization = 'composition_optimization'
    SMILES = 'smiles'
    LITERATURE = 'literature'
    JobResultRetrieval = 'job_result_retrieval'
    DPA = 'DPA'
    APEX = 'APEX'
    ABACUS = 'ABACUS'
    VISUALIZE_DATA = 'visualize_data'
