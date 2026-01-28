import asyncio
import base64
import logging
import os
import re
import shutil
import tarfile
import time
import zipfile
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

import aiofiles
import aiohttp
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


@dataclass(frozen=True, slots=True)
class ReportUploadParams:
    """Parameters for uploading a markdown report to OSS."""

    report_markdown: str
    session_id: str
    invocation_id: str
    oss_prefix: str = 'agent/reports'


@dataclass(frozen=True, slots=True)
class ReportUploadResult:
    """Result for uploading a markdown report to OSS."""

    oss_url: str
    oss_path: str
    filename: str


@asynccontextmanager
async def temp_dir(path: str = './tmp'):
    """异步上下文管理器创建/清理临时目录"""
    temp_path = Path(path)
    temp_path.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


async def get_filename_from_url(url: str) -> str:
    """
    从 HTTP URL 异步获取文件名：
    1. 尝试解析 Content-Disposition
    2. fallback：从 URL 路径推断
    """
    FILENAME_RE = re.compile(r'filename\*?=(?:"?)([^";]+)')
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=True) as resp:
            cd = resp.headers.get('Content-Disposition')
            if cd:
                match = FILENAME_RE.search(cd)
                if match:
                    return unquote(match.group(1))

    return 'unknown'


# Step1: download tgz -> unzip -> find jpg_files
async def _download_file(session: aiohttp.ClientSession, url: str, dest: Path) -> None:
    """异步下载文件"""
    async with session.get(url) as response:
        response.raise_for_status()
        async with aiofiles.open(dest, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                await f.write(chunk)


async def _extract_compressed_file(compressed_path: Path, extract_to: Path) -> None:
    loop = asyncio.get_running_loop()

    def _sync_extract():
        extract_to.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"Extracting {compressed_path}, file exists? {Path(compressed_path).exists()}"
        )

        if tarfile.is_tarfile(compressed_path):
            with tarfile.open(compressed_path) as tf:
                tf.extractall(extract_to)
        elif zipfile.is_zipfile(compressed_path):
            with zipfile.ZipFile(compressed_path) as zf:
                zf.extractall(extract_to)
        else:
            raise ValueError(f"Unsupported archive: {compressed_path}")

    await loop.run_in_executor(None, _sync_extract)


async def _find_all_files(directory: Path) -> List[Path]:
    """异步递归列出目录下的所有文件（包括子目录）"""
    loop = asyncio.get_running_loop()

    def _sync_list():
        return [
            p
            for p in directory.rglob('*')
            if p.is_file() and not p.suffix.lower() in {'.tgz', '.zip'}
        ]

    return await loop.run_in_executor(None, _sync_list)


async def extract_files_from_compressed_file_url(
    compressed_file_url: str, temp_path: Path
) -> List[Path]:
    """使用指定临时目录处理文件"""
    async with aiohttp.ClientSession() as session:
        temp_compressed_file = (
            'downloaded.tgz'
            if compressed_file_url.endswith('.tgz')
            else 'downloaded.zip'
        )
        compressed_path = temp_path / temp_compressed_file

        await _download_file(session, compressed_file_url, compressed_path)
        await _extract_compressed_file(
            compressed_path=compressed_path, extract_to=temp_path
        )

        return await _find_all_files(temp_path)


async def read_file_bytes(file_path: Path) -> bytes:
    """异步读取文件内容并返回字节数据"""
    async with aiofiles.open(file_path, 'rb') as f:
        return await f.read()


def bytes_to_base64(data: bytes) -> str:
    """将字节数据转为 Base64 字符串"""
    return base64.b64encode(data).decode('utf-8')


# Step2: jpg -> base64
async def file_to_base64(file_path: Path) -> Tuple[Path, str]:
    """组合调用：读取文件 + 转 Base64"""
    content = await read_file_bytes(file_path)
    return file_path, bytes_to_base64(content)


# Step3: Upload to OSS
async def upload_to_oss_wrapper(
    b64_data: str,
    oss_path: str,
    filename: str,
    *,
    with_download_headers: bool = False,
) -> Dict[str, dict]:
    def _sync_upload_base64_to_oss(data: str, oss_path: str) -> str:
        try:
            auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
            endpoint = os.environ['OSS_ENDPOINT']
            bucket_name = os.environ['OSS_BUCKET_NAME']
            bucket = oss2.Bucket(auth, endpoint, bucket_name)
            headers = None
            if with_download_headers:
                headers = {
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'text/markdown',
                }
            bucket.put_object(oss_path, base64.b64decode(data), headers=headers)
            return f"https://{bucket_name}.oss-cn-zhangjiakou.aliyuncs.com/{oss_path}"
        except Exception as e:
            return str(e)

    async def upload_base64_to_oss(data: str, oss_path: str) -> dict:
        return await asyncio.to_thread(_sync_upload_base64_to_oss, data, oss_path)

    """上传包装器，保留原始文件名信息"""
    result = await upload_base64_to_oss(b64_data, oss_path)

    return {filename: result}


async def upload_report_md_to_oss(
    params: ReportUploadParams,
    temp_dir_path: str = './tmp',
) -> Optional[ReportUploadResult]:
    """Upload markdown report content to OSS and return its URL."""

    report_markdown = (params.report_markdown or '').strip()
    if not report_markdown:
        return None

    async with temp_dir(temp_dir_path) as tdir:
        filename = f'matmaster_report_{params.invocation_id}.md'
        md_file_path = tdir / filename
        md_file_path.write_text(report_markdown, encoding='utf-8')

        _, b64_data = await file_to_base64(md_file_path)
        oss_path = f"agent/{int(time.time())}_{filename}"
        oss_result = await upload_to_oss_wrapper(
            b64_data, oss_path, filename, with_download_headers=True
        )
        oss_url = list(oss_result.values())[0]
        return ReportUploadResult(
            oss_url=oss_url,
            oss_path=oss_path,
            filename=filename,
        )


async def extract_convert_and_upload(
    compressed_url: str, temp_dir_path: str = './tmp', session_id: str = ''
) -> dict:
    """
    下载 TGZ → 解压 → JPG 转 Base64 → 上传 OSS → 自动清理
    """
    async with temp_dir(temp_dir_path) as temp_path:
        # 获取所有JPG文件的Base64编码
        logger.info(f"{session_id} compressed_url = {compressed_url}")
        files = await extract_files_from_compressed_file_url(compressed_url, temp_path)
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


async def update_tgz_dict(tool_result: dict, session_id: str = ''):
    new_tool_result = {}
    compressed_flag = False
    for k, v in tool_result.items():
        new_tool_result[k] = v
        if isinstance(v, str) and v.startswith('https') and v.endswith(('tgz', 'zip')):
            compressed_flag = True
            new_tool_result.update(
                **await extract_convert_and_upload(v, session_id=session_id)
            )

    return compressed_flag, new_tool_result


async def extract_file_content(file_url: str, temp_dir_path: str = './tmp') -> dict:
    async with temp_dir(temp_dir_path) as tdir:
        file_name = await get_filename_from_url(file_url)
        temp_file_path = tdir / file_name

        async with aiohttp.ClientSession() as session:
            await _download_file(session, file_url, temp_file_path)

        content = await read_file_bytes(temp_file_path)
        return {'file_content': content}


if __name__ == '__main__':
    invalid_zip = 'https://bohrium-agent-test.oss-cn-zhangjiakou.aliyuncs.com/agent/jobs/337612/fc6c0cc25d8847c8acb226c097557ed7/outputs.zip'
    valid_zip = 'https://bohrium-agent-test.oss-cn-zhangjiakou.aliyuncs.com/agent/jobs/110680/c15113bb106b46f1a49800e776a2b8fc/outputs.zip'
    failed_zip = 'https://bohrium-agents.oss-cn-zhangjiakou.aliyuncs.com/agent/jobs/337612/263edcfa12a2460abd222f6deeb19969/outputs.zip'
    asyncio.run(extract_convert_and_upload(failed_zip, './tmp'))
