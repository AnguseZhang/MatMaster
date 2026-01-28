import logging
import os
from datetime import datetime
from pathlib import Path

from google.adk.tools.tool_context import ToolContext
from mcp import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s (%(filename)s:%(lineno)d) [%(levelname)s] %(message)s'
    )
)
logger.addHandler(handler)


async def matmodeler_logging_handler(
    params: types.LoggingMessageNotificationParams,
    tool_context: ToolContext | None = None,
):
    session_id = None
    function_call_id = None
    tool_name = None
    if tool_context is not None:
        try:
            session_id = tool_context.session.id
        except Exception:
            session_id = None
        try:
            function_call_id = tool_context.function_call_id
        except Exception:
            function_call_id = None
        try:
            tool = getattr(tool_context, 'tool', None)
            if tool is not None:
                tool_name = getattr(tool, 'name', None)
        except Exception:
            tool_name = None

    prefix = (
        f"[mcp_log session={session_id} tool={tool_name} "
        f"call_id={function_call_id}] "
    )
    logger.log(getattr(logging, params.level.upper()), prefix + str(params.data))


class PrefixFilter(logging.Filter):
    def __init__(self, prefix):
        self.prefix = prefix

    def filter(self, record):
        record.msg = f"[{self.prefix}] {record.msg}"
        return True


def setup_global_logger():
    root_logger = logging.getLogger()

    # 创建文件处理器
    LOG_DIR = Path('../logs')
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    if Path(LOG_DIR / log_filename).exists():
        os.remove(Path(LOG_DIR / log_filename))
    file_handler = logging.FileHandler(LOG_DIR / log_filename)  # 文件名可以自定义
    file_handler.setLevel(logging.INFO)

    # 创建格式化器并设置给处理器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # 将文件处理器添加到 logger
    root_logger.addHandler(file_handler)

    return root_logger
