import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import jsonpickle
import requests
from dotenv import find_dotenv, load_dotenv
from toolsy.logger import init_colored_logger

from agents.matmaster_agent.constant import OPENAPI_FILE_TOKEN_API, OpenAPIJobAPI
from agents.matmaster_agent.utils.job_utils import mapping_status
from scripts.sandbox_api import kill_job

load_dotenv(find_dotenv())

logger = init_colored_logger(__name__)


def get_duration(create_time, update_time):
    """
    计算两个时间戳之间的时间差，格式化为时-分-秒

    Args:
        create_time (str): 创建时间，ISO 8601格式
        update_time (str): 更新时间，ISO 8601格式

    Returns:
        str: 时间差，格式为"时-分-秒"
    """
    # 解析时间字符串为datetime对象
    create_dt = datetime.fromisoformat(create_time)
    update_dt = datetime.fromisoformat(update_time)

    # 计算时间差
    time_diff = update_dt - create_dt

    # 提取总秒数
    total_seconds = int(time_diff.total_seconds())

    # 计算小时、分钟、秒
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # 格式化为时-分-秒
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def check_status_and_download_file(response, file_download_path):
    def download_file(response, output_path):
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(
                            f"\rDownload progress: {progress:.1f}%", end='', flush=True
                        )

        print()

    status_code = response.status_code
    if status_code == 400:
        logger.error(f'`{file_download_path}` url returned 400 Bad Request')
    elif status_code == 200:
        download_file(response, file_download_path)
        if Path(file_download_path).exists():
            file_size = os.path.getsize(file_download_path)
            logger.info(
                f"Download `{file_download_path}` completed successfully! File size: {file_size} bytes"
            )
        else:
            logger.error(
                f"Error: Download `{file_download_path}` failed - file doesn't exist"
            )
    else:
        logger.error(f'`{file_download_path}` url returned status code: {status_code}')


def get_token_and_download_file(file_path, job_id):
    # 获取log文件的token
    request_body = {'filePath': file_path, 'jobId': job_id}
    response = requests.post(
        f"{OPENAPI_FILE_TOKEN_API}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}",
        json=request_body,
    )
    response.raise_for_status()
    response_data_json: dict = response.json().get('data', {})

    response_file_token = response_data_json.get('token', '')
    response_file_path = response_data_json.get('path', '')
    response_file_host = response_data_json.get('host', '')

    # 构建log文件URL并检查状态
    if response_file_host and response_file_path and response_file_token:
        file_url = f"{response_file_host}/api/download/{response_file_path}?token={response_file_token}"
        file_response = requests.get(file_url, timeout=10)
        check_status_and_download_file(file_response, file_path)
    else:
        logger.error(f'Incomplete {file_path} information - cannot construct file URL')


def poll_job_status(job_id, interval=10):
    """轮询作业状态并在每次轮询时下载最新的日志"""
    logger.info(f"开始轮询作业 {job_id} 的状态 (间隔: {interval} 秒)")

    while True:
        try:
            response = requests.get(
                f"{OpenAPIJobAPI}/{job_id}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}"
            )
            response.raise_for_status()
            job_info = response.json()

            if job_info.get('code') != 0:
                logger.error(f"API返回错误: {job_info}")
                break

            create_time = job_info['data']['createTime']
            update_time = job_info['data']['updateTime']
            duration = get_duration(create_time, update_time)
            job_status = mapping_status(job_info['data']['status'])
            job_name = job_info['data']['jobName']
            logger.info(f"{job_name}[{job_status}] -- {duration}")

            # 下载日志
            get_token_and_download_file('log', job_id)

            # 如果作业已结束，则退出轮询
            if job_status in ['Finished', 'Failed', 'Killed']:
                logger.info(f"作业状态为 {job_status}，停止轮询")
                break

            # 等待下次轮询
            time.sleep(interval)

        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info('用户中断轮询')
            break
        except Exception as e:
            logger.error(f"轮询过程中发生错误: {e}")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description='Sandbox job cli')
    subparsers = parser.add_subparsers(
        dest='command', help='Available commands', required=True
    )

    # detail 子命令
    detail_parser = subparsers.add_parser(
        'detail', help='Get job details and download results'
    )
    detail_parser.add_argument('job_id', help='Job ID to fetch results for')
    detail_parser.add_argument(
        '-o',
        '--output',
        default='output.zip',
        help='Output file path (default: output.zip)',
    )
    detail_parser.add_argument('-d', '--download_output', action='store_true')
    detail_parser.add_argument('--debug', action='store_true')

    # kill 子命令
    kill_parser = subparsers.add_parser('kill', help='Kill a job')
    kill_parser.add_argument('job_id', help='Job ID to kill')

    # poll 子命令
    poll_parser = subparsers.add_parser(
        'poll', help='Poll job status and update logs periodically'
    )
    poll_parser.add_argument('job_id', help='Job ID to poll')
    poll_parser.add_argument(
        '-i',
        '--interval',
        type=int,
        default=10,
        help='Polling interval in seconds (default: 10)',
    )

    args = parser.parse_args()

    # 调用API获取job信息
    logger.info(f"Job ID: {args.job_id}")

    # 根据子命令执行不同的逻辑
    if args.command == 'detail':
        # 删除已存在的输出文件
        if os.path.exists(args.output):
            os.remove(args.output)

        try:
            response = requests.get(
                f"{OpenAPIJobAPI}/{args.job_id}?accessKey={os.getenv('MATERIALS_ACCESS_KEY')}"
            )
            response.raise_for_status()
            job_info = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error: Failed to fetch data from API: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error: Failed to parse JSON response: {e}")
            sys.exit(1)

        if args.debug:
            logger.setLevel('DEBUG')
            logger.debug(f"\n{json.dumps(job_info, indent=2, ensure_ascii=False)}")
            logger.setLevel('INFO')

        # 解析JSON获取resultUrl
        if job_info.get('code') == 0:
            result_url = job_info.get('data', {}).get('resultUrl', '')
        else:
            logger.error(f"API returned error，{job_info}")
            sys.exit(-1)

        create_time = job_info['data']['createTime']
        update_time = job_info['data']['updateTime']
        duration = get_duration(create_time, update_time)
        job_status = mapping_status(job_info['data']['status'])
        job_name = job_info['data']['jobName']
        logger.info(f"{job_name}[{job_status}] -- {duration}")

        # download log
        get_token_and_download_file('log', args.job_id)

        if job_status in ['Running']:
            return
        elif job_status == 'Finished':
            # download result.txt
            results_txt = 'results.txt'
            get_token_and_download_file(results_txt, args.job_id)
            with open(results_txt) as f:
                logger.info(jsonpickle.loads(f.read()))
            os.remove(results_txt)

            if args.download_output:
                # 下载结果文件
                if result_url and result_url != 'null':
                    result_response = requests.get(result_url, stream=False)
                    check_status_and_download_file(result_response, args.output)
                else:
                    logger.error('No resultUrl found or resultUrl is empty')
    elif args.command == 'kill':
        kill_job(args.job_id)
    elif args.command == 'poll':
        poll_job_status(args.job_id, args.interval)


if __name__ == '__main__':
    main()
