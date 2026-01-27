import asyncio
import json
import logging
import os
from pathlib import Path

import aiohttp
import jsonpickle

from agents.matmaster_agent.constant import (
    MATMASTER_AGENT_NAME,
    OPENAPI_FILE_TOKEN_API,
    OPENAPI_HOST,
    TIEFBLUE_NAS_HOST,
    OpenAPIJobAPI,
)
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.utils.io_oss import file_to_base64, upload_to_oss_wrapper

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


async def check_job_create_service(access_key, project_id):
    job_create_url = f"{OPENAPI_HOST}/openapi/v1/sandbox/job/create"
    payload = {
        'projectId': project_id,
        'name': 'check_job_create',
    }
    params = {'accessKey': access_key}
    logger.info(f"project_id = {project_id}, ak = {access_key}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            job_create_url, json=payload, params=params
        ) as response:
            res = json.loads(await response.text())
            if res['code'] != 0:
                if res['code'] == 140202:
                    res['error'][
                        'msg'
                    ] = '钱包余额不足，请在[此页面](https://www.bohrium.com/consume?menu=cash)充值后重试。'

                return res


async def get_job_detail(job_id, access_key):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{OpenAPIJobAPI}/{job_id}', headers={'accessKey': access_key}
        ) as response:
            res_text = await response.text()
            logger.info(
                f'job_id = {job_id}, access_key = {access_key}, response = {res_text}'
            )
            res = json.loads(res_text)

            return res


async def check_status_and_download_file(
    response: aiohttp.ClientResponse, file_download_path: str
):
    async def download_file(resp: aiohttp.ClientResponse, output_path: str):
        # --- 新增：确保父目录存在 ---
        dest_path = Path(output_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        # parents=True 表示递归创建所有不存在的父目录
        # exist_ok=True 表示如果目录已存在则不报错
        # ------------------------

        total_size = int(resp.headers.get('content-length', 0))
        downloaded_size = 0

        # aiohttp 读取 body 用 resp.content.iter_chunked
        with open(output_path, 'wb') as f:
            async for chunk in resp.content.iter_chunked(8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(
                            f"\rDownload progress: {progress:.1f}%", end='', flush=True
                        )
        print()

    status_code = response.status

    if status_code == 400:
        logger.error(f'`{file_download_path}` url returned 400 Bad Request')
        return

    if status_code == 200:
        await download_file(response, file_download_path)
        if Path(file_download_path).exists():
            file_size = os.path.getsize(file_download_path)
            logger.info(
                f"Download `{file_download_path}` completed successfully! File size: {file_size} bytes"
            )
        else:
            logger.error(
                f"Error: Download `{file_download_path}` failed - file doesn't exist"
            )
        return

    logger.error(f'`{file_download_path}` url returned status code: {status_code}')


async def get_token(file_path, job_id, access_key):
    request_body = {'filePath': file_path, 'jobId': job_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OPENAPI_FILE_TOKEN_API}?accessKey={access_key}",
            json=request_body,
        ) as response:
            response.raise_for_status()
            payload = await response.json()

            response_data_json = payload.get('data', {})
            response_file_token = response_data_json.get('token', '')
            response_file_path = response_data_json.get('path', '')
            response_file_host = response_data_json.get('host', '')

    return response_file_host, response_file_path, response_file_token


async def get_token_and_download_file(file_path, job_id, access_key):
    response_file_host, response_file_path, response_file_token = await get_token(
        file_path, job_id, access_key
    )

    # 构建log文件URL并检查状态
    if response_file_host and response_file_path and response_file_token:
        file_url = f"{response_file_host}/api/download/{response_file_path}?token={response_file_token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as file_response:
                file_response.raise_for_status()
                await check_status_and_download_file(
                    file_response, file_path
                )  # 需要你把该函数签名改一下
    else:
        logger.error(f"Incomplete {file_path} information - cannot construct file URL")


async def get_token_and_download_dir(dir_path, job_id, access_key):
    host, path, token = await get_token('', job_id, access_key)
    prefix = path.replace('results.txt', '')
    request_body = {
        'targetDir': dir_path,
        'tempDir': prefix,
        'maxCompressSize': 1073741824,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{TIEFBLUE_NAS_HOST}/api/downloadr',
            json=request_body,
            headers={
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json',
            },
        ) as response:
            blob = await response.read()
            with open(f"{dir_path.split("/")[-2]}.zip", 'wb') as f:
                f.write(blob)


async def get_iterate_files(
    job_id: str, prefix: str | None = None, access_key: str = ''
):
    """
    兼容版：支持列根目录，也支持列任意子目录 prefix。
    - 若 prefix=None：沿用你原来的逻辑，从 get_token("", job_id) 里拿 results.txt 的 path 推出根 prefix
    - 若 prefix!=None：直接用传入 prefix 去 iterate
    """
    host, path, token = await get_token('', job_id, access_key)

    if prefix is None:
        # path 形如 jobs/xxx/xxx/results.txt
        prefix = path.replace('results.txt', '')
    prefix = prefix.replace('\\', '/')
    if not prefix.endswith('/'):
        prefix += '/'

    request_body = {'prefix': prefix}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{host}/api/iterate",
            json=request_body,
            headers={
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json',
            },
        ) as response:
            iterate_json = await response.json()

    return prefix, iterate_json


async def parse_and_prepare_results(
    job_id: str = '', access_key: str = '', session_id: str = ''
):
    def norm(p: str) -> str:
        p = p.replace('\\', '/')
        if p.endswith('/') and p != '/':
            p = p[:-1]
        return p

    async def list_dir(dir_prefix: str):
        """
        dir_prefix: jobs/xxx/xxx/ 或 jobs/xxx/xxx/trajs_files/
        """
        dp = dir_prefix.replace('\\', '/')
        if not dp.endswith('/'):
            dp += '/'

        if dp in listing_cache:
            return listing_cache[dp]

        _prefix, iterate_json = await get_iterate_files(
            job_id, prefix=dp, access_key=access_key
        )
        objects = iterate_json.get('data', {}).get('objects', [])
        idx = {norm(o['path']): o for o in objects}

        listing_cache[dp] = {'prefix': _prefix, 'objects': objects, 'idx': idx}

        return listing_cache[dp]

    def remote_candidates(rel: str):
        rel = norm(rel)
        remote_file = norm(job_root_prefix + rel)
        remote_dir = norm(job_root_prefix + rel + '/')
        return remote_file, remote_dir

    async def find_obj(rel: str):
        """
        优先根目录 listing，找不到则去父目录 listing（例如 trajs_files/）再找。
        """
        rf, rd = remote_candidates(rel)

        # 1) 根目录
        root_listing = await list_dir(job_root_prefix)
        obj = root_listing['idx'].get(rf) or root_listing['idx'].get(rd)
        if obj:
            return obj

        # 2) 父目录（比如 trajs_files/）
        parent = Path(rel).parent.as_posix()  # '.' or 'trajs_files' or 'a/b'
        if parent == '.':
            return None

        parent_prefix = job_root_prefix + parent.strip('/') + '/'
        parent_listing = await list_dir(parent_prefix)
        obj = parent_listing['idx'].get(rf) or parent_listing['idx'].get(rd)
        return obj

    async def safe_cleanup_file(file_download_path: Path):
        """
        删除文件，并由内向外清理空的父目录，直到当前工作目录为止。
        """
        file_path = file_download_path.resolve()
        root_dir = Path.cwd().resolve()  # 获取当前工作目录的绝对路径

        # 1. 删除文件本身
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除文件: {file_path}")
        except Exception as e:
            logger.error(f"无法删除文件 {file_path}: {e}")
            return

        # 2. 逐级向上清理空目录
        # target_dir 从文件所在的直接父目录开始
        target_dir = file_path.parent

        # 循环条件：目标目录属于当前目录的子目录，且不是当前目录本身
        while target_dir.is_relative_to(root_dir) and target_dir != root_dir:
            try:
                # rmdir 仅在目录为空时才会成功
                target_dir.rmdir()
                logger.info(f"清理空目录: {target_dir}")
                # 移动到上一层
                target_dir = target_dir.parent
            except OSError:
                # 如果目录非空（比如里面还有其他 band.png）或权限不足，停止向上清理
                logger.info(f"停止清理：目录 {target_dir} 非空或无权限")
                break

    # Download results.txt & Prepare Parse
    RESULTS_TXT = 'results.txt'
    await get_token_and_download_file(RESULTS_TXT, job_id, access_key)

    with open(RESULTS_TXT) as f:
        results_txt_parsed = jsonpickle.loads(
            f.read().replace('pathlib._local.PosixPath', 'pathlib.PosixPath')
        )
        logger.info(f"{session_id} results_txt_parsed = {results_txt_parsed}")
    os.remove(RESULTS_TXT)

    final_results = {}

    # 缓存：dir_prefix -> {"idx":..., "objects":...}
    listing_cache: dict[str, dict] = {}

    # 先拿 job 根 prefix（jobs/xxx/xxx/）
    job_root_prefix, _ = await get_iterate_files(job_id, access_key=access_key)
    job_root_prefix = job_root_prefix.replace('\\', '/')
    if not job_root_prefix.endswith('/'):
        job_root_prefix += '/'

    for k, v in results_txt_parsed.items():
        # 非文件型
        if not isinstance(v, Path):
            final_results[k] = v
            continue

        rel = str(v).replace('\\', '/')
        obj = await find_obj(rel)

        if obj is None:
            logger.warning(f"{session_id} `{rel}` is not exist")
            continue

        is_dir = bool(obj.get('isDir'))
        if not is_dir:
            await get_token_and_download_file(rel, job_id, access_key)
            filename = Path(rel)
        else:
            await get_token_and_download_dir(obj['path'], job_id, access_key)
            filename = Path(f"{obj['path'].split("/")[-2]}.zip")

        # 上传文件到 OSS
        file_path, b64_data = await file_to_base64(filename)
        oss_path = f"agent/{job_root_prefix}{file_path.name}"
        oss_url = await upload_to_oss_wrapper(b64_data, oss_path, file_path.name)
        final_results[k] = list(oss_url.values())[0]

        # 删除文件
        await safe_cleanup_file(filename)

    return final_results


if __name__ == '__main__':
    asyncio.run(
        parse_and_prepare_results(
            job_id='2bdc71b918aa46d3ada0ae5d40d3d43b',
            access_key=os.getenv('BOHRIUM_ACCESS_KEY'),
        )
    )
