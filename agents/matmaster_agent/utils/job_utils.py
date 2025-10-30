import json
import logging

import aiohttp

from agents.matmaster_agent.constant import (
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    MATMASTER_AGENT_NAME,
    OPENAPI_HOST,
    OpenAPIJobAPI,
)
from agents.matmaster_agent.model import BohrJobInfo, JobStatus

logger = logging.getLogger(__name__)


def mapping_status(status):
    return {
        -1: 'Failed',
        -2: 'Deleted',
        0: 'Pending',
        1: 'Running',
        2: 'Finished',
        3: 'Scheduling',
        4: 'Stopping',
        5: 'Stopped',
        6: 'Terminating',
        7: 'Killing',
        8: 'Uploading',
        9: 'Wait',
    }.get(status, 'Unknown')


async def get_job_status(job_id, access_key):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{OpenAPIJobAPI}/{job_id}', headers={'accessKey': access_key}
        ) as response:
            logger.info(f'[{MATMASTER_AGENT_NAME}] response = {response.text()}')
            data = await response.json()
            return mapping_status(data['data']['status'])


def has_job_running(jobs_dict: BohrJobInfo) -> bool:
    """检查是否有任何作业处于运行状态"""
    return any(job['job_status'] == JobStatus.Running for job in jobs_dict.values())


def get_running_jobs_detail(jobs_dict: BohrJobInfo):
    return [
        (job['origin_job_id'], job['job_id'], job['agent_name'])
        for job in jobs_dict.values()
        if job['job_status'] == JobStatus.Running
    ]


async def get_project_name():
    user_project_list_url = f"{OPENAPI_HOST}/openapi/v1/open/user/project/list"
    params = {'accessKey': MATERIALS_ACCESS_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(user_project_list_url, params=params) as response:
            res = json.loads(await response.text())
            logger.info(f"[{MATMASTER_AGENT_NAME}] res = {res}")
            project_name = [
                item['project_name']
                for item in res['data']['items']
                if item['project_id'] == MATERIALS_PROJECT_ID
            ][0]

    return project_name


async def check_job_create_service():
    job_create_url = f"{OPENAPI_HOST}/openapi/v1/sandbox/job/create"
    payload = {
        'projectId': MATERIALS_PROJECT_ID,
        'name': 'check_job_create',
    }
    params = {'accessKey': MATERIALS_ACCESS_KEY}
    logger.info(
        f"[{MATMASTER_AGENT_NAME}] project_id = {MATERIALS_PROJECT_ID}, "
        f"ak = {MATERIALS_ACCESS_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            job_create_url, json=payload, params=params
        ) as response:
            res = json.loads(await response.text())
            print(job_create_url, payload, params)
            if res['code'] != 0:
                if res['code'] == 140202:
                    res['error'][
                        'msg'
                    ] = 'Agent 开发者账户余额不足，需开发者充值，请稍后重试。'
                print(res)
                return res
