from agents.matmaster_agent.constant import SKU_MAPPING


def cost_func(tool) -> tuple[int, int]:
    photon_cost = 0
    if tool.name == 'fetch_bohrium_crystals':
        photon_cost = 50

    return photon_cost, SKU_MAPPING['matmaster']
