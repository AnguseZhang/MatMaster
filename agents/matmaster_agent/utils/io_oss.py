import asyncio
import base64
import os
import shutil
import tarfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

import aiofiles
import aiohttp
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider


# Step1: download tgz -> unzip -> find jpg_files
async def _download_file(session: aiohttp.ClientSession, url: str, dest: Path) -> None:
    """异步下载文件"""
    async with session.get(url) as response:
        response.raise_for_status()
        async with aiofiles.open(dest, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                await f.write(chunk)


async def _extract_tarfile(tgz_path: Path, extract_to: Path) -> None:
    """异步解压tar文件(实际解压是同步操作)"""
    # 使用run_in_executor避免阻塞事件循环
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: tarfile.open(tgz_path).extractall(extract_to)
    )


async def _find_all_files(directory: Path) -> List[Path]:
    """异步递归列出目录下的所有文件（包括子目录）"""
    loop = asyncio.get_running_loop()

    def _sync_list():
        return [
            p
            for p in directory.rglob('*')
            if p.is_file() and not p.suffix.lower() in {'.tgz'}
        ]

    return await loop.run_in_executor(None, _sync_list)


async def extract_files_from_tgz_url(tgz_url: str, temp_path: Path) -> List[Path]:
    """使用指定临时目录处理文件"""
    async with aiohttp.ClientSession() as session:
        tgz_path = temp_path / 'downloaded.tgz'

        await _download_file(session, tgz_url, tgz_path)
        await _extract_tarfile(tgz_path, temp_path)

        return await _find_all_files(temp_path)


# Step2: jpg -> base64
async def file_to_base64(file_path: Path) -> Tuple[Path, str]:
    """异步将JPG文件转换为Base64编码"""
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
        return (file_path, base64.b64encode(content).decode('utf-8'))


# Step3: Upload to OSS
async def upload_to_oss_wrapper(
    b64_data: str, oss_path: str, filename: str
) -> Dict[str, dict]:
    def _sync_upload_base64_to_oss(data: str, oss_path: str) -> str:
        try:
            auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
            endpoint = os.environ['OSS_ENDPOINT']
            bucket_name = os.environ['OSS_BUCKET_NAME']
            bucket = oss2.Bucket(auth, endpoint, bucket_name)
            bucket.put_object(oss_path, base64.b64decode(data))
            return f"https://{bucket_name}.oss-cn-zhangjiakou.aliyuncs.com/{oss_path}"
        except Exception as e:
            return str(e)

    async def upload_base64_to_oss(data: str, oss_path: str) -> dict:
        return await asyncio.to_thread(_sync_upload_base64_to_oss, data, oss_path)

    """上传包装器，保留原始文件名信息"""
    result = await upload_base64_to_oss(b64_data, oss_path)

    return {filename: result}


# Main Func
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
        files = await extract_files_from_tgz_url(tgz_url, temp_path)
        conversion_tasks = [file_to_base64(file) for file in files]
        base64_results = await asyncio.gather(*conversion_tasks)

        # 准备上传任务
        upload_tasks = []
        for file_path, b64_data in base64_results:
            filename = file_path.name
            oss_path = f"agent/{int(time.time())}_{filename}"
            upload_tasks.append(upload_to_oss_wrapper(b64_data, oss_path, filename))

        return {
            filename: result
            for item in await asyncio.gather(*upload_tasks)
            for filename, result in item.items()
        }
    finally:
        # 清理临时目录
        shutil.rmtree(temp_path, ignore_errors=True)


async def update_tgz_dict(tool_result: dict):
    new_tool_result = {}
    tgz_flag = False
    for k, v in tool_result.items():
        new_tool_result[k] = v
        if isinstance(v, str) and v.startswith('https') and v.endswith('tgz'):
            tgz_flag = True
            new_tool_result.update(**await extract_convert_and_upload(v))

    return tgz_flag, new_tool_result
