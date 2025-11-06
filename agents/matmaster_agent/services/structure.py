import asyncio
import json
import logging
from typing import Optional

import aiohttp

from agents.matmaster_agent.constant import BOHRIUM_COM, MATMASTER_AGENT_NAME

logger = logging.getLogger(__name__)


async def fetch_file_content(url: str, timeout: int = 30) -> Optional[str]:
    """
    异步获取 URL 文件内容
    Args:
        url: 文件 URL 链接
        timeout: 请求超时时间（秒）
    Returns:
        文件内容字符串，如果失败返回 None
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(url) as response:
                response.raise_for_status()  # 如果状态码不是 200，抛出异常
                content = await response.text()
                return content
    except aiohttp.ClientError as e:
        print(f"网络请求错误: {e}")
        return None
    except asyncio.TimeoutError:
        print(f"请求超时: {timeout}秒")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None


async def get_info_by_path(file_url, format) -> dict:
    info_by_path_url = (
        f"{BOHRIUM_COM}/api/materials_db/public/v1/material_visualization/info_by_str"
    )
    body_json = {'fileContent': await fetch_file_content(file_url), 'format': format}
    async with aiohttp.ClientSession() as session:
        async with session.post(info_by_path_url, json=body_json) as response:
            raw_res = await response.text()
            logger.info(f"[{MATMASTER_AGENT_NAME}] raw_res = {raw_res}")
            dict_res = json.loads(raw_res)
            logger.info(f"[{MATMASTER_AGENT_NAME}] res = {dict_res}")

    return dict_res
