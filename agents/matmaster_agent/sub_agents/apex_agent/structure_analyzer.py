"""
APEX结构分析模块
用于分析材料结构的原子数量、晶胞大小等信息，为费用计算提供依据
"""

import logging
import math
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class StructureAnalyzer:
    """结构分析器，用于分析材料结构特征"""

    # 机器成本配置（元/小时）
    MACHINE_COST_SMALL = 2.56  # 原子数 < 200
    MACHINE_COST_LARGE = 5.12  # 原子数 >= 200

    # 基准结构：Cu4 (4个原子，晶胞3.6x3.6x3.6 Å³)
    REFERENCE_ATOMS = 4
    REFERENCE_CELL_SIZE = 3.6

    # 真空层阈值：如果晶胞体积 > 原子占据体积的130%，则视为有显著真空层
    VACUUM_THRESHOLD = 1.3

    def __init__(self, structure_info: Dict):
        """
        初始化结构分析器

        Args:
            structure_info: 从services.structure.get_info_by_path获取的结构信息
        """
        self.structure_info = structure_info
        self.atom_types = structure_info.get('atom_types', [])
        self.atom_counts = structure_info.get('atom_counts', {})
        self.total_atoms = structure_info.get('total_atoms', 0)
        self.lattice = structure_info.get('lattice', {})
        self.lattice_volume = structure_info.get('lattice_volume', 0.0)

        # 计算有效原子数（考虑真空层）
        self.effective_atoms = self._calculate_effective_atoms()

    def _calculate_effective_atoms(self) -> int:
        """
        计算有效原子数（考虑晶胞中的真空层）

        如果晶胞体积显著大于原子占据体积，说明存在真空层，
        需要将原子数乘以2来反映实际计算量

        Returns:
            有效原子数
        """
        try:
            # 估算原子占据的体积
            # 假设每个原子占据约10 Å³的空间（粗略估计）
            estimated_atom_volume = self.total_atoms * 10.0

            # 计算体积比
            if estimated_atom_volume > 0:
                volume_ratio = self.lattice_volume / estimated_atom_volume
                logger.info(
                    f"晶胞体积: {self.lattice_volume:.2f} Ų, "
                    f"估算原子体积: {estimated_atom_volume:.2f} Ų, "
                    f"体积比: {volume_ratio:.2f}"
                )

                # 如果晶胞体积 > 原子体积的130%，说明有显著真空层
                if volume_ratio > self.VACUUM_THRESHOLD:
                    effective_atoms = int(self.total_atoms * 2)
                    logger.info(
                        f"检测到显著真空层，有效原子数: {self.total_atoms} -> {effective_atoms}"
                    )
                    return effective_atoms

            return self.total_atoms

        except Exception as e:
            logger.error(f"计算有效原子数时出错: {str(e)}")
            return self.total_atoms

    def get_element_count(self) -> int:
        """获取元素种类数量"""
        return len(self.atom_types)

    def is_multi_element(self) -> bool:
        """判断是否为多元素体系"""
        return self.get_element_count() > 1

    def get_machine_cost_per_hour(self) -> float:
        """
        获取机器成本（元/小时）

        Returns:
            机器成本
        """
        if self.effective_atoms < 200:
            return self.MACHINE_COST_SMALL
        else:
            return self.MACHINE_COST_LARGE

    def estimate_time_scaling_factor(self) -> float:
        """
        估算时间缩放因子（相对于Cu4基准结构）

        单元素: 按原子数比例1:1.5逐步提升
        多元素: 按1:2比例提升

        Returns:
            时间缩放因子
        """
        atom_ratio = self.effective_atoms / self.REFERENCE_ATOMS

        if self.is_multi_element():
            # 多元素：1:2比例
            scaling_factor = atom_ratio**2
        else:
            # 单元素：1:1.5比例
            scaling_factor = atom_ratio**1.5

        logger.info(
            f"时间缩放因子: {scaling_factor:.2f} "
            f"(有效原子数: {self.effective_atoms}, "
            f"元素种类: {self.get_element_count()})"
        )

        return scaling_factor

    def get_structure_summary(self) -> str:
        """获取结构摘要信息"""
        return (
            f"原子数: {self.total_atoms}, "
            f"有效原子数: {self.effective_atoms}, "
            f"元素种类: {self.get_element_count()} ({', '.join(self.atom_types)}), "
            f"晶胞体积: {self.lattice_volume:.2f} Ų"
        )


class ApexTaskConfig:
    """APEX计算任务配置（基于Cu4基准）"""

    # Cu4基准计算时间（分钟）
    BASE_OPTIMIZE_TIME = 5  # 几何优化

    # 各性质计算的配置：(几何优化时间, 单个性质计算时间, 性质计算任务数)
    TASK_CONFIGS = {
        'apex_optimize_structure': (5, 0, 0),  # 只有几何优化
        'apex_calculate_vacancy': (5, 10, 1),  # 几何优化 + 空位计算×元素数
        'apex_calculate_eos': (5, 30, 8),  # 几何优化 + 8个性质计算
        'apex_calculate_phonon': (5, 180, 6),  # 几何优化 + 6个性质计算(3h=180min)
        'apex_calculate_surface': (5, 30, 3),  # 几何优化 + 3个表面计算
        'apex_calculate_gamma': (5, 10, 4),  # 几何优化 + 4个性质计算
        'apex_calculate_interstitial': (5, 10, 2),  # 几何优化 + 2个性质计算
        'apex_calculate_elastic': (5, 40, 24),  # 几何优化 + 24个性质计算
    }

    @classmethod
    def get_base_time(cls, tool_name: str, element_count: int = 1) -> float:
        """
        获取基准计算时间（分钟）

        Args:
            tool_name: 工具名称
            element_count: 元素种类数（对vacancy有影响）

        Returns:
            基准计算时间（分钟）
        """
        if tool_name not in cls.TASK_CONFIGS:
            logger.warning(f"未知的工具名称: {tool_name}，使用默认配置")
            return 30.0  # 默认30分钟

        opt_time, calc_time, calc_count = cls.TASK_CONFIGS[tool_name]

        # 对于vacancy，计算任务数量要乘以元素数
        if tool_name == 'apex_calculate_vacancy':
            calc_count = calc_count * element_count

        total_time = opt_time + calc_time * calc_count
        return float(total_time)


def calculate_apex_cost(
    tool_name: str, structure_analyzer: StructureAnalyzer
) -> Tuple[int, Dict]:
    """
    计算APEX任务的费用

    Args:
        tool_name: 工具名称
        structure_analyzer: 结构分析器

    Returns:
        (photon费用, 费用详情字典)
    """
    try:
        # 获取基准计算时间（Cu4）
        element_count = structure_analyzer.get_element_count()
        base_time_minutes = ApexTaskConfig.get_base_time(tool_name, element_count)

        # 获取时间缩放因子
        scaling_factor = structure_analyzer.estimate_time_scaling_factor()

        # 计算实际计算时间
        actual_time_minutes = base_time_minutes * scaling_factor
        actual_time_hours = actual_time_minutes / 60.0

        # 获取机器成本
        machine_cost_per_hour = structure_analyzer.get_machine_cost_per_hour()

        # 计算总成本（元）
        total_cost_yuan = actual_time_hours * machine_cost_per_hour

        # 转换为photon（100 photon = 1元）- 向上取整，保证开发者收益
        photon_cost = math.ceil(total_cost_yuan * 100)

        # 费用详情
        cost_details = {
            'structure_summary': structure_analyzer.get_structure_summary(),
            'base_time_minutes': base_time_minutes,
            'scaling_factor': scaling_factor,
            'actual_time_minutes': actual_time_minutes,
            'actual_time_hours': actual_time_hours,
            'machine_cost_per_hour': machine_cost_per_hour,
            'total_cost_yuan': total_cost_yuan,
            'photon_cost': photon_cost,
        }

        logger.info(
            f"[{tool_name}] 费用计算详情:\n"
            f"  结构: {cost_details['structure_summary']}\n"
            f"  基准时间: {base_time_minutes:.1f}分钟 (Cu4)\n"
            f"  缩放因子: {scaling_factor:.2f}\n"
            f"  预计时间: {actual_time_minutes:.1f}分钟 ({actual_time_hours:.2f}小时)\n"
            f"  机器成本: {machine_cost_per_hour:.2f}元/小时\n"
            f"  总费用: {total_cost_yuan:.2f}元 = {photon_cost} photon"
        )

        return photon_cost, cost_details

    except Exception as e:
        logger.error(f"计算费用时出错: {str(e)}")
        # 返回默认费用
        default_cost = 500  # 默认5元
        return default_cost, {'error': str(e), 'photon_cost': default_cost}
