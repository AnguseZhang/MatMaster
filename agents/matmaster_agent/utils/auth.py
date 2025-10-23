import logging

import requests

from agents.matmaster_agent.constant import (
    BOHRIUM_API_URL,
    MATMASTER_AGENT_NAME,
    OPENAPI_HOST,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def ak_to_username(access_key: str) -> str:
    url = f"{OPENAPI_HOST}/openapi/v1/account/info"
    headers = {
        'AccessKey': access_key,
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': f"{OPENAPI_HOST.split('//')[1]}",
    }
    try:
        logger.info(f"[{MATMASTER_AGENT_NAME}]:[ak_to_username] headers = {headers}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误异常

        data = response.json()
        if data.get('code') == 0:
            user_data = data.get('data', {})
            email = user_data.get('email', '')
            phone = user_data.get('phone', '')
            if not email and not phone:
                raise ValueError(
                    'Username not found in response. Please bind your email or phone at https://www.bohrium.com/settings/user.'
                )
            username = email if email else phone
            return username
        else:
            raise Exception(f"API error: {data}")
    except requests.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to get user info: {e}")


def ak_to_ticket(access_key: str, expiration: int = 48) -> str:  # 48 hours
    url = (
        f"{BOHRIUM_API_URL}/bohrapi/v1/ticket/get?expiration={expiration}&preOrderId=0"
    )
    headers = {
        'Brm-AK': access_key,
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': f"{BOHRIUM_API_URL.split('//')[1]}",
        'Connection': 'keep-alive',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 0:
            ticket = data.get('data', {}).get('ticket', '')
            if not ticket:
                raise ValueError('Ticket not found in response.')
            return ticket
        else:
            raise Exception(f"API error: {data}")
    except requests.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")
    except Exception as e:
        raise Exception(f"Failed to get ticket: {e}")
