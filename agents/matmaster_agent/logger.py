import logging

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
    params: types.LoggingMessageNotificationParams, tool_context: ToolContext
):
    logger.log(getattr(logging, params.level.upper()), params.data)


class PrefixFilter(logging.Filter):
    def __init__(self, prefix):
        self.prefix = prefix

    def filter(self, record):
        record.msg = f"[{self.prefix}] {record.msg}"
        return True
