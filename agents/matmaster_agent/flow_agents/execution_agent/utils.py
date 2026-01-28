from google.adk.agents import InvocationContext

from agents.matmaster_agent.state import ERROR_DETAIL, ERROR_OCCURRED


def should_exit_retryLoop(ctx: InvocationContext) -> bool:
    ANY_ERROR = ctx.session.state[ERROR_OCCURRED]

    # 下载 results.txt 失败，退出同一工具重试
    DOWNLOAD_RESULTS_TXT_FAILED = (
        ANY_ERROR
        and ctx.session.state[ERROR_DETAIL].startswith('ClientResponseError')
        and 'results.txt' in ctx.session.state[ERROR_DETAIL]
    )

    # HTTP 412 ERROR
    HTTP_412_ERROR = (
        ANY_ERROR
        and ctx.session.state[ERROR_DETAIL].startswith('HTTPStatusError')
        and '412 Precondition Failed' in ctx.session.state[ERROR_DETAIL]
    )

    # AccessKey Error
    AccessKey_ERROR = (
        ANY_ERROR and 'AccessKey Invalid!' in ctx.session.state[ERROR_DETAIL]
    )

    return DOWNLOAD_RESULTS_TXT_FAILED or HTTP_412_ERROR or AccessKey_ERROR
