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
from agents.matmaster_agent.sub_agents.structure_search_agent.constant import (
    STRUCTURE_SEARCH_AGENT_NAME,
)
from agents.matmaster_agent.sub_agents.structure_search_agent.prompt import (
    StructureSearchAgentArgsSetting,
    StructureSearchAgentSummaryPrompt,
    StructureSearchAgentToolDescription,
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
    'abacus_vacancy_formation_energy_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.VACANCY_FORMATION_ENERGY],
        'description': (
            '功能：使用密度泛函理论（DFT）计算金属原子中非带电空位的形成能。\n'
            '使用场景：当需要计算金属结构的空位形成能时使用。\n'
            'ABACUS,空位形成能\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：如泛函、自旋极化、DFT+U、磁矩等。\n'
            '2. 输出：空位形成能。\n'
            '3. 注意事项：仅支持金属原子的非带电空位；计算需使用超胞。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_phonon_dispersion_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.PHONON],
        'description': (
            '功能：使用密度泛函理论（DFT）计算声子色散曲线。\n'
            '使用场景：当需要结构的声子性质和热修正时使用。\n'
            'ABACUS,声子\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：可选超胞、高对称点、k 路径。\n'
            '2. 输出：声子色散能带结构图和热修正。\n'
            '3. 注意事项：需要 DFT 计算；可能需要超胞以提高精度。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_cal_band_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.BAND],
        'description': (
            '功能：使用密度泛函理论（DFT）计算电子能带结构。\n'
            '使用场景：当需要材料的能带结构和带隙时使用。\n'
            'ABACUS,能带\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：可选高对称点、k 路径。\n'
            '2. 输出：能带结构图和带隙。\n'
            '3. 注意事项：基于 DFT；支持 PYATB 或 ABACUS nscf。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_calculation_scf_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.SCF],
        'description': (
            '功能：使用密度泛函理论（DFT）执行自洽场（SCF）计算以计算能量。\n'
            '使用场景：当需要结构的基态能量时使用。\n'
            'ABACUS,SCF\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数。\n'
            '2. 输出：能量。\n'
            '3. 注意事项：基础 SCF 计算；不包含弛豫或其他性质。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
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
    'abacus_dos_run_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.DENSITY_OF_STATES],
        'description': (
            '功能：使用密度泛函理论（DFT）计算态密度（DOS）和投影态密度（PDOS）。\n'
            '使用场景：当需要态密度进行电子结构分析时使用。\n'
            'ABACUS,态密度\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT参数，PDOS 模式（"species"、"species+shell"、"species+orbital"）。\n'
            '2. 输出：DOS 和 PDOS 图。\n'
            '3. 注意事项：基于 DFT；需要弛豫支持。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_badercharge_run_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.BADER_CHARGE_ANALYSIS],
        'description': (
            '功能：使用密度泛函理论（DFT）计算 Bader 电荷。\n'
            '使用场景：当需要进行原子电荷分析时使用。\n'
            'ABACUS,Bader 电荷\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数。\n'
            '2. 输出：每个原子的 Bader 电荷。\n'
            '3. 注意事项：基于 DFT；需要电荷密度计算。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_do_relax_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': (
            '功能：使用密度泛函理论（DFT）执行几何优化（弛豫）。\n'
            '使用场景：当需要优化结构时使用。\n'
            'ABACUS,结构优化\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数；弛豫设置（晶胞、步数、方法、轴）。\n'
            '2. 输出：弛豫后的结构文件。\n'
            '3. 注意事项：基于 DFT 的弛豫。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
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
    'abacus_cal_work_function_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.WORK_FUNCTION],
        'description': (
            '功能：使用密度泛函理论（DFT）计算表面和二维材料的功函数。\n'
            '使用场景：当需要表面材料的功函数时使用。\n'
            'ABACUS,功函数\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数；真空方向、偶极修正。\n'
            '2. 输出：静电势和功函数图。\n'
            '3. 注意事项：适用于表面和二维材料；极性表面有两个功函数。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_run_md_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.MOLECULAR_DYNAMICS],
        'description': (
            '功能：使用密度泛函理论（DFT）执行从头算分子动力学。\n'
            '使用场景：当需要具有 DFT 精度的分子动力学模拟时使用。\n'
            'ABACUS,分子动力学模拟\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数；系综、步数、时间步长、温度。\n'
            '2. 输出：ASE 轨迹文件。\n'
            '3. 注意事项：基于 DFT 的分子动力学；长时间模拟成本高。\n'
            '4. 成本/备注：高 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_cal_elf_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.Electron_Localization_Function],
        'description': (
            '功能：使用密度泛函理论（DFT）计算电子局域化函数（ELF）。\n'
            '使用场景：当需要 ELF 进行键合分析时使用。\n'
            'ABACUS,电子局域函数\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数。\n'
            '2. 输出：ELF 的 Cube 文件。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
    'abacus_eos_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.EOS],
        'description': (
            '功能：使用密度泛函理论（DFT）计算状态方程。\n'
            '使用场景：当需要状态方程曲线和体相性质时使用。\n'
            'ABACUS,EOS\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数。\n'
            '2. 输出：拟合的状态方程图和拟合参数。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
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
            'Outputs: Elastic tensor (Voigt notation), bulk/shear/Young\'s modulus, Poisson ratio.\n'
            'Cannot do / Limits: DFT-based.\n'
            'Cost / Notes: DFT calculation cost; supports relaxation before calculation.'
        ),
        'alternative': ['apex_calculate_elastic', 'calculate_elastic_constants'],
        'self_check': False,
    },
    'abacus_cal_elastic_zh': {
        'belonging_agent': ABACUS_AGENT_NAME,
        'scene': [SceneEnum.ABACUS, SceneEnum.ELASTIC_CONSTANT],
        'description': (
            '功能：使用密度泛函理论（DFT）计算弹性性质。\n'
            '使用场景：当需要弹性常数和模量时使用。\n'
            'ABACUS,弹性常数\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：cif、VASP POSCAR 或 ABACUS STRU 格式的结构文件；\n'
            '   计算参数：DFT 参数。\n'
            '2. 输出：弹性张量（Voigt 记号）、体积/剪切/杨氏模量、泊松比。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本；支持在计算前进行结构弛豫。'
        ),
        'alternative': ['apex_calculate_elastic', 'calculate_elastic_constants'],
        'self_check': False,
    },
    'apex_calculate_vacancy': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.VACANCY_FORMATION_ENERGY],
        'description': (
            'What it does: Evaluate vacancy formation energies by relaxing supercells after creating vacancies internally (removes one atom from a pristine supercell).\n'
            'When to use: When you need vacancy formation energies for a material starting from a pristine crystal.\n'
            'Prerequisites / Inputs: Pristine (defect-free) structure file of the bulk crystal (unit cell or supercell). Do NOT provide a structure that already contains vacancies/defects (missing atoms, partial occupancies, disordered sites), because the tool assumes a complete bulk lattice and will construct vacancies itself; defected inputs may cause errors or invalid energies.\n'
            'Outputs: Vacancy formation energies.\n'
            'Cannot do / Limits: DFT-based.; does not accept pre-defected structures.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': ['abacus_vacancy_formation_energy'],
        'self_check': False,
    },
    'apex_calculate_vacancy_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.VACANCY_FORMATION_ENERGY],
        'description': (
            '功能：通过在内部创建空位后弛豫超胞（从完整超胞中移除一个原子）来评估空位形成能。\n'
            '使用场景：当需要从完整晶体开始计算材料的空位形成能时使用。\n'
            'APEX,空位形成能\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：完整（无缺陷）的体相晶体结构文件（原胞或超胞）。\n'
            '2. 输出：空位形成能。\n'
            '3. 注意事项：基于 DFT；不要提供已包含空位/缺陷的结构（缺失原子、部分占位、无序位点），该工具假设完整的体相晶格并会自行构建空位；提供已有缺陷的结构可能导致错误或无效的能量。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
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
    'apex_optimize_structure_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.OPTIMIZE_STRUCTURE, SceneEnum.APEX],
        'description': (
            '功能：执行晶体的几何优化，弛豫原子位置并可选择弛豫原胞。\n'
            '使用场景：当需要优化的晶体结构时使用，特别适用于合金体系。\n'
            'APEX,结构优化\n'
            '使用方法：\n'
            '1. 输入：结构文件。\n'
            '2. 输出：优化后的结构。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
        ),
        'alternative': ['abacus_do_relax', 'optimize_structure'],
        'self_check': False,
    },
    'apex_calculate_interstitial': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.INTERSTITIAL_FORMATION_ENERGY],
        'description': (
            'What it does: Insert interstitial atoms into a host lattice to compute formation energies across candidate sites (generated internally).\n'
            'When to use: When you need interstitial formation energies starting from a defect-free bulk crystal.\n'
            'Prerequisites / Inputs: Pristine (defect-free) host lattice structure and interstitial atoms.\n The host structure must be a complete bulk lattice (no vacancies/antisites/substitutions, no missing atoms, no partial occupancies/disordered sites). Do NOT provide a structure that already contains defects or extra atoms; the tool assumes a pristine lattice and will place interstitials itself—defected inputs may cause errors or invalid energies.\n'
            'Outputs: Interstitial formation energies for candidate sites.\n'
            'Cannot do / Limits: DFT-based. Not intended for pre-defected host structures.\n'
            'Cost / Notes: DFT calculation cost.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'apex_calculate_interstitial_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.INTERSTITIAL_FORMATION_ENERGY],
        'description': (
            '功能：将间隙原子插入宿主晶格，计算候选位点（内部生成）的形成能。\n'
            '使用场景：当需要从无缺陷的体相晶体开始计算间隙形成能时使用。\n'
            'APEX,间隙形成能\n'
            '使用方法：\n'
            '1. 输入：\n'
            '   结构文件：完整（无缺陷）的宿主晶格结构和间隙原子。\n'
            '   宿主结构必须是完整的体相晶格（无空位/反位/替代、无缺失原子、无部分占位/无序位点）。\n'
            '2. 输出：候选位点的间隙形成能。\n'
            '3. 注意事项：基于 DFT。不要提供已包含缺陷或额外原子的结构；该工具假设完整的晶格并会自行放置间隙原子——提供已有缺陷的结构可能导致错误或无效的能量。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
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
    'apex_calculate_elastic_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.ELASTIC_CONSTANT],
        'description': (
            '功能：对晶格施加小应变以提取弹性常数和衍生模量。\n'
            '使用场景：当需要弹性常数和模量时使用。\n'
            'APEX,弹性常数\n'
            '使用方法：\n'
            '1. 输入：结构文件。\n'
            '2. 输出：弹性常数和衍生模量。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
        ),
        'alternative': ['abacus_cal_elastic', 'calculate_elastic_constants'],
        'self_check': False,
    },
    'apex_calculate_surface': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.SURFACE_ENERGY],
        'description': (
            'What it does: Execute a workflow of surface energy calculation using a pristine Bulk crystal as input.\n'
            'When to use: When you need surface energy starting from a Bulk structure.\n'
            'Prerequisites / Inputs: Bulk structure file. \n'
            'Outputs: Surface energy.\n'
            'Cannot do / Limits: Do NOT provide an already-cut slab/surface structure as input. Slab inputs can cause errors or lead to invalid surface energies.; DFT-based.\n'
            'Cost / Notes: DFT calculation cost.ensure the input is a complete bulk lattice.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'apex_calculate_surface_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.SURFACE_ENERGY],
        'description': (
            '功能：使用完整的体相晶体作为输入执行表面能计算工作流。\n'
            '使用场景：当需要从体相结构开始计算表面能时使用。\n'
            'APEX,表面能\n'
            '使用方法：\n'
            '1. 输入：体相结构文件。\n'
            '2. 输出：表面能。\n'
            '3. 注意事项：\n'
            '   不要提供已切割的板/表面结构作为输入。板状输入可能导致错误或无效的表面能。\n'
            '   基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本。确保输入是完整的体相晶格。'
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
    'apex_calculate_eos_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.EOS],
        'description': (
            '功能：扫描平衡点附近的体积，弛豫内部坐标，构建状态方程的能量-体积曲线。\n'
            '使用场景：当需要状态方程曲线时使用。\n'
            'APEX,EOS\n'
            '使用方法：\n'
            '1. 输入：结构文件。\n'
            '2. 输出：状态方程能量-体积曲线。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
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
    'apex_calculate_phonon_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.PHONON],
        'description': (
            '功能：执行超胞有限位移计算，弛豫构型，并组装声子谱。\n'
            '使用场景：当需要声子谱时使用。\n'
            'APEX,声子\n'
            '使用方法：\n'
            '1. 输入：结构文件。\n'
            '2. 输出：声子谱。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本。\n'
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
    'apex_calculate_gamma_zh': {
        'belonging_agent': ApexAgentName,
        'scene': [SceneEnum.APEX, SceneEnum.STACKING_FAULT_ENERGY],
        'description': (
            '功能：构建并弛豫滑动板，沿指定滑移路径映射广义堆垛层错能。\n'
            '使用场景：当需要堆垛层错能时使用。\n'
            'APEX,堆垛层错能\n'
            '使用方法：\n'
            '1. 输入：结构文件和指定的滑移路径。\n'
            '2. 输出：广义堆垛层错能。\n'
            '3. 注意事项：基于 DFT。\n'
            '4. 成本/备注：涉及 DFT 计算成本。'
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
    'get_target_info_zh': {
        'belonging_agent': UniELFAgentName,
        'scene': [SceneEnum.POLYMER],
        'description': (
            '功能：从 Uni-ELF 推理系统的配置设置中获取目标信息。\n'
            '使用场景：当需要 Uni-ELF 的配置信息时使用。\n'
            '聚合物\n'
            '使用方法：\n'
            '1. 输入：无。\n'
            '2. 输出：全面的配置信息和可用的目标模型映射。\n'
            '3. 注意事项：特定于 Uni-ELF 系统。\n'
            '4. 成本/备注：低。'
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
    'unielf_inference_zh': {
        'belonging_agent': UniELFAgentName,
        'scene': [SceneEnum.POLYMER],
        'description': (
            '功能：对配方输入运行 Uni-ELF 推理以预测性质。\n'
            '使用场景：当需要配方的性质预测时使用。\n'
            '聚合物\n'
            '使用方法：\n'
            '1. 输入：配方的组分和比例。\n'
            '2. 输出：预测的性质。\n'
            '3. 注意事项：支持混合物和伪配方。\n'
            '4. 成本/备注：中等。'
        ),
     
    

    },
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
    'get_database_info_zh': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': (
            '功能：获取钙钛矿太阳能电池数据库的完整模式和描述信息。\n'
            '使用场景：在查询钙钛矿数据库之前使用。\n'
            '钙钛矿\n'
            '使用方法：\n'
            '1. 输入：无。\n'
            '2. 输出：数据库模式和描述。\n'
            '3. 注意事项：特定于钙钛矿数据库。\n'
            '4. 成本/备注：低。'
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
    'sql_database_mcp_zh': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': (
            '功能：对钙钛矿太阳能电池数据库执行 SQL 查询并返回前 k 行。\n'
            '使用场景：获取数据库架构（Schema）信息后，需要查询钙钛矿数据库时使用。\n'
            '钙钛矿\n'
            '使用方法：\n'
            '1. 输入：SQL 查询语句。\n'
            '2. 输出：查询结果的前 k 行。\n'
            '3. 注意事项：仅限于前 k 行。\n'
            '4. 成本/备注：中等。'
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
    'Unimol_Predict_Perovskite_Additive_zh': {
        'belonging_agent': PerovskiteAgentName,
        'scene': [SceneEnum.PEROVSKITE_RESEARCH],
        'description': (
            '功能：使用添加剂分子列表预测添加剂对钙钛矿 PCE 的影响。\n'
            '使用场景：当需要添加剂的 PCE 变化预测时使用。\n'
            '钙钛矿\n'
            '使用方法：\n'
            '1. 输入：添加剂分子列表。\n'
            '2. 输出：预测的 PCE 变化。\n'
            '3. 注意事项：特定于钙钛矿添加剂。\n'
            '4. 成本/备注：中等。'
        ),
        'alternative': [],
        'self_check': False,
    },
    'run_dart_ga': {
        'belonging_agent': COMPDART_AGENT_NAME,
        'scene': [SceneEnum.COMPOSITION_OPTIMIZATION],
        'description': (
            'What it does: Perform compositional optimization for multi-component materials to target specific properties using genetic algorithm.\n'
            'When to use: Search optimized compositions for target properties.\n'
            'Prerequisites / Inputs: Target properties, optional initial compositions or structure templates, constrains, and surrogate model.\n'
            'Outputs: Optimized compositions.\n'
            'Cannot do / Limits: Cannot build doping structures; requires surrogate model.\n'
            'Cost / Notes: High due to long iterations.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'run_dart_ga_zh': {
        'belonging_agent': COMPDART_AGENT_NAME,
        'scene': [SceneEnum.COMPOSITION_OPTIMIZATION],
        'description': (
            '功能：利用遗传算法对多组分材料进行成分优化，以匹配特定的目标性能。\n'
            '使用场景：搜索针对目标性质的优化成分。\n'
            '组分优化\n'
            '使用方法：\n'
            '1. 输入：目标性质、可选的初始成分或结构模板、约束条件和代理模型。\n'
            '2. 输出：优化后的成分。\n'
            '3. 注意事项：无法构建掺杂结构；需要代理模型。\n'
            '4. 成本/备注：由于迭代时间长，成本高。'
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
    'run_doe_task_zh': {
        'belonging_agent': DOE_AGENT_NAME,
        'scene': [SceneEnum.DOE],
        'description': (
            '功能：使用支持的算法运行实验设计（DoE）任务。\n'
            '使用场景：当需要实验设计时使用。\n'
            'DOE\n'
            '使用方法：\n'
            '1. 输入：算法选择（极值顶点、单纯形重心等）。\n'
            '2. 输出：DOE 结果。\n'
            '3. 注意事项：仅限于支持的算法。\n'
            '4. 成本/备注：中等。'
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
    'extract_material_data_from_pdf_zh': {
        'belonging_agent': DocumentParserAgentName,
        'scene': [SceneEnum.LITERATURE, SceneEnum.UNIVERSAL],
        'description': (
            '功能：从 PDF 文档中读取并提取材料数据和方法。\n'
            '使用场景：当需要从 PDF 文献中提取信息时使用。\n'
            '文献,通用场景\n'
            '使用方法：\n'
            '1. 输入：PDF 文件。\n'
            '2. 输出：提取的材料信息和方法。\n'
            '3. 注意事项：无法从互联网检索；仅支持本地 PDF 文件。\n'
            '4. 成本/备注：低。'
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
    'optimize_structure_zh': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.OPTIMIZE_STRUCTURE],
        'description': (
            '功能：使用机器学习势对晶体或分子结构进行几何优化。\n'
            '使用场景：当你需要快速获得优化后的结构，且不想进行耗时的 DFT 计算时使用\n'
            'DPA,结构优化\n'
            '使用方法：\n'
            '1. 输入：结构文件（CIF/POSCAR/ABACUS STRU/LAMMPS 数据）；兼容的机器学习势文件。\n'
            '2. 输出：优化后的结构文件。\n'
            '3. 注意事项：基于机器学习；精度取决于所使用的势函数适用范围\n'
            '4. 成本/备注：相对于 DFT 成本低。'
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
    'run_molecular_dynamics_zh': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.MOLECULAR_DYNAMICS],
        'description': (
            '功能：使用机器学习势运行分子动力学模拟。\n'
            '使用场景：当你需要比密度泛函理论（DFT）更快的速度，但又不满足于传统力场的精度时。\n'
            'DPA,分子动力学\n'
            '使用方法：\n'
            '1. 输入：结构文件；机器学习势；系综设置。\n'
            '2. 输出：分子动力学轨迹和热力学性质。\n'
            '3. 注意事项：仅支持 NVE/NVT/NPT；不支持经典力场或 DFT。\n'
            '4. 成本/备注：中等；计算量随系统规模（原子数）和模拟步数增加。'
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
    'calculate_phonon_zh': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.PHONON],
        'description': (
            '功能：使用机器学习势计算声子性质。\n'
            '使用场景：当需要声子色散和热性质时使用。\n'
            'DPA,声子\n'
            '使用方法：\n'
            '1. 输入：优化后的结构；机器学习势。\n'
            '2. 输出：声子色散、态密度、热性质。\n'
            '3. 注意事项：需要有限位移超胞。\n'
            '4. 成本/备注：高；计算量随超胞规模的增大而显著增加。'
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
            'Outputs: Elastic tensor (Cij), bulk/shear/Young\'s modulus, Poisson ratio (units reported in the result payload).\n'
            'Cannot do / Limits: Not a DFT calculation; accuracy depends on the ML potential domain; may be unreliable for structures far from training distribution.\n'
            'Cost / Notes: Medium; scales with system size and deformation settings.'
        ),
        'args_setting': f"{DPA_MODEL_BRANCH_SELECTION}",
        'alternative': ['abacus_cal_elastic', 'apex_calculate_elastic'],
        'self_check': False,
    },
    'calculate_elastic_constants_zh': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.ELASTIC_CONSTANT],
        'description': (
            '功能：使用机器学习原子间势计算弹性常数（Cij）和衍生的力学性质。\n'
            '使用场景：当你已拥有优化好的结构（Relaxed Structure），并希望跳过 DFT 计算，快速获取弹性性质时。\n'
            'DPA,弹性常数\n'
            '使用方法：\n'
            '1. 输入：结构文件（例如 CIF/POSCAR/ABACUS STRU/LAMMPS 数据）、兼容的机器学习势。\n'
            '2. 输出：弹性张量（Cij）、体积/剪切/杨氏模量、泊松比。\n'
            '3. 注意事项：\n'
            '   非 DFT 计算；其精度高度依赖于机器学习势的拟合水平；\n'
            '   如果目标结构超出了机器学习势的训练集分布，结果可能不可靠。\n'
            '4. 成本/备注：中等；计算量随原子数规模和形变采样（Deformation settings）的复杂程度增加。'
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
    'run_neb_zh': {
        'belonging_agent': DPACalulator_AGENT_NAME,
        'scene': [SceneEnum.DPA, SceneEnum.Nudged_Elastic_Band],
        'description': (
            '功能：使用机器学习势运行微动弹性能带（NEB）计算以估计最小能量路径和能垒。\n'
            '使用场景：当你已知反应的初态和末态（以及可选的初始猜测路径），且需要快速估算反应能垒时。\n'
            'DPA,NEB\n'
            '使用方法：\n'
            '1. 输入：初始和最终结构文件；可选的中间态构型或插值点数；兼容的机器学习势。\n'
            '2. 输出：优化的 NEB 路径、沿图像的能量、估计的能垒和反应坐标。\n'
            '3. 注意事项：\n'
            '   默认精度不直接等同于 DFT 水准。如果中间映像畸变过大，或势函数无法准确描述该化学环境，计算可能会失败。\n'
            '4. 成本/备注：相对于单次弛豫成本高；计算量随映像数量和系统规模增加。'
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
    'finetune_dpa_model_zh': {
        'belonging_agent': FinetuneDPAAgentName,
        'scene': [SceneEnum.DPA],
        'description': (
            '功能：使用 DFT 标记的数据微调 DPA 预训练模型。\n'
            '使用场景：当需要将 DPA 势适应特定体系时使用。\n'
            'DPA\n'
            '使用方法：\n'
            '1. 输入：DFT 标记的数据（能量、力、应力）。\n'
            '2. 输出：微调后的 DPA 模型。\n'
            '3. 注意事项：该功能仅负责“训练”，不能直接运行具体的模拟计算（如 MD 或 NEB）。\n'
            '4. 成本/备注：高。'
        ),
        'args_setting': '不要省略具有默认值的参数。如果用户未提供值，您必须使用输入参数中定义的默认值，并在工具调用中包含该字段。只有没有默认值的参数才是真正必需的，必须从用户输入中填充。',
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
    'HEA_params_calculator_zh': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：从成分计算高熵合金参数，如 VEC、delta、Hmix、Smix、Lambda。\n'
            '使用场景：当需要高熵合金热力学参数时使用。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：高熵合金化学式。\n'
            '2. 输出：VEC、delta、Hmix、Smix、Lambda。\n'
            '3. 注意事项：特定于 HEA。\n'
            '4. 成本/备注：低。'
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
    'HEA_predictor_zh': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：预测高熵合金成分是否形成固溶体及其晶体结构。\n'
            '使用场景：当需要高熵合金的相预测时使用。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：高熵合金成分。\n'
            '2. 输出：固溶体形成和晶体结构。\n'
            '3. 注意事项：使用预训练的机器学习模型。\n'
            '4. 成本/备注：低。'
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
    'HEA_comps_generator_zh': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：通过调节单一元素的摩尔比来生成一系列高熵合金成分。\n'
            '使用场景：用于高熵合金成分设计和优化。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：初始高熵合金成分。\n'
            '2. 输出：一系列修改后的成分。\n'
            '3. 注意事项：一次调整一个元素。\n'
            '4. 成本/备注：低。'
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
    'HEA_data_extract_zh': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：从 PDF 文献中提取高熵合金数据。\n'
            '使用场景：当需要从论文中获取高熵合金数据时使用。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：PDF 文献。\n'
            '2. 输出：成分、合成、微观结构、性质。\n'
            '3. 注意事项：仅支持 PDF 格式。\n'
            '4. 成本/备注：低。'
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
    'HEA_paper_search_zh': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：从 arXiv 搜索并下载高熵合金论文。\n'
            '使用场景：当需要高熵合金文献时使用。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：标题、作者或关键词。\n'
            '2. 输出：搜索结果和下载的论文。\n'
            '3. 注意事项：仅支持 arXiv。\n'
            '4. 成本/备注：中等。'
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
    'HEA_bi_phase_Calc_zh': {
        'belonging_agent': HEA_assistant_AgentName,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：计算高熵合金 中二元对的形成能和相图。\n'
            '使用场景：当需要高熵合金的二元相信息时使用。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：高熵合金化学体系。\n'
            '2. 输出：形成能和凸包。\n'
            '3. 注意事项：仅支持二元对。\n'
            '4. 成本/备注：中等。'
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
    'generate_binary_phase_diagram_zh': {
        'belonging_agent': HEACALCULATOR_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：基于后端工作流中可用的热力学/能量数据，为指定的 A–B 体系生成二元相图。\n'
            '使用场景：当你需要快速了解二元合金或化合物体系在不同成分下，有哪些稳定相（Stable phases）或竞争相（Competing phases）时。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：元素对（A, B）和可选的温度/压力范围；可访问的形成能/热力学数据集或计算路径。\n'
            '2. 输出：相图原始数据（稳定相、结线/共轭线 (Tie-lines)、成分范围）以及可直接绘图的展示结果。\n'
            '3. 注意事项：\n'
            '   如果没有可用的数据集/计算路径，工具将返回错误；\n'
            '   结果依赖于数据覆盖范围和模型假设。\n'
            '4. 成本/备注：中等；使用缓存数据集更快。'
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
    'query_heakb_literature_zh': {
        'belonging_agent': HEA_KB_AGENT_NAME,
        'scene': [SceneEnum.HIGH_ENTROPY_ALLOY],
        'description': (
            '功能：使用自然语言查询高熵合金（HEA）研究的文献知识库。\n'
            '使用场景：当您需要对高熵合金相关主题进行深入的文献分析时。\n'
            '高熵合金\n'
            '使用方法：\n'
            '1. 输入：关于高熵合金的自然语言问题。\n'
            '2. 输出：通过向量相似性搜索返回的文献摘要。\n'
            '3. 注意事项：\n'
            '   主题仅限于高熵合金。\n'
            '4. 成本/备注：中等。\n',
        ),
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
    'query_ssekb_literature_zh': {
        'belonging_agent': SSE_KB_AGENT_NAME,
        'scene': [SceneEnum.Solid_State_Electrolyte],
        'description': (
            '功能：使用自然语言查询固态电解质（SSE）研究的文献知识库。\n'
            '使用场景：当您需要对固态电解质相关主题进行深入的文献分析时。\n'
            '固态电解质\n'
            '使用方法：\n'
            '1. 输入：关于固态电解质的自然语言问题。\n'
            '2. 输出：通过向量相似性搜索返回的文献摘要。\n'
            '3. 注意事项：\n'
            '   主题仅限于固态电解质。\n'
            '4. 成本/备注：中等。\n',
        ),
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
    'query_polymerkb_literature_zh': {
        'belonging_agent': POLYMER_KB_AGENT_NAME,
        'scene': [SceneEnum.POLYMER],
        'description': ('功能：使用自然语言查询聚合物研究的文献知识库。\n'
        '使用场景：当您需要对聚合物相关主题进行深入的文献分析时。\n'
        '聚合物\n'
        '使用方法：\n'
        '1. 输入：关于聚合物的自然语言问题。\n'
        '2. 输出：通过向量相似性搜索返回的文献摘要。\n'
        '3. 注意事项：\n'
        '   主题仅限于聚合物。\n'
        '4. 成本/备注：中等。\n',
        ),
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
    'query_steelkb_literature_zh': {
        'belonging_agent': STEEL_KB_AGENT_NAME,
        'scene': [SceneEnum.STEEL],
        'description': (
            '功能：查询不锈钢研究的文献知识库。\n'
            '使用场景：当您需要对不锈钢相关主题进行深入的文献分析时。\n'
            '不锈钢\n'
            '使用方法：\n'
            '1. 输入：关于不锈钢的自然语言问题。\n'
            '2. 输出：通过向量搜索返回的文献摘要。\n'
            '3. 注意事项：\n'
            '   主题仅限于不锈钢。\n'
            '4. 成本/备注：中等。\n',
        ),
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
    'predict_tensile_strength_zh': {
        'belonging_agent': STEEL_PREDICT_AGENT_NAME,
        'scene': [SceneEnum.STEEL],
        'description': (
            '功能：使用神经网络预测不锈钢的极限抗拉强度。\n'
            '使用场景：当您需要基于化学成分预测抗拉强度时。\n'
            '不锈钢\n'
            '使用方法：\n'
            '1. 输入：化学配方列表。\n'
            '2. 输出：预测的极限抗拉强度值列表（单位：MPa）。\n'
            '3. 注意事项：\n'
            '   仅适用于不锈钢；不返回文件。\n'
            '4. 成本/备注：低。\n',
        ),
        'args_setting': f"{STEELPredictAgentArgsSetting}",
        'alternative': ['search-papers-enhanced', 'web-search'],
        'summary_prompt': STEELPredictAgentSummaryPrompt,
        'self_check': False,
    },
    'fetch_structures_from_db': {
        'belonging_agent': STRUCTURE_SEARCH_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': StructureSearchAgentToolDescription,
        'args_setting': f"{StructureSearchAgentArgsSetting}",
        'alternative': [
            'web-search',
        ],
        'summary_prompt': StructureSearchAgentSummaryPrompt,
        'self_check': True,
    },
    'fetch_structures_from_db_zh': {
        'belonging_agent': STRUCTURE_SEARCH_AGENT_NAME,
        'scene': [SceneEnum.DATABASE_SEARCH],
        'description': (
            '功能：从多个数据源（BohriumPublic / OpenLAM / OPTIMADE 提供者）检索晶体结构，或对 MOFdb 运行高级 SQL 查询。\n'
            '使用场景：任何“查找晶体结构”的请求，包括按化学式/元素/空间群/带隙筛选、或针对 MOF 的特定分析（MOFdb SQL）。\n'
            '数据库搜索\n'
            '使用方法：\n'
            '1. 输入：结构化筛选条件（化学式/元素/空间群范围）、筛选条件，筛选字符串，或 MOFdb SQL 语句。\n'
            '2. 输出：CIF/JSON 格式的结构或元数据；MOFdb 返回 SQL 查询结果行及可选的结构文件链接。\n'
            '3. 注意事项：\n'
            '   OPTIMADE 筛选必须遵循标准语法；MOFdb 仅限 MOF 相关数据；OpenLAM 不提供空间群/带隙信息。\n'
            '4. 成本/备注：低。\n',
        ),
        'args_setting': f"{StructureSearchAgentArgsSetting}",
        'alternative': ['web-search'],
        'summary_prompt': StructureSearchAgentSummaryPrompt,
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
    'calculate_reaction_profile_zh': {
        'belonging_agent': ORGANIC_REACTION_AGENT_NAME,
        'scene': [SceneEnum.REACTION],
        'description': (
            '功能：计算反应势能剖面。\n'
            '使用场景：用于有机反应分析。\n'
            '反应\n'
            '使用方法：\n'
            '1. 输入：反应输入。\n'
            '2. 输出：反应势能剖面（展示反应坐标与能量关系的剖面图）。\n'
            '3. 注意事项：仅针对化学反应体系；不适用于通用的结构搜索或非反应性计算。\n'
            '4. 成本/备注：中等。'
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
    'run_piloteye_zh': {
        'belonging_agent': PILOTEYE_ELECTRO_AGENT_NAME,
        'scene': [SceneEnum.PILOTEYE_ELECTRO],
        'description': (
            '功能：使用分子动力学和密度泛函理论对锂离子电池电解质进行性质计算。\n'
            '使用场景：当你需要评估或预测电解液体系的性能指标时。\n'
            'PILOTEYE_ELECTRO\n'
            '使用方法：\n'
            '1. 输入：包含“配方信息（Formulation）”的 JSON 格式参数文件。\n'
            '2. 输出：建模流程的目标性质。\n'
            '3. 注意事项：仅限使用内置分子库中的物料。该模块为固定工作流，自定义灵活度受限。\n'
            '4. 成本/备注：高。'
        ),
        'alternative': [],
        'self_check': False,
    },
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
    'generate_calypso_structures_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：利用 CALYPSO 进行全局结构搜索，从而生成一系列候选晶体结构。\n'
            '使用场景：当需要探索成分的同质异形体时使用。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：有效的元素输入。\n'
            '2. 输出：POSCAR 文件。\n'
            '3. 注意事项：需要下游弛豫。\n'
            '4. 成本/备注：中等。'
        ),
        'args_setting': '参数指导：n_tot=10–30 可在不过度成本的情况下提供合理的多样性。元素必须来自支持的列表（H–Bi, Ac–Pu）。输出是一组 POSCAR 文件；强烈建议进行下游弛豫。',
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
    'generate_crystalformer_structures_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.CONDITIONAL_GENERATE],
        'description': (
            '功能：基于条件属性和空间群生成晶体结构。\n'
            '使用场景：当需要具有特定性质的结构时使用。\n'
            '结构生成，条件生成\n'
            '使用方法：\n'
            '1. 输入：目标性质（带隙、模量、Tc、声速）；空间群。\n'
            '2. 输出：生成的结构。\n'
            '3. 注意事项：仅支持模型预训练过的特定性质;必须指定空间群作为生成的约束条件。\n'
            '4. 成本/备注：高；使用生成模型。'
        ),
        'args_setting': '参数指导：支持的性质：带隙（eV）、剪切模量、体积模量（均为 log₁₀ GPa）、超导常压/高压（K）、声速（m/s）。对于 target_type="minimize"，使用小目标值（例如 0.1）和低 alpha（0.01）；对于 "equal"、"greater"、"less"，使用 alpha=1.0。mc_steps=500 平衡收敛和速度；对于高精度目标，增加到 2000。建议 sample_num=20–100；如果 random_spacegroup_num>0，则在空间群之间分布。关键：空间群必须由用户明确指定——无默认值或自动推断。',
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
    'make_supercell_structure_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：从结构文件创建超胞扩充。\n'
            '使用场景：当你需要构建更大尺寸的单元以进行模拟时。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：结构文件。\n'
            '2. 输出：超胞结构。\n'
            '3. 注意事项：仅支持扩展，不支持缩减。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': '参数指导：主要遵循用户的指示。如果未指定，首先获取结构信息以了解原始晶格。用于计算的理想超胞是各向同性的。例如，原始晶格为（4 Å, 10 Å, 12 Å, 90 deg, 90 deg, 90 deg），超胞应为 5 × 2 × 2。30-50 埃通常适合模拟。除非需要长程相互作用，否则避免过大的晶胞。',
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
    'build_bulk_structure_by_template_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：为简单堆积类型和化合物构建体相结构。\n'
            '使用场景：用于标准晶体结构，如 sc、fcc、bcc、hcp、岩盐等。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：元素符号或化学式；晶格常数。\n'
            '2. 输出：晶体结构文件。\n'
            '3. 注意事项：仅限于简单结构；不支持复杂晶体。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：由于对称性约束的晶格常数要求：sc/fcc/bcc/diamond/rocksalt/cesiumchloride/zincblende/fluorite → 仅 a；hcp/wurtzite → a 和 c；orthorhombic/monoclinic → a, b, c。除非明确要求原胞，否则默认设置 conventional=True。对于元素，使用元素符号；对于化合物，使用化学式（例如 "NaCl"）。{STRUCTURE_BUILDING_SAVENAME}',
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
    'build_surface_slab_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：从体相结构构建表面结构。\n'
            '使用场景：当需要表面模型进行计算时使用。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：体相结构文件；Miller 指数。\n'
            '2. 输出：表面结构文件。\n'
            '3. 注意事项：需要体相输入；添加真空层。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：为了稳定性，优先使用 slab_size_mode="layers"，slab_size_value=4–6；或使用 "thickness"，≥12 Å 用于电子收敛。使用 vacuum=15–20 Å 以最小化虚假相互作用。对于极性表面或具有强偶极子的体系，增加真空层以确保静电势在真空区域变平。对于共价材料（例如，类药物分子晶体、有机-无机杂化物、MOF），启用 repair=True；对于规则的类球形无机晶体，设置为 false。如果设置为 True，速度会变慢。默认 termination="auto" 通常选择最化学计量的终止。{STRUCTURE_BUILDING_SAVENAME}',
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
    'build_surface_adsorbate_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：通过在表面上放置分子来构建表面-吸附物结构。\n'
            '使用场景：用于吸附研究。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：表面结构文件和吸附质结构文件。\n'
            '2. 输出：组合结构文件。\n'
            '3. 注意事项：仅支持单吸附质放置。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：height=2.0 Å 通常用于物理吸附；对于化学吸附（例如，CO 在 Pt 上）减少到 1.5–1.8 Å。对于高对称性位点，使用字符串关键词（"ontop"、"fcc"、"hcp"）；对于自定义放置，提供 [x, y] 分数坐标。{STRUCTURE_BUILDING_SAVENAME}',
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
    'build_surface_interface_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：通过堆叠两个表面结构来构建异质界面。\n'
            '使用场景：用于界面研究。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：两个表面结构文件。\n'
            '2. 输出：界面结构文件。\n'
            '3. 注意事项：基础的应变 (Strain) 检查。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：保持 max_strain=0.05（5%）以确保物理相关性；仅在有意进行应变工程时进行弛豫。尝试结合 make_supercell 和 get_structural_info 以获得两个板的适当尺寸。interface_distance=2.5 Å 对于范德华间隙是安全的；对于共价键合（例如，具有轨道重叠的异质结构）减少到 1.8–2.0 Å。{STRUCTURE_BUILDING_SAVENAME}',
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
    'add_cell_for_molecules_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：为分子结构添加周期晶胞以进行计算。\n'
            '使用场景：用于需要周期性的孤立分子计算。\n'
            '使用方法：\n'
            '结构生成\n'
            '1. 输入：分子结构文件。\n'
            '2. 输出：带周期晶胞的结构。\n'
            '3. 注意事项：用于气相分子。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：对于需要周期性边界条件的非周期体系（例如，使用 ABACUS 的 DFT 计算），使用 add_cell_for_molecules 将体系放入大晶胞中。默认晶胞 [10, 10, 10] Å 和 vacuum = 5 Å 适合大多数气相分子；对于极性或扩散体系（例如，阴离子、激发态）增加到 ≥15 Å 和 ≥8 Å 真空。{STRUCTURE_BUILDING_SAVENAME}',
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
    'build_bulk_structure_by_wyckoff_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：通过指定空间群和 Wyckoff 位置来构建晶体结构。\n'
            '使用场景：用于自定义晶体结构。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：空间群；带坐标的 Wyckoff 位置。\n'
            '2. 输出：晶体结构文件。\n'
            '3. 注意事项：需要对称性知识。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：空间群：整数（例如，225）或符号（例如，"Fm-3m"）。Wyckoff 一致性：提供的坐标必须在数学上属于特定的 Wyckoff 位置（例如，如果在 (0,0,0) 使用位置 4a，不要仅仅因为它在同一晶胞中就输入 (0.5, 0.5, 0)；只输入规范生成元）。晶格：角度以度为单位，长度以 Å 为单位。分数坐标：必须在 [0, 1) 范围内。严格使用非对称单元：您必须仅为每个 Wyckoff 轨道提供生成坐标。不要预先计算对称性：函数将自动将所有空间群操作符应用于您的输入。如果您手动输入已经对称等价的坐标（例如，在中心对称结构中同时提供 (x, y, z) 和 (-x, -y, -z)），函数将再次生成它们，导致灾难性的原子重叠。冗余规则：在添加坐标之前，检查它是否可以通过空间群中的任何操作符从现有输入坐标生成。如果是，则丢弃它。一个 Wyckoff 字母 = 一个坐标三元组输入。{STRUCTURE_BUILDING_SAVENAME}',
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
    'build_molecule_structures_from_smiles_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：从 SMILES 字符串构建 3D 分子结构。\n'
            '使用场景：当您有 SMILES 并需要 3D 坐标时使用。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：SMILES 字符串。\n'
            '2. 输出：分子结构文件。\n'
            '3. 注意事项：单个构象生成。\n'
            '4. 成本/备注：低。'
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
    'make_doped_structure_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：通过替换原子生成掺杂晶体结构。\n'
            '使用场景：用于掺杂研究。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：主体结构；掺杂物种和浓度。\n'
            '2. 输出：掺杂结构文件。\n'
            '3. 注意事项：随机替换；建议使用超胞。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': f'参数指导：分数按位点应用；实际掺杂百分比在小晶胞中可能略有不同——对于 <10% 掺杂，建议使用 ≥2×2×2 超胞。共价离子（铵、甲脒等）通过内置库支持；按名称指定（例如，"ammonium"）。{STRUCTURE_BUILDING_SAVENAME}',
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
    'make_defect_structure_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：通过基于空间关系移除特定分子簇来创建缺陷结构。\n'
            '使用场景：用于通过基于空间聚类移除特定分子单元在分子晶体中创建空位缺陷。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：分子晶体结构文件；（可选）目标移除物种、起始分子索引。\n'
            '2. 输出：缺陷结构文件。\n'
            '3. 注意事项：专为分子晶体设计。该功能确保移除的是整个分子单元，而非晶格中的孤立原子。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': '参数指导：structure_path 是输入的分子晶体结构文件（例如，CIF）；target_spec 是一个可选的字典，将物种 ID 映射到要移除的数量（例如，{"C6H14N2_1": 1, "H4N_1": 1}），如果为 None 则使用晶体中最简单的单元；seed_index 是开始移除的分子的索引，如果为 None 则从最稀有物种中随机选择；method 是用于选择要移除的分子的方法；return_removed_cluster：控制是否返回移除的簇；output_file 是保存生成的缺陷结构文件的路径。',
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
    'make_amorphous_structure_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：在周期性盒子 (Periodic Box) 中生成非晶态/无定形分子结构。\n'
            '使用场景：用于非晶材料模拟。\n'
            '结构生成\n'
            '使用方法：\n'
            '1. 输入：分子结构；盒子尺寸/密度/数量。\n'
            '2. 输出：非晶结构文件。\n'
            '3. 注意事项：具备基础的防重叠功能，但生成的结构仍需进行后续的结构弛豫或分子动力学平衡。\n'
            '4. 成本/备注：中等。'
        ),
        'args_setting': f'参数指导：输入约束：精确指定以下两个：box_size、density、molecule_numbers。第三个是推导的。密度范围（关键）：固体/液体：目标 ~0.9–1.2 g/cm³（例如，水 ~1.0，聚合物 ~1.1）。气体/蒸汽：目标数量级更低（例如，STP 气体 ~0.001–0.002 g/cm³）。警告：不要将默认液体密度应用于气体输入。如果模拟特定压力，预先计算给定盒子体积 V 所需的分子数 N（使用理想气体定律），然后固定 box_size 和 molecule_numbers。组成：对于多组分混合物使用 composition；否则假设等摩尔比。堆积几何：盒子尺寸：对于气体，确保盒子足够大（通常 >15 Å）以最小化非物理周期性自相互作用，即使密度很低。{STRUCTURE_BUILDING_SAVENAME}',
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
    'get_structure_info_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            '功能：从文件中提取结构信息。\n'
            '使用场景：分析晶体/分子结构文件。\n'
            '通用场景\n'
            '使用方法：\n'
            '1. 输入：结构文件路径。\n'
            '2. 输出：化学式、空间群、晶格、原子。\n'
            '3. 注意事项：不进行修改；只读。\n'
            '4. 成本/备注：低。'
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
    'get_molecule_info_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            '功能：从文件中提取分子结构信息。\n'
            '使用场景：分析分子结构文件。\n'
            '通用场景\n'
            '使用方法：\n'
            '1. 输入：分子文件路径。\n'
            '2. 输出：化学式、原子、键、性质。\n'
            '3. 注意事项：不进行修改；只读。\n'
            '4. 成本/备注：低。'
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
    'add_hydrogens_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_SANITIZE, SceneEnum.STRUCTURE_GENERATE],
        'description': (
            '功能：为输入结构添加氢原子。\n'
            '使用场景：补全结构中缺失的氢原子。\n'
            '结构规范化,结构生成\n'
            '使用方法：\n'
            '1. 输入：结构文件路径；成键规则或特定的加氢逻辑。\n'
            '2. 输出：已添加氢原子的结构文件。\n'
            '3. 注意事项：不进行优化、精化或反应。\n'
            '4. 成本/备注：低。'
        ),
        'args_setting': (
            '- target_elements: 可选。将氢添加限制到特定元素。\n'
            '- optimize_torsion: 可选。如果为 True，调整扭转角以优化几何结构；默认为 False。\n'
            '- rules: 可选。对于特殊情况**关键**（例如，铵中的 N 必须保持 target_coordination=4 和四面体几何）。'
            '如果未提供，则使用默认化学环境规则。为了精确控制，提供规则以覆盖默认值。\n'
            '- bond_lengths: 可选。覆盖特定原子对的默认键长。如果为 None，则使用默认值。\n'
            '重要提示：尽管规则是可选的，但某些官能团需要显式规则才能正确。'
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
    'generate_ordered_replicas_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.STRUCTURE_SANITIZE],
        'description': (
            '功能：处理含有原子无序的 CIF 文件，生成对应的有序化副本结构。\n'
            '使用场景：当您有无序结构并需要解决无序以创建有序结构时使用。\n'
            '结构生成,结构规范化\n'
            '使用方法：\n'
            '1. 输入：无序 CIF 文件路径；（可选）生成的有序结构数量、生成方法。\n'
            '2. 输出：生成的有序结构文件路径列表。\n'
            '3. 注意事项：仅处理无序结构到有序结构；必须提供符合规范的 CIF 输入文件。\n'
            '4. 成本/备注：中等。'
        ),
        'args_setting': (
            '参数指导：structure_path: 必需。输入无序结构文件（CIF 格式）。'
            'generate_count: 可选。要生成的有序结构数量（默认：1）。'
            'method: 可选。生成方法（"optimal" 用于单个最佳结构，"random" 用于结构集合）（默认："random"）。'
            'output_file: 可选。保存输出文件的目录；默认为输入文件位置的子目录。'
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
    'remove_solvents_zh': {
        'belonging_agent': StructureGenerateAgentName,
        'scene': [SceneEnum.STRUCTURE_GENERATE, SceneEnum.STRUCTURE_SANITIZE],
        'description': (
            '功能：从分子晶体结构中移除指定的溶剂分子。\n'
            '使用场景：当对分子晶体进行去溶剂化以获得无溶剂或部分去溶剂化结构用于分析或模拟时使用。\n'
            '结构生成,结构规范化\n'
            '使用方法：\n'
            '1. 输入：包含可识别溶剂分子的 CIF 结构文件；目标溶剂名称或化学式。\n'
            '2. 输出：去溶剂化结构文件的路径。\n'
            '3. 注意事项：仅能移除基于化学组成识别的完整溶剂分子；该操作不会修改骨架原子，也不会处理结构中的无序问题。建议首先调用 get_structure_info 以检查分子组分并确认溶剂身份。\n'
            '4. 成本/备注：低。建议首先检查分子组分。'
        ),
        'args_setting': (
            '参数指导：structure_path: 必需。包含溶剂分子的输入 CIF 文件。'
            'output_file: 必需。保存去溶剂化结构的路径。'
            'targets: 必需。要移除的溶剂名称或化学式列表（例如，"H2O"、"DMF"）。'
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
    'run_superconductor_optimization_zh': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            '功能：优化超导结构。\n'
            '使用场景：弛豫超导体几何结构。\n'
            '超导体\n'
            '使用方法：\n'
            '1. 输入：结构文件（CIF/POSCAR）。\n'
            '2. 输出：优化后的结构。\n'
            '3. 注意事项：仅进行几何优化。\n'
            '4. 成本/备注：高（DPA 计算）。'
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
    'calculate_superconductor_enthalpy_zh': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            '功能：计算焓和稳定性。\n'
            '使用场景：筛选超导体稳定性。\n'
            '超导体\n'
            '使用方法：\n'
            '1. 输入：结构候选物。\n'
            '2. 输出：焓、凸包、稳定相。\n'
            '3. 注意事项：仅限超导体。\n'
            '4. 成本/备注：高（DPA 计算）。'
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
    'predict_superconductor_Tc_zh': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            '功能：预测超导 Tc。\n'
            '使用场景：估算临界温度。\n'
            '超导体\n'
            '使用方法：\n'
            '1. 输入：材料结构。\n'
            '2. 输出：Tc 预测。\n'
            '3. 注意事项：仅限 DPA 模型。\n'
            '4. 成本/备注：高（ML 预测）。'
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
    'screen_superconductor_zh': {
        'belonging_agent': SuperconductorAgentName,
        'scene': [SceneEnum.SUPERCONDUCTOR],
        'description': (
            '功能：筛选多个超导体。\n'
            '使用场景：比较 Tc 和稳定性。\n'
            '超导体\n'
            '使用方法：\n'
            '1. 输入：候选物列表。\n'
            '2. 输出：排序的 Tc 和稳定性。\n'
            '3. 注意事项：仅限多个候选物。\n'
            '4. 成本/备注：高（批量 DPA）。'
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
    'predict_thermoelectric_properties_zh': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            '功能：预测热电性质。\n'
            '使用场景：估算带隙、塞贝克系数等。\n'
            '热电\n'
            '使用方法：\n'
            '1. 输入：材料结构文件。\n'
            '2. 输出：带隙、塞贝克系数、功率因子、模量。\n'
            '3. 注意事项：暂不支持热导率的预测。\n'
            '4. 成本/备注：高（DPA 预测）。'
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
    'run_pressure_optimization_zh': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            '功能：在压力下优化。\n'
            '使用场景：弛豫热电结构。\n'
            '热电\n'
            '使用方法：\n'
            '1. 输入：结构、压力。\n'
            '2. 输出：优化后的结构。\n'
            '3. 注意事项：仅限热电材料。\n'
            '4. 成本/备注：高（DPA 计算）。'
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
    'calculate_thermoele_enthalp_zh': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            '功能：计算压力下的焓。\n'
            '使用场景：筛选热电稳定性。\n'
            '热电\n'
            '使用方法：\n'
            '1. 输入：候选物、压力。\n'
            '2. 输出：焓、凸包。\n'
            '3. 注意事项：仅限热电材料。\n'
            '4. 成本/备注：高（DPA 计算）。'
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
    'screen_thermoelectric_candidate_zh': {
        'belonging_agent': ThermoelectricAgentName,
        'scene': [SceneEnum.THERMOELECTRIC],
        'description': (
            '功能：筛选热电候选物。\n'
            '使用场景：识别有前景的材料。\n'
            '热电\n'
            '使用方法：\n'
            '1. 输入：多个结构。\n'
            '2. 输出：排序的热电性质。\n'
            '3. 注意事项：需要多个输入。\n'
            '4. 成本/备注：高（批量 DPA）。'
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
    'traj_analysis_diffusion_zh': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            '功能：从分子动力学轨迹分析扩散。\n'
            '使用场景：计算均方位移（MSD）、扩散系数等。\n'
            'POST_MD_ANALYSIS\n'
            '使用方法：\n'
            '1. 输入：分子动力学轨迹文件。\n'
            '2. 输出：MSD、扩散系数 D、电导率等。\n'
            '3. 注意事项：仅用于分子动力学后处理分析。\n'
            '4. 成本/备注：中等。'
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
    'traj_analysis_rdf_zh': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            '功能：从分子动力学轨迹计算径向分布函数（RDF）。\n'
            '使用场景：分析原子分布。\n'
            'POST_MD_ANALYSIS\n'
            '使用方法：\n'
            '1. 输入：分子动力学轨迹。\n'
            '2. 输出：径向分布函数。\n'
            '3. 注意事项：仅用于分子动力学后处理分析。\n'
            '4. 成本/备注：中等。'
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
    'traj_analysis_solvation_zh': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            '功能：分析溶剂化结构。\n'
            '使用场景：研究溶剂-溶质相互作用。\n'
            'POST_MD_ANALYSIS\n'
            '使用方法：\n'
            '1. 输入：分子动力学轨迹。\n'
            '2. 输出：溶剂化壳层、相关性质。\n'
            '3. 注意事项：仅用于分子动力学后处理分析。\n'
            '4. 成本/备注：中等。'
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
    'traj_analysis_bond_zh': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            '功能：分析键长随时间的变化。\n'
            '使用场景：监测化学键动力学。\n'
            'POST_MD_ANALYSIS\n'
            '使用方法：\n'
            '1. 输入：分子动力学轨迹。\n'
            '2. 输出：键长时间序列。\n'
            '3. 注意事项：仅用于分子动力学后处理分析。\n'
            '4. 成本/备注：中等。'
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
    'traj_analysis_react_zh': {
        'belonging_agent': TrajAnalysisAgentName,
        'scene': [SceneEnum.POST_MD_ANALYSIS],
        'description': (
            '功能：分析反应网络。\n'
            '使用场景：研究化学反应。\n'
            'POST_MD_ANALYSIS\n'
            '使用方法：\n'
            '1. 输入：分子动力学轨迹。\n'
            '2. 输出：反应物种、反应网络。\n'
            '3. 注意事项：仅用于分子动力学后处理分析。\n'
            '4. 成本/备注：中等。'
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
    'visualize_data_from_file_zh': {
        'belonging_agent': VisualizerAgentName,
        'scene': [SceneEnum.VISUALIZE_DATA, SceneEnum.UNIVERSAL],
        'description': (
            '功能：从数据文件创建图表。\n'
            '使用场景：可视化 CSV/Excel/JSON 等数据。\n'
            '数据可视化,通用场景\n'
            '使用方法：\n'
            '1. 输入：数据文件 URL。\n'
            '2. 输出：图表。\n'
            '3. 注意事项：仅支持数据文件。\n'
            '4. 成本/备注：低。'
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
    'visualize_data_from_prompt_zh': {
        'belonging_agent': VisualizerAgentName,
        'scene': [SceneEnum.VISUALIZE_DATA, SceneEnum.UNIVERSAL],
        'description': (
            '功能：根据提示词创建图表。\n'
            '使用场景：快速可视化嵌入在提示词中的数据。\n'
            '数据可视化,通用场景\n'
            '使用方法：\n'
            '1. 输入：提示词（内含数据）。\n'
            '2. 输出：图表。\n'
            '3. 注意事项：仅支持包含有效数据的绘图请求。\n'
            '4. 成本/备注：低。'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
    'orchestrate_input': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [
            SceneEnum.MOLECULAR_DYNAMICS,
            SceneEnum.LAMMPS,
            SceneEnum.ABACUS,
            SceneEnum.UNIVERSAL,
        ],
        'description': (
            'What it does: Generate input scripts for simulation/calculation engines. '
            'Supports: LAMMPS, ABACUS, VASP, QE (Quantum ESPRESSO), Psi4, Gaussian, ORCA.\n'
            'When to use: Create input from description.\n'
            'Prerequisites / Inputs: structural information; engine_type (one of: lammps, abacus, vasp, qe, psi4, gaussian, orca), natural language task.\n'
            'Outputs: Input script content.\n'
            'Cannot do / Limits: Script generation only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'orchestrate_input_zh': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            '功能：为模拟引擎生成输入脚本（当前支持：LAMMPS, ABACUS, VASP, QE, Psi4, Gaussian, ORCA）。\n'
            '使用场景：根据描述创建输入文件。\n'
            '分子动力学,LAMMPS\n'
            '使用方法：\n'
            '1. 输入：engine_type="lammps"（或者以下其中一种：abacus, vasp, qe, psi4, gaussian, orca），自然语言任务描述。\n'
            '2. 输出：输入脚本内容。\n'
            '3. 注意事项：仅生成脚本，不执行模拟。\n'
            '4. 成本/备注：低。'
        ),
        'alternative': [],
        'self_check': False,
    },
    'convert_structural_format': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            'What it does: Convert structure to target format (Currently supports: lammps/lmp).\n'
            'When to use: Prepare structures for simulation.\n'
            'Prerequisites / Inputs: Structure file URL, target_format="lammps/lmp".\n'
            'Outputs: Converted structure file.\n'
            'Cannot do / Limits: Format conversion only.\n'
            'Cost / Notes: Low.'
        ),
        'alternative': [],
        'self_check': False,
    },
    'convert_structural_format_zh': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            '功能：将结构转换为目标格式（当前支持：lammps/lmp）。\n'
            '使用场景：为模拟准备结构文件。\n'
            '分子动力学,LAMMPS\n'
            '使用方法：\n'
            '1. 输入：结构文件 URL；target_format="lammps/lmp"。\n'
            '2. 输出：转换后的结构文件。\n'
            '3. 注意事项：仅进行格式转换。\n'
            '4. 成本/备注：低。'
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
    'run_lammps_zh': {
        'belonging_agent': LAMMPS_AGENT_NAME,
        'scene': [SceneEnum.MOLECULAR_DYNAMICS, SceneEnum.LAMMPS],
        'description': (
            '功能：运行 LAMMPS 分子动力学模拟。\n'
            '使用场景：执行分子动力学或能量最小化。\n'
            '分子动力学,LAMMPS\n'
            '使用方法：\n'
            '1. 输入：LAMMPS 数据文件。\n'
            '2. 输出：模拟结果。\n'
            '3. 注意事项：输入须为 LAMMPS 格式。\n'
            '4. 成本/备注：高（取决于模拟时长）。'
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
    'search-papers-enhanced_zh': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.LITERATURE],
        'description': (
            '功能：检索科学文献。\n'
            '使用场景：按主题查找相关研究。\n'
            '文献\n'
            '使用方法：\n'
            '1. 输入：主题关键词。\n'
            '2. 输出：文献摘要、相关论文摘要信息及论文链接。\n'
            '3. 注意事项：仅进行文献检索；不下载学位论文等文件（.pdf、.doc 等）。\n'
            '4. 成本/备注：低。'
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
    'web-search_zh': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            '功能：执行网页搜索，回答 what、why、how 类问题。\n'
            '使用场景：进行简明的事实查询或解释性检索。\n'
            '通用场景\n'
            '使用方法：\n'
            '1. 输入：搜索查询词。\n'
            '2. 输出：URL、标题、摘要片段。\n'
            '3. 注意事项：不支持指令型查询；如需提取页面内容可后续调用 extract_info_from_webpage。\n'
            '4. 成本/备注：低。'
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
    'build_convex_hull_zh': {
        'belonging_agent': ConvexHullAgentName,
        'scene': [SceneEnum.CONVEXHULL],
        'description': (
            '功能：构建凸包图。\n'
            '使用场景：评估材料的热力学稳定性。\n'
            '凸包\n'
            '使用方法：\n'
            '1. 输入：材料结构。\n'
            '2. 输出：凸包、稳定相。\n'
            '3. 注意事项：仅适用于通用材料。\n'
            '4. 成本/备注：高（涉及 DPA 计算）。'
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
    'NMR_search_tool_zh': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': (
            '功能：根据核磁共振谱图特征在分子数据库中检索候选结构。\n'
            '使用场景：已有 NMR 峰/化学位移等谱图信息，需要匹配的可能分子。\n'
            'NMR\n'
            '使用方法：\n'
            '1. 输入：符合工具规范的 NMR 特征（如化学位移、多重度、耦合、核类型等）；可选容差设置。\n'
            '2. 输出：带匹配分数和关键证据的候选分子/结构排序列表。\n'
            '3. 注意事项：非唯一鉴定；结果依赖数据库覆盖度和特征质量。\n'
            '4. 成本/备注：中等；容差越严，耗时增加、召回率降低。'
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
    'NMR_predict_tool_zh': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': (
            '功能：预测分子结构的核磁共振谱图性质。\n'
            '使用场景：需要模拟的 NMR 化学位移时使用。\n'
            'NMR\n'
            '使用方法：\n'
            '1. 输入：SMILES 字符串。\n'
            '2. 输出：预测的 NMR 化学位移及相似度分数。\n'
            '3. 注意事项：仅支持 1H 与 13C。\n'
            '4. 成本/备注：中等。'
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
    'NMR_reverse_predict_tool_zh': {
        'belonging_agent': NMR_AGENT_NAME,
        'scene': [SceneEnum.NMR],
        'description': (
            '功能：从核磁共振谱图数据生成候选分子结构。\n'
            '使用场景：已有 NMR 数据，需要结构候选时使用。\n'
            'NMR\n'
            '使用方法：\n'
            '1. 输入：核磁共振谱图数据。\n'
            '2. 输出：候选分子结构。\n'
            '3. 注意事项：基于 NMR 特征生成。\n'
            '4. 成本/备注：中等。'
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
    'extract_info_from_webpage_zh': {
        'belonging_agent': SCIENCE_NAVIGATOR_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            '功能：从网页 URL 提取关键信息。\n'
            '使用场景：需要从网页获取科学事实、数据或结论时使用。\n'
            '通用场景\n'
            '使用方法：\n'
            '1. 输入：网页 URL。\n'
            '2. 输出：以文本形式呈现的提取结果。\n'
            '3. 注意事项：仅返回文本，不支持生成任何格式的文件。\n'
            '4. 成本/备注：低。'
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
    'xrd_parse_file_zh': {
        'belonging_agent': XRD_AGENT_NAME,
        'scene': [SceneEnum.XRD],
        'description': (
            '功能：解析并预处理原始 XRD 数据文件。\n'
            '使用场景：有待分析的 XRD 数据时使用。\n'
            'XRD\n'
            '使用方法：\n'
            '1. 输入：XRD 文件（.xrdml、.xy、.asc、.txt）。\n'
            '2. 输出：处理后的数据及可视化配置。\n'
            '3. 注意事项：不支持 .raw、.mdi 格式。\n'
            '4. 成本/备注：低。'
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
    'xrd_phase_identification_zh': {
        'belonging_agent': XRD_AGENT_NAME,
        'scene': [SceneEnum.XRD],
        'description': (
            '功能：在 XRD 谱图中鉴定晶相。\n'
            '使用场景：已有处理后的 XRD 数据时使用。\n'
            'XRD\n'
            '使用方法：\n'
            '1. 输入：处理后的 CSV 文件；可选的组分过滤条件。\n'
            '2. 输出：最佳匹配相及对比图。\n'
            '3. 注意事项：需要先完成数据预处理。\n'
            '4. 成本/备注：中等。'
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
    'get_electron_microscope_recognize_zh': {
        'belonging_agent': Electron_Microscope_AGENT_NAME,
        'scene': [SceneEnum.Electron_Microscope],
        'description': (
            '功能：分析电镜图像中的颗粒与形貌。\n'
            '使用场景：有待分析的 TEM/SEM 图像时使用。\n'
            '电镜\n'
            '使用方法：\n'
            '1. 输入：电镜图像（.tif、.tiff、.png、.jpeg、.jpg）。\n'
            '2. 输出：检测到的颗粒、形貌及几何性质。\n'
            '3. 注意事项：仅支持 .tif、.tiff、.png、.jpeg、.jpg 格式。\n'
            '4. 成本/备注：中等。'
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
    'tpd_parse_and_get_mol_zh': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            '功能：解析单个 TPD 文件并提取识别到的分子量（m/z 或标签）。\n'
            '使用场景：需要获知 TPD 文件中包含哪些分子量时使用。\n'
            'TPD\n'
            '使用方法：\n'
            '1. 输入：本地文件路径、文件名、数据类型（Signal 或 Temp/Time）。\n'
            '2. 输出：分子量列表（m/z 或 "*"）。\n'
            '3. 注意事项：仅解析本地文件；远程 URL 需先下载。\n'
            '4. 成本/备注：快速；支持三种数据类型。'
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
    'tpd_get_chart_zh': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            '功能：为 TPD 文件中选定的分子量生成 ECharts 可视化配置。\n'
            '使用场景：需要绘制 TPD 文件中选定 m/z 通道的曲线时使用。\n'
            'TPD\n'
            '使用方法：\n'
            '1. 输入：本地文件路径、文件名、selected_weights（m/z 列表）、数据类型、线宽。\n'
            '2. 输出：保存的 ECharts 配置 JSON 文件路径。\n'
            '3. 注意事项：仅支持本地文件；selected_weights 须与可用 m/z 对应。\n'
            '4. 成本/备注：快速；支持三种数据类型。'
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
    'tpd_get_cal_zh': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            '功能：对单个文件中某一分子量（m/z）信号进行 TPD 分析（寻峰、拟合、积分、求导）。\n'
            '使用场景：需要对特定 m/z 通道或总信号做峰分析、面积计算或求导时使用。\n'
            'TPD\n'
            '使用方法：\n'
            '1. 输入：本地文件路径；目标分子量（m/z 字符串如 "18"、"44"，或 "*" 表示总信号）；分析操作（寻峰、拟合、积分范围、求导设置等）。\n'
            '2. 输出：ECharts 可视化配置、积分面积（若计算）、失败操作的错误列表。\n'
            '3. 注意事项：每次仅处理一个 m/z；多分子需多次调用；须为本地文件。\n'
            '4. 成本/备注：中等；各操作独立；未指定 m/z 时默认总信号。'
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
    'tpd_peak_integrate_zh': {
        'belonging_agent': TPD_AGENT_NAME,
        'scene': [SceneEnum.TPD],
        'description': (
            '功能：对单个 TPD 文件及 m/z，在局部窗口内检测峰并对各峰积分；可视化原始曲线、峰标记与基线段。\n'
            '使用场景：快速估算单通道峰面积时使用。\n'
            'TPD\n'
            '使用方法：\n'
            '1. 输入：本地文件路径、文件名、mol_weight（m/z 或 "*"）、数据类型、baseline_mode、window_halfwidth、线宽。\n'
            '2. 输出：ECharts 配置 JSON 路径、峰列表、各峰积分值、llm_context 摘要。\n'
            '3. 注意事项：仅支持本地文件；窗口积分在峰密集时可能重叠。\n'
            '4. 成本/备注：快速；支持水平/趋势基线。'
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
    'llm_tool_zh': {
        'belonging_agent': TOOL_AGENT_NAME,
        'scene': [],
        'description': (
            '功能：调用大语言模型处理通用任务。\n'
            '使用场景：需要基于 LLM 的辅助时使用。\n'
            'LLM\n'
            '使用方法：\n'
            '1. 输入：查询或任务描述。\n'
            '2. 输出：LLM 回复。\n'
            '3. 注意事项：通用工具。\n'
            '4. 成本/备注：低。'
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
    'physical_adsorption_echart_data_zh': {
        'belonging_agent': Physical_Adsorption_AGENT_NAME,
        'scene': [SceneEnum.PHYSICAL_ADSORPTION],
        'description': (
            '功能：分析物理吸附仪器报告。\n'
            '使用场景：有气体吸附数据需要分析时使用。\n'
            '物理吸附\n'
            '使用方法：\n'
            '1. 输入：仪器报告。\n'
            '2. 输出：分析后的数据。\n'
            '3. 注意事项：仅针对物理吸附。\n'
            '4. 成本/备注：低。'
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
    'file_parse_zh': {
        'belonging_agent': FILE_PARSE_AGENT_NAME,
        'scene': [SceneEnum.UNIVERSAL],
        'description': (
            '功能：解析各类文件内容并提取关键信息。\n'
            '使用场景：需要从文件中提取信息、且无专用提取工具时使用。\n'
            '通用工具\n'
            '使用方法：\n'
            '1. 输入：文件（TXT、PDF、Word、Excel、PNG、JPG 等）。\n'
            '2. 输出：以文本形式呈现的提取信息。\n'
            '3. 注意事项：仅返回文本，不支持生成任何格式的文件。\n'
            '4. 成本/备注：低。'
        ),
        'alternative': [],
        'bypass_confirmation': True,
        'self_check': False,
    },
}

    