import logging
from typing import Any, Dict, Optional

from agents.matmaster_agent.constant import SKU_MAPPING
from agents.matmaster_agent.services.structure import get_info_by_path

from .structure_analyzer import StructureAnalyzer, calculate_apex_cost

logger = logging.getLogger(__name__)


def _get_structure_format(structure_url: str) -> str:
    """
    根据文件扩展名判断结构文件格式

    Args:
        structure_url: 结构文件的URL或路径

    Returns:
        文件格式字符串 (cif, poscar, stru, xyz等)
    """
    url_lower = structure_url.lower()

    if url_lower.endswith('.cif'):
        return 'cif'
    elif url_lower.endswith(('.poscar', '.vasp', '.contcar')):
        return 'poscar'
    elif url_lower.endswith(('.stru', '.abacus')):
        return 'stru'
    elif url_lower.endswith('.xyz'):
        return 'xyz'
    else:
        # 默认尝试poscar格式
        logger.warning(f"无法识别文件格式，默认使用poscar: {structure_url}")
        return 'poscar'


async def _get_structure_info(structure_url: str) -> Optional[Dict[str, Any]]:
    """
    获取结构文件的详细信息

    Args:
        structure_url: 结构文件的URL或路径

    Returns:
        包含原子类型、原子数量、晶胞信息的字典，失败返回None
    """
    try:
        # 判断文件格式
        file_format = _get_structure_format(structure_url)

        # 调用服务获取结构信息
        structure_info = await get_info_by_path(structure_url, file_format)

        if structure_info and 'data' in structure_info:
            data = structure_info['data']
            logger.info(f"成功获取结构信息: {structure_info}")
            return {
                'atom_types': data.get('elements', []),  # 原子类型列表
                'atom_counts': data.get('elementCount', {}),  # 各原子数量
                'total_atoms': sum(data.get('elementCount', {}).values()),  # 总原子数
                'lattice': data.get('lattice', {}),  # 晶胞参数
                'lattice_volume': data.get('volume', 0.0),  # 晶胞体积
            }
        else:
            logger.error(f"获取结构信息失败: {structure_info}")
            return None

    except Exception as e:
        logger.error(f"获取结构信息时出错: {str(e)}")
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
        'apex_calculate_vacancy': 200,  # 15min (5+10)
        'apex_calculate_eos': 1500,  # 245min (5+30*8)
        'apex_calculate_phonon': 5000,  # 1085min (5+180*6)
        'apex_calculate_surface': 1000,  # 95min (5+30*3)
        'apex_calculate_gamma': 400,  # 45min (5+10*4)
        'apex_calculate_interstitial': 200,  # 25min (5+10*2)
        'apex_calculate_elastic': 5000,  # 965min (5+40*24)
    }

    return default_costs.get(tool_name, 200)


async def apex_cost_func(tool, args) -> tuple[int, int]:
    """
    APEX计算费用函数

    收费标准：
    - 机器成本：原子数<200时2.56元/小时，>=200时5.12元/小时
    - 基准参考：Cu4结构（4个原子，3.6x3.6x3.6 Ų晶胞）
    - 时间缩放：单元素按1:1.5，多元素按1:2
    - 真空层处理：晶胞体积>原子占据体积130%时，有效原子数×2

    Args:
        tool: 工具对象
        args: 工具参数字典，包含structure_file等

    Returns:
        (photon费用, SKU_ID)元组
    """
    photon_cost = 0

    try:
        # 获取结构文件URL
        structure_url = args.get('structure_file')

        if not structure_url:
            logger.warning(f'[{tool.name}] 未提供结构文件URL，使用默认费用')
            photon_cost = _get_default_cost(tool.name)
        else:
            # 获取结构信息
            structure_info = await _get_structure_info(structure_url)

            if structure_info:
                # 使用结构分析器计算费用
                analyzer = StructureAnalyzer(structure_info)
                photon_cost, cost_details = calculate_apex_cost(tool.name, analyzer)

                logger.info(
                    f"[{tool.name}] 费用计算完成: {photon_cost} photon "
                    f"({cost_details.get('total_cost_yuan', 0):.2f}元)"
                )
            else:
                # 无法获取结构信息，使用默认费用
                logger.warning(f'[{tool.name}] 无法获取结构信息，使用默认费用')
                photon_cost = _get_default_cost(tool.name)

    except Exception as e:
        logger.error(f"[{tool.name}] 计算费用时出错: {str(e)}", exc_info=True)
        # 发生错误时使用默认费用
        photon_cost = _get_default_cost(tool.name)

    logger.info(f"[{tool.name}] 最终费用: {photon_cost} photon")
    return photon_cost, SKU_MAPPING['matmaster']
