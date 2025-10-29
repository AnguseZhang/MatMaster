"""
Ops ENV: MATERIALS_ACCESS_KEY, MATERIALS_PROJECT_ID, MATMASTER_SKU_ID, DEFAULT_MODEL
DEBUG ENV: OPIK_PROJECT_NAME, BOHRIUM_ACCESS_KEY, BOHRIUM_PROJECT_ID, BOHRIUM_USER_ID
Other ENV: MATERIALS_USER_ID, MATERIALS_ORG_ID, SESSION_API_URL
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Constant-VAR
MATMASTER_AGENT_NAME = 'matmaster_agent'

ModelRole = 'model'

Transfer2Agent = 'transfer_to_agent'

FRONTEND_STATE_KEY = 'frontend_state'
TMP_FRONTEND_STATE_KEY = 'tmp_frontend_state'

LOADING_STATE_KEY = 'loading_state'
LOADING_START = 'loading_start'
LOADING_END = 'loading_end'
LOADING_DESC = 'loading_desc'
LOADING_TITLE = 'loading_title'

JOB_RESULT_KEY = 'job_result'
JOB_LIST_KEY = 'job_list'

# DB
DBUrl = os.getenv('SESSION_API_URL')

# HOST URL
DFLOW_HOST = ''
DFLOW_K8S_API_SERVER = ''
MATMASTER_SKU_ID = -1

CURRENT_ENV = os.getenv('OPIK_PROJECT_NAME', 'prod')
URL_PART = f'.{CURRENT_ENV}' if CURRENT_ENV != 'prod' else ''
OPENAPI_HOST = f'https://openapi{URL_PART}.dp.tech'
BOHRIUM_API_URL = f'https://bohrium-api{URL_PART}.dp.tech'
GOODS_API_BASE = f'https://goods-server{URL_PART}.dp.tech'
FINANCE_API_BASE = f'https://finance-web{URL_PART}.dp.tech'
BOHRIUM_COM = f'https://www{URL_PART}.bohrium.com'
BOHRIUM_HOST = f'https://bohrium{URL_PART}.dp.tech'
if CURRENT_ENV == 'test':
    DFLOW_HOST = 'https://lbg-workflow-mlops.test.dp.tech'
    DFLOW_K8S_API_SERVER = 'https://lbg-workflow-mlops.test.dp.tech'
elif CURRENT_ENV == 'uat':
    pass
elif CURRENT_ENV == 'prod':
    DFLOW_HOST = 'https://workflows.deepmodeling.com'
    DFLOW_K8S_API_SERVER = 'https://workflows.deepmodeling.com'

# API URL
OPENAPI_SANDBOX = f'{OPENAPI_HOST}/openapi/v1/sandbox'
OPENAPI_JOB_KILL_API = f'{OPENAPI_SANDBOX}/kill'
OpenAPIJobAPI = f"{OPENAPI_SANDBOX}/job"
OPENAPI_JOB_CREATE_API = f'{OpenAPIJobAPI}/create'
OPENAPI_FILE_TOKEN_API = f'{OpenAPIJobAPI}/file/token'
OPENAPI_JOB_LIST_API = f'{OpenAPIJobAPI}/list'

BOHRIUM_TICKET_API = f'{BOHRIUM_HOST}/bohrapi/v1/ticket/get'

GOODS_SKU_LIST_API = f"{GOODS_API_BASE}/api/v1/sku/list"
FINANCE_WALLET_INFO_API = f"{FINANCE_API_BASE}/api/wallet/detail"
FINANCE_INFO_API = f"{FINANCE_API_BASE}/api/integral/info"
FINANCE_CONSUME_API = f"{FINANCE_API_BASE}/api/integral/consume"

SANDBOX_JOB_DETAIL_URL = f'{BOHRIUM_COM}/sandboxjob/detail'

# Constant-Materials
MATERIALS_USER_ID = int(os.getenv('MATERIALS_USER_ID', -1))
MATERIALS_ORG_ID = int(os.getenv('MATERIALS_ORG_ID', -1))
MATERIALS_ACCESS_KEY = str(os.getenv('MATERIALS_ACCESS_KEY'))
MATERIALS_PROJECT_ID = int(os.getenv('MATERIALS_PROJECT_ID'))
MATMASTER_SKU_ID = int(os.getenv('MATMASTER_SKU_ID', -1))

# Constant-SKU
SKU_MAPPING = {'matmaster': MATMASTER_SKU_ID}

# Constant-Storage
BohriumStorge = {
    'type': 'https',
    'plugin': {
        'type': 'bohrium',
        'access_key': MATERIALS_ACCESS_KEY,
        'project_id': MATERIALS_PROJECT_ID,
        'app_key': 'agent',
    },
}

# Constant-Executor
LOCAL_EXECUTOR = {'type': 'local'}
BohriumExecutor = {
    'type': 'dispatcher',
    'machine': {
        'batch_type': 'OpenAPI',
        'context_type': 'OpenAPI',
        'remote_profile': {
            'access_key': MATERIALS_ACCESS_KEY,
            'project_id': MATERIALS_PROJECT_ID,
            'app_key': 'agent',
            'image_address': '',
            'platform': 'ali',
            'machine_type': 'c2_m8_cpu',
            'real_user_id': -1,
            'session_id': '',
        },
    },
    'resources': {'envs': {'BOHRIUM_PROJECT_ID': MATERIALS_PROJECT_ID}},
}
DFlowExecutor = {
    'type': 'local',
    'dflow': True,
    'env': {
        'DFLOW_HOST': DFLOW_HOST,
        'DFLOW_K8S_API_SERVER': DFLOW_K8S_API_SERVER,
        'DFLOW_S3_REPO_KEY': 'oss-bohrium',
        'DFLOW_S3_STORAGE_CLIENT': 'dflow.plugins.bohrium.TiefblueClient',
        'BOHRIUM_ACCESS_KEY': MATERIALS_ACCESS_KEY,
        'BOHRIUM_PROJECT_ID': str(MATERIALS_PROJECT_ID),
        'BOHRIUM_APP_KEY': 'agent',
    },
}


def get_BohriumExecutor():
    return BohriumExecutor


def get_DFlowExecutor():
    return DFlowExecutor


def get_BohriumStorage():
    return BohriumStorge
