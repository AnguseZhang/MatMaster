import asyncio

from google.adk.tools._gemini_schema_util import _to_gemini_schema
from mcp import ClientSession
from mcp.client.sse import sse_client


async def get_tool_function_declaration(url: str, tool_name: str):
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 调用 tools/list 方法（对应 get_tools）
            result = await session.list_tools()
            target_tool = [tool for tool in result.tools if tool.name == tool_name][0]
            result = _to_gemini_schema(target_tool.inputSchema).to_json_dict()
            print(result)


if __name__ == '__main__':
    url = 'http://toyl1410396.bohrium.tech:50001/sse'
    asyncio.run(
        get_tool_function_declaration(url, tool_name='abacus_cal_work_function')
    )
