from agents.matmaster_agent.constant import SKU_MAPPING


def dpa_cost_func(tool) -> tuple[int, int]:
    photon_cost = 0
    if tool.name == 'optimize_structure':
        photon_cost = 200

    return photon_cost, SKU_MAPPING['matmaster']
