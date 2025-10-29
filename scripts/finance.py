import requests
from dotenv import find_dotenv, load_dotenv

from agents.matmaster_agent.constant import (
    FINANCE_WALLET_INFO_API,
    GOODS_SKU_LIST_API,
    MATERIALS_ORG_ID,
)

load_dotenv(find_dotenv())

sku_id = 10808


def sku_list():
    payload = {'skuIds': [sku_id]}
    response = requests.post(
        GOODS_SKU_LIST_API, json=payload, headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    data = response.json()

    print(data)


def wallet_info():
    response = requests.get(
        f'{FINANCE_WALLET_INFO_API}/{MATERIALS_ORG_ID}',
        headers={'Content-Type': 'application/json'},
    )
    response.raise_for_status()
    data = response.json()
    print(data)


if __name__ == '__main__':
    wallet_info()
