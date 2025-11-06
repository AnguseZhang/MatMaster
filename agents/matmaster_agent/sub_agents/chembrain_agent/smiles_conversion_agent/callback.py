import json

from google.adk.tools import ToolContext
from mcp.types import CallToolResult

from agents.matmaster_agent.logger import logger
from agents.matmaster_agent.sub_agents.chembrain_agent.smiles_conversion_agent.constant import (
    SMILESConversionToolCall,
)
from agents.matmaster_agent.sub_agents.chembrain_agent.utils import is_json


async def smiles_conversion_before_tool(tool, args, tool_context: ToolContext):
    tool_info = {'before': {'tool_name': tool.name, 'tool_args': args}}
    _update_tool_context(tool_context, tool_info)

    return


async def smiles_conversion_after_tool(
    tool, args, tool_context: ToolContext, tool_response: CallToolResult
):
    """处理SMILES转图像工具的后处理，将base64图像上传至OSS并生成Markdown格式"""
    tool_info = {
        'after': {
            'tool_name': tool.name,
            'tool_args': args,
            'tool_response': (
                tool_response.content[0].text
                if (tool_response and len(tool_response.content))
                else None
            ),
        }
    }

    # 检查是否有有效的图像数据
    if not (
        tool_response
        and tool_response.content
        and tool_response.content[0].text
        and is_json(tool_response.content[0].text)
        and json.loads(tool_response.content[0].text).get('output_path', None)
        is not None
    ):
        _update_tool_context(tool_context, tool_info)
        return None

    try:
        markdown_image = (
            f"![mol_png]({json.loads(tool_response.content[0].text)['output_path']})"
        )
        tool_info['after']['tool_response'] = markdown_image
        # 更新工具上下文
        _update_tool_context(tool_context, tool_info)
        return markdown_image
    except Exception as e:
        logger.error(f"Failed to process SMILES image: {str(e)}")
        _update_tool_context(tool_context, tool_info)
        return None


def _update_tool_context(tool_context, tool_info):
    """辅助函数：更新工具上下文状态"""
    if SMILESConversionToolCall not in tool_context.state:
        tool_context.state[SMILESConversionToolCall] = []

    tool_context.state[SMILESConversionToolCall].append(tool_info)
