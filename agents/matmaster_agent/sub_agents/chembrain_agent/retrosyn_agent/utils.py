import asyncio
import base64
import shutil
import tarfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

import aiofiles
import aiohttp

from ..tools.io import upload_base64_to_oss


async def extract_convert_and_upload(tgz_url: str, temp_dir: str = './tmp') -> dict:
    """
    使用当前目录下的临时文件夹处理文件
    :param tgz_url: 要下载的tgz文件URL
    :param temp_dir: 临时目录路径（默认当前目录下的tmp文件夹）
    :return: 上传结果字典
    """
    # 创建临时目录（如果不存在）
    temp_path = Path(temp_dir)
    temp_path.mkdir(exist_ok=True, parents=True)

    try:
        # 获取所有JPG文件的Base64编码
        jpg_files = await extract_jpg_from_tgz_url(tgz_url, temp_path)
        conversion_tasks = [jpg_to_base64(jpg) for jpg in jpg_files]
        base64_results = await asyncio.gather(*conversion_tasks)

        # 准备上传任务
        upload_tasks = []
        for jpg_path, b64_data in base64_results:
            filename = jpg_path.name
            oss_path = f"retrosyn/image_{filename}_{int(time.time())}.jpg"
            upload_tasks.append(upload_to_oss_wrapper(b64_data, oss_path, filename))

        return {
            filename: result
            for item in await asyncio.gather(*upload_tasks)
            for filename, result in item.items()
        }
    finally:
        # 清理临时目录
        shutil.rmtree(temp_path, ignore_errors=True)


async def upload_to_oss_wrapper(
    b64_data: str, oss_path: str, filename: str
) -> Dict[str, dict]:
    """上传包装器，保留原始文件名信息"""
    result = await upload_base64_to_oss(b64_data, oss_path)

    return {filename: result}


async def jpg_to_base64(jpg_path: Path) -> Tuple[Path, str]:
    """异步将JPG文件转换为Base64编码"""
    async with aiofiles.open(jpg_path, 'rb') as f:
        content = await f.read()
        return (jpg_path, base64.b64encode(content).decode('utf-8'))


async def extract_jpg_from_tgz_url(tgz_url: str, temp_path: Path) -> List[Path]:
    """使用指定临时目录处理文件"""
    async with aiohttp.ClientSession() as session:
        tgz_path = temp_path / 'downloaded.tgz'

        await download_file(session, tgz_url, tgz_path)
        await extract_tarfile(tgz_path, temp_path)

        return await find_jpg_files(temp_path)


async def download_file(session: aiohttp.ClientSession, url: str, dest: Path) -> None:
    """异步下载文件"""
    async with session.get(url) as response:
        response.raise_for_status()
        async with aiofiles.open(dest, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                await f.write(chunk)


async def extract_tarfile(tgz_path: Path, extract_to: Path) -> None:
    """异步解压tar文件(实际解压是同步操作)"""
    # 使用run_in_executor避免阻塞事件循环
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: tarfile.open(tgz_path).extractall(extract_to)
    )


async def find_jpg_files(directory: Path) -> List[Path]:
    """异步查找JPG文件"""
    # 使用run_in_executor避免阻塞事件循环
    loop = asyncio.get_running_loop()

    def _sync_find():
        return list(directory.rglob('*.jpg')) + list(directory.rglob('*.JPG'))

    return await loop.run_in_executor(None, _sync_find)
