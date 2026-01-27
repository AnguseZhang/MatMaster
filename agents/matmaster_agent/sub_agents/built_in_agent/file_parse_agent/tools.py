import asyncio
import base64
import mimetypes
from typing import TypedDict

import aiohttp
from litellm import acompletion

from agents.matmaster_agent.llm_config import MatMasterLlmConfig
from agents.matmaster_agent.sub_agents.built_in_agent.file_parse_agent.prompt import (
    FileParseAgentInstruction,
)
from agents.matmaster_agent.utils.io_oss import get_filename_from_url


class FileParseResponse(TypedDict):
    msg: str


# Configuration Constants
TEXT_FILE_MAX_SIZE = 1 * 1024 * 1024  # 1MB for text files
IMAGE_FILE_MAX_SIZE = 20 * 1024 * 1024  # 20MB for images


async def _parse_image_content(content: bytes, mime_type: str) -> str:
    """Handles visual parsing using the configured Gemini model."""
    b64_data = base64.b64encode(content).decode('utf-8')
    data_uri = f"data:{mime_type};base64,{b64_data}"

    model_name = MatMasterLlmConfig.gemini_3_flash.model

    response = await acompletion(
        model=model_name,
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': FileParseAgentInstruction},
                    {'type': 'image_url', 'image_url': {'url': data_uri}},
                ],
            }
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


async def _parse_text_content(content: bytes) -> str:
    """
    Handles text parsing by decoding the bytes content.
    """
    try:
        # Attempt to decode the content as text
        text_content = content.decode('utf-8')
        return text_content
    except UnicodeDecodeError:
        # If UTF-8 fails, try other encodings
        try:
            text_content = content.decode('gbk')
            return text_content
        except UnicodeDecodeError:
            # If all decodings fail, return an error message
            return '无法解码文件内容：不支持的文本编码格式'


async def file_parse(file_url: str) -> FileParseResponse:
    """Orchestrator: Downloads file and dispatches to appropriate parser."""
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Download & Validate
            async with session.get(
                file_url, timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                # Determine the file type first to apply appropriate size limit
                filename = await get_filename_from_url(file_url)
                mime_type, _ = mimetypes.guess_type(filename)

                max_size = (
                    IMAGE_FILE_MAX_SIZE
                    if mime_type and mime_type.startswith('image/')
                    else TEXT_FILE_MAX_SIZE
                )

                if resp.content_length and resp.content_length > max_size:
                    return FileParseResponse(
                        msg=f'文件超出大小限制（>{max_size} 字节）'
                    )

                content = await resp.read()
                if len(content) > max_size:
                    return FileParseResponse(
                        msg=f'文件超出大小限制（>{max_size} 字节）'
                    )

            # 2. Type Detection
            # mime_type, _ = mimetypes.guess_type(filename)

            # 3. Dispatch
            if mime_type and mime_type.startswith('image/'):
                result = await _parse_image_content(content, mime_type)
            else:
                # Parse text content directly from the bytes we already have
                result = await _parse_text_content(content)

            return FileParseResponse(msg=str(result))

        except asyncio.TimeoutError:
            return FileParseResponse(msg='请求超时，请检查网络或文件地址')
        except Exception as e:
            # 捕获 litellm 异常或其他网络异常
            return FileParseResponse(msg=f'解析错误: {str(e)}')


if __name__ == '__main__':
    # text file
    asyncio.run(
        file_parse(
            'https://dp-storage-test2.oss-cn-zhangjiakou.aliyuncs.com/bohrium-test/bohrium/feedback/attachment/01KBM1X4KGDHTE2ZR44G7EHC0Z/dsc-example.txt'
        )
    )

    # image file
    asyncio.run(
        file_parse(
            'https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/bohrium/feedback/attachment/01KF8EZX821J2MVRGPZ9PG4JY8/screenshot-20260118-194811.png'
        )
    )
