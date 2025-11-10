import logging
import os
from typing import Any, Dict, List, Optional

from agents.matmaster_agent.constant import SKU_MAPPING
from agents.matmaster_agent.services.structure import get_info_by_path

from .structure_analyzer import StructureAnalyzer, calculate_apex_cost


def _calculate_cell_volume(matrix: Optional[List[List[float]]]) -> float:
    """根据晶胞矩阵计算体积（Å³）"""
    if not matrix or len(matrix) != 3:
        return 0.0

    try:
        a, b, c = matrix
        volume = (
            a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])
        )
        return abs(float(volume))
    except (TypeError, ValueError, IndexError):
        logger.warning('[_get_structure_info] 晶胞体积计算失败，返回0.0')
        return 0.0


logger = logging.getLogger(__name__)


def _get_structure_format(structure_url: str) -> str:
    """
    根据文件扩展名判断结构文件格式

    Args:
        structure_url: 结构文件的URL或路径

    Returns:
        文件格式字符串 (cif, poscar, stru, xyz等)
    """
    cleaned_url = structure_url.split('?')[0]
    filename = os.path.basename(cleaned_url).lower()

    # 先根据后缀判断
    if filename.endswith('.cif'):
        return 'CIF'
    if filename.endswith(('.poscar', '.vasp', '.contcar')):
        return 'POSCAR'
    if filename.endswith(('.stru', '.abacus')):
        return 'STRU'
    if filename.endswith('.xyz'):
        return 'XYZ'

    # 再根据文件名关键词匹配
    if 'poscar' in filename or 'contcar' in filename or 'vasp' in filename:
        return 'POSCAR'
    if 'stru' in filename or 'abacus' in filename:
        return 'STRU'
    if 'cif' in filename:
        return 'CIF'
    if 'xyz' in filename:
        return 'XYZ'

    # 默认尝试POSCAR格式
    logger.warning(f"无法识别文件格式，默认使用POSCAR: {structure_url}")
    return 'POSCAR'


async def _get_structure_info(structure_url: str) -> Optional[Dict[str, Any]]:
    """
    获取结构文件的详细信息

    Args:
        structure_url: 结构文件的URL或路径

    Returns:
        包含原子类型、原子数量、晶胞信息的字典，失败返回None
    """
    logger.info('[_get_structure_info] ========== 开始分析结构 ==========')
    logger.info(f"[_get_structure_info] 结构URL: {structure_url}")

    try:
        # 判断文件格式
        file_format = _get_structure_format(structure_url)
        logger.info(f"[_get_structure_info] 识别的文件格式: {file_format}")

        # 调用服务获取结构信息
        logger.info('[_get_structure_info] 调用 get_info_by_path 获取结构信息...')
        structure_info = await get_info_by_path(structure_url, file_format)

        logger.info(
            f"[_get_structure_info] get_info_by_path 返回类型: {type(structure_info)}"
        )
        logger.info(
            f"[_get_structure_info] get_info_by_path 返回键: {list(structure_info.keys()) if isinstance(structure_info, dict) else 'N/A'}"
        )

        if structure_info and 'data' in structure_info:
            data = structure_info['data']

            # `get_info_by_path` 可能返回列表或字典，根据不同情况处理
            if isinstance(data, list):
                if not data:
                    logger.error('[_get_structure_info] 返回的数据列表为空')
                    return None
                logger.info(
                    f"[_get_structure_info] data 为列表，取第一个元素进行解析 (length={len(data)})"
                )
                data = data[0]

            if not isinstance(data, dict):
                logger.error(
                    f"[_get_structure_info] 无法解析的 data 类型: {type(data)}"
                )
                return None

            logger.info('[_get_structure_info] 成功获取结构数据')

            atoms: List[Dict[str, Any]] = data.get('atoms', []) or []

            # 兼容接口未返回 elements/elementCount 的情况
            atom_counts = data.get('elementCount') or {}
            if not atom_counts and atoms:
                for atom in atoms:
                    element = atom.get('formula') or atom.get('element')
                    if not element:
                        continue
                    atom_counts[element] = atom_counts.get(element, 0) + 1

            atom_types = data.get('elements') or list(atom_counts.keys())
            if not atom_types and atoms:
                atom_types = sorted(
                    {
                        atom.get('formula') or atom.get('element')
                        for atom in atoms
                        if atom.get('formula') or atom.get('element')
                    }
                )

            total_atoms = data.get('atomCount')
            if not total_atoms:
                if atom_counts:
                    total_atoms = sum(atom_counts.values())
                else:
                    total_atoms = len(atoms)

            lattice = data.get('lattice') or {
                'length': data.get('length'),
                'angle': data.get('angle'),
                'matrix': data.get('matrix'),
            }

            lattice_volume = data.get('volume')
            if lattice_volume is None:
                matrix = data.get('matrix')
                lattice_volume = _calculate_cell_volume(matrix)

            result = {
                'atom_types': atom_types,
                'atom_counts': atom_counts,
                'total_atoms': total_atoms,
                'lattice': lattice,
                'lattice_volume': lattice_volume or 0.0,
            }

            logger.info('[_get_structure_info] 解析结果:')
            logger.info(f"[_get_structure_info]   - 原子类型: {result['atom_types']}")
            logger.info(f"[_get_structure_info]   - 原子数量: {result['atom_counts']}")
            logger.info(f"[_get_structure_info]   - 总原子数: {result['total_atoms']}")
            logger.info(
                f"[_get_structure_info]   - 晶胞体积: {result['lattice_volume']}"
            )
            logger.info('[_get_structure_info] ========== 结构分析成功 ==========')

            return result
        else:
            logger.error('[_get_structure_info] 获取结构信息失败')
            logger.error(f"[_get_structure_info] 返回数据: {structure_info}")

            # 检查是否有错误信息
            if isinstance(structure_info, dict) and 'error' in structure_info:
                logger.error(
                    f"[_get_structure_info] 错误详情: {structure_info.get('error')}"
                )
                if 'raw_response' in structure_info:
                    logger.error(
                        f"[_get_structure_info] API原始响应: {structure_info.get('raw_response')}"
                    )

            logger.error('[_get_structure_info] ========== 结构分析失败 ==========')
            return None

    except Exception as e:
        logger.error(
            f"[_get_structure_info] 获取结构信息时出错: {str(e)}", exc_info=True
        )
        logger.error('[_get_structure_info] ========== 结构分析异常 ==========')
        return None


def _get_default_cost(tool_name: str) -> int:
    """
    获取默认费用（当无法获取结构信息时使用）

    基于Cu4结构的估算成本（向上取整）

    Args:
        tool_name: 工具名称

    Returns:
        默认费用（photon）
    """
    # 基于Cu4的默认费用估算（单位：photon，100 photon = 1元）
    default_costs = {
        'apex_optimize_structure': 100,  # 5min
        'apex_calculate_vacancy': 400,  # 25min (5+25)
        'apex_calculate_eos': 2500,  # 480min (5+60*8)
        'apex_calculate_phonon': 5000,  # 1000min (5+180*6)
        'apex_calculate_surface': 1000,  # 95min (5+30*3)
        'apex_calculate_gamma': 500,  # 105min (5+10*10)
        'apex_calculate_interstitial': 200,  # 25min (5+10*2)
        'apex_calculate_elastic': 5000,  # 965min (5+40*24)
        'apex_show_and_modify_config': 0,  # 参数查询工具，免费
    }

    return default_costs.get(tool_name, 200)


async def apex_cost_func(tool, args) -> tuple[int, int]:
    """
    APEX计算费用函数

    收费标准：
    - 机器成本：原子数<200时2.56元/小时，>=200时5.12元/小时
    - 基准参考：Cu4结构（4个原子，3.6x3.6x3.6 Ų晶胞）
    - 时间缩放：元素按1:1
    - 真空层处理：晶胞体积>原子占据体积130%时，有效原子数×2

    Args:
        tool: 工具对象
        args: 工具参数字典，包含structure_file等

    Returns:
        (photon费用, SKU_ID)元组
    """
    logger.info('[apex_cost_func] ========================================')
    logger.info(f"[apex_cost_func] 开始计算 {tool.name} 的费用")
    logger.info(f"[apex_cost_func] 工具参数: {args}")
    logger.info('[apex_cost_func] ========================================')

    photon_cost = 0

    try:
        # 获取结构文件URL
        structure_url = args.get('structure_file')
        logger.info(f"[apex_cost_func] 提取的结构文件URL: {structure_url}")

        if not structure_url:
            logger.warning('[apex_cost_func] 未提供结构文件URL，使用默认费用')
            photon_cost = _get_default_cost(tool.name)
            logger.info(f"[apex_cost_func] 默认费用: {photon_cost} photon")
        else:
            logger.info('[apex_cost_func] 开始获取并分析结构信息...')

            # 获取结构信息
            structure_info = await _get_structure_info(structure_url)

            if structure_info:
                logger.info('[apex_cost_func] 结构信息获取成功，开始计算费用...')

                # 使用结构分析器计算费用
                analyzer = StructureAnalyzer(structure_info)
                photon_cost, cost_details = calculate_apex_cost(tool.name, analyzer)

                logger.info('[apex_cost_func] ========== 费用计算详情 ==========')
                logger.info(f"[apex_cost_func] 工具: {tool.name}")
                logger.info(
                    f"[apex_cost_func] 结构: {cost_details.get('structure_summary', 'N/A')}"
                )
                logger.info(
                    f"[apex_cost_func] 基准时间: {cost_details.get('base_time_minutes', 0):.1f} 分钟"
                )
                logger.info(
                    f"[apex_cost_func] 时间缩放因子: {cost_details.get('scaling_factor', 0):.2f}"
                )
                logger.info(
                    f"[apex_cost_func] 预计时间: {cost_details.get('actual_time_hours', 0):.2f} 小时"
                )
                logger.info(
                    f"[apex_cost_func] 机器成本: {cost_details.get('machine_cost_per_hour', 0):.2f} 元/小时"
                )
                logger.info(
                    f"[apex_cost_func] 总费用: {cost_details.get('total_cost_yuan', 0):.2f} 元"
                )
                logger.info(f"[apex_cost_func] Photon费用: {photon_cost} photon")
                logger.info('[apex_cost_func] =====================================')
            else:
                # 无法获取结构信息，使用默认费用
                logger.warning('[apex_cost_func] 无法获取结构信息，使用默认费用')
                photon_cost = _get_default_cost(tool.name)
                logger.info(f"[apex_cost_func] 默认费用: {photon_cost} photon")

    except Exception as e:
        logger.error(f"[apex_cost_func] 计算费用时出错: {str(e)}", exc_info=True)
        # 发生错误时使用默认费用
        photon_cost = _get_default_cost(tool.name)
        logger.error(f"[apex_cost_func] 使用默认费用: {photon_cost} photon")

    logger.info('[apex_cost_func] ========================================')
    logger.info(
        f"[apex_cost_func] {tool.name} 最终费用: {photon_cost} photon ({photon_cost/100:.2f}元)"
    )
    logger.info(f"[apex_cost_func] SKU_ID: {SKU_MAPPING['matmaster']}")
    logger.info('[apex_cost_func] ========================================')

    return photon_cost, SKU_MAPPING['matmaster']
