from agents.matmaster_agent.constant import SKU_MAPPING
from agents.matmaster_agent.services.structure import get_info_by_path


def apex_cost_func(tool, args) -> tuple[int, int]:
    photon_cost = 0
    structure_url = args['xxxx']
    format = 'xxxx'
    get_info_by_path(structure_url, format)

    return photon_cost, SKU_MAPPING['matmaster']
