import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from google.adk.tools.tool_context import ToolContext
from mcp import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 修复 Windows 终端编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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


def setup_global_logger():
    # 创建 log 文件夹
    log_dir = Path("log")
    log_dir.mkdir(exist_ok=True)
    
    # 创建带时间戳的日志文件
    log_file = log_dir / f"adk_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 文件 Handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s (%(filename)s:%(lineno)d) [%(levelname)s] %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # 控制台 Handler (保持原来 StreamHandler 的配置)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s (%(filename)s:%(lineno)d) [%(levelname)s] %(message)s'
    ))

    root_logger = logging.getLogger()
    # 移除所有现有的 handler，避免重复添加
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 确保 Uvicorn 的日志也能写入文件
    # Uvicorn 默认有自己的 logger，且 propagate=False
    for log_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(log_name)
        # 避免重复添加 FileHandler
        if not any(isinstance(h, logging.FileHandler) for h in uvicorn_logger.handlers):
            uvicorn_logger.addHandler(file_handler)

    # 创建文件处理器
    LOG_DIR = Path('../logs')
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    # 并发场景下跳过删除，避免 PermissionError
    try:
        if Path(LOG_DIR / log_filename).exists():
            os.remove(Path(LOG_DIR / log_filename))
    except (PermissionError, OSError):
        pass  # 文件被其他进程占用，跳过删除
    # 指定 UTF-8 编码，避免写入文件时出错
    file_handler = logging.FileHandler(
        LOG_DIR / log_filename, 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    # 创建格式化器并设置给处理器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # 将文件处理器添加到 logger
    root_logger.addHandler(file_handler)
    
    # 添加控制台处理器，使用 UTF-8 编码
    import io
    console_handler = logging.StreamHandler(
        io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    )
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger
