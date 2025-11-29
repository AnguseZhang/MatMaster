"""
统一维护各个子 Agent 的运行时配置，例如：
- Docker 镜像地址（image_address）
- Bohrium 机器类型（machine_type）

注意：
- 本模块只声明纯数据，不依赖任何其他 matmaster 代码，避免循环导入。
- 其他模块（如 mapping.py、各 *_agent/constant.py）只从这里读取配置。
"""

# Agent 镜像地址映射（使用字符串作为 key，避免循环导入）
AGENT_IMAGE_ADDRESS = {
    'ABACUS_calculation_agent': 'registry.dp.tech/dptech/dp/native/prod-22618/abacusagenttools-matmaster-new-tool:v0.2.3',
    'apex_agent': 'registry.dp.tech/dptech/dp/native/prod-16664/apex-agent-all:0.2.1',
    'LAMMPS_agent': 'registry.dp.tech/dptech/lammps-agent:9ae769be',
    'vaspkit_agent': 'registry.dp.tech/dptech/dp/native/prod-16664/vaspkit-agent:0.0.1',
    'dpa_calculator_agent': 'registry.dp.tech/dptech/dpa-calculator:a86b37cc',
    'compdart_agent': 'registry.dp.tech/dptech/dpa-calculator:50e69ca3',
    'piloteye_electro_agent': 'registry.dp.tech/dptech/dp/native/prod-13375/piloteye:mcpv03',
    'organic_reaction_agent': 'registry.dp.tech/dptech/dp/native/prod-13364/autots:0.1.0',
    'HEA_assistant_agent': 'registry.dp.tech/dptech/dp/native/prod-485756/mcphub:heafinal',
    'thermoelectric_agent': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:20',
    'superconductor_agent': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:20',
    'finetune_dpa_agent': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-superconductor:20',
    'convexhull_agent': 'registry.dp.tech/dptech/dp/native/prod-435364/dpa-thermo-convexhull:20',
    'structure_generate_agent': 'registry.dp.tech/dptech/dpa-calculator:46bc2c88',
}

# Agent 机器类型映射（使用字符串作为 key，避免循环导入）
# 如果 agent 未在此字典中，默认使用 'c2_m4_cpu'
AGENT_MACHINE_TYPE = {
    'ABACUS_calculation_agent': 'c32_m128_cpu',
    'apex_agent': 'c2_m4_cpu',  # 默认值，未明确设置
    'LAMMPS_agent': 'c16_m64_1 * NVIDIA 4090',
    'vaspkit_agent': 'c2_m8_cpu',
    'dpa_calculator_agent': 'c16_m64_1 * NVIDIA 4090',
    'compdart_agent': 'c16_m64_1 * NVIDIA 4090',
    'piloteye_electro_agent': 'c2_m8_cpu',
    'organic_reaction_agent': 'c32_m128_cpu',
    'HEA_assistant_agent': 'c2_m4_cpu',  # 默认值，未明确设置
    'thermoelectric_agent': 'c16_m64_1 * NVIDIA 4090',
    'superconductor_agent': 'c16_m64_1 * NVIDIA 4090',
    'finetune_dpa_agent': 'c16_m64_1 * NVIDIA 4090',
    'convexhull_agent': 'c16_m64_1 * NVIDIA 4090',
    'structure_generate_agent': 'c8_m32_1 * NVIDIA 4090',
}
