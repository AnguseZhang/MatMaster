import os

import requests
from toolsy.logger import init_colored_logger

from agents.matmaster_agent.constant import (
    BOHRIUM_HOST,
    MATERIALS_ACCESS_KEY,
    MATERIALS_PROJECT_ID,
    OPENAPI_HOST,
    OPENAPI_JOB_CREATE_API,
    OPENAPI_JOB_KILL_API,
    OPENAPI_JOB_LIST_API,
    OpenAPIJobAPI,
)

logger = init_colored_logger(__name__)


def get_token():
    url = f'{OPENAPI_HOST}/openapi/v1/storage/token'
    headers = {'x-app-key': 'agent'}
    params = {'projectId': MATERIALS_PROJECT_ID, 'accessKey': MATERIALS_ACCESS_KEY}
    response = requests.get(url, headers=headers, params=params)
    logger.info(response.json())


def get_ticket(authorization):
    headers = {'authorization': authorization}

    url = f'{BOHRIUM_HOST}/bohrapi/v1/ticket/get'
    response = requests.get(url, headers=headers)
    logger.info(response.json())

    return response.json()['data']['ticket']


def create_job():
    request_body_json = {'projectId': MATERIALS_PROJECT_ID, 'name': 'demo_job'}
    request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}

    response = requests.post(
        OPENAPI_JOB_CREATE_API, json=request_body_json, params=request_query_string
    )
    print(response)


def kill_job(job_id, use_ticket=False, authorization=None):
    url = f'{OPENAPI_JOB_KILL_API}/{job_id}'
    if use_ticket and authorization:
        ticket = get_ticket(authorization)
        headers = {'Brm-Ticket': ticket}
        response = requests.post(url, headers=headers)
    else:
        request_query_string = {'accessKey': MATERIALS_ACCESS_KEY}
        response = requests.post(url, params=request_query_string)

    logger.info(response.json())


def get_job_detail(job_id, use_ticket=False, authorization=None):
    if use_ticket and authorization:
        ticket = get_ticket(authorization)
        headers = {'Brm-Ticket': ticket}
        response = requests.get(f"{OpenAPIJobAPI}/{job_id}", headers=headers)
        logger.info(response.json())


def get_job_list(
    job_ids, use_ticket=False, authorization=None, realUserId=None, sessionId=None
):
    if use_ticket and authorization:
        ticket = get_ticket(authorization)
        headers = {'Brm-Ticket': ticket}
        query_params = {
            'jobIds': job_ids,
            'realUserId': realUserId,
            'sessionId': sessionId,
        }
        response = requests.get(
            OPENAPI_JOB_LIST_API, headers=headers, params=query_params
        )
        logger.info(response.json())


if __name__ == '__main__':
    authorization = os.getenv('BEARER_TOKEN')
    job_id = 'da2fc84fdf56443a9b600a3007a502b1'
    # use_ticket_get_job_list(['03b212ee76964c82bc58c1c2314fac79'], 110680, '19c1a7d4-2502-44fc-a58c-f29cce49986f')
    # kill_job(job_id, use_ticket=True, authorization=authorization)
    # get_job_detail(job_id, use_ticket=True, authorization=authorization)
    get_token()
