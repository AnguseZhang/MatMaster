import asyncio
import time

from mcp import ClientSession
from mcp.client.sse import sse_client


async def get_tools(type='mcphub'):
    if type == 'mcphub':
        url = 'https://thermoelectricmcp000-uuid1750905361.app-space.dplink.cc/sse?token=096592e0f567437cbf35ffeb6d33a2a6'
    elif type == 'func':
        # url = 'https://cystalformer-uuid1754551471.app-space.dplink.cc/sse?token=1750cd294e6c4270946ae37107a725ff'
        url = 'https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=7c2e8de61ec94f4e80ebcef1ac17c92e'
    else:
        url = 'http://pfmx1355864.bohrium.tech:50003/sse'
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 调用 tools/list 方法（对应 get_tools）
            await session.list_tools()


def color_text(text, color_code):
    """返回带颜色的文本"""
    return f"\033[{color_code}m{text}\033[0m"


def format_time(duration):
    """格式化时间，如果超过1秒则显示为红色"""
    if duration > 1.0:
        return color_text(f"{duration:.3f}", '91')  # 91 是亮红色
    else:
        return f"{duration:.3f}"


if __name__ == '__main__':
    for i in range(20):
        start1 = time.time()
        asyncio.run(get_tools(type='node'))
        start2 = time.time()
        asyncio.run(get_tools(type='mcphub'))
        start3 = time.time()
        asyncio.run(get_tools(type='func'))
        start4 = time.time()

        node_time = start2 - start1
        mcphub_time = start3 - start2
        func_time = start4 - start3

        print(
            f'第 {i + 1} 轮测试：【Node】{format_time(node_time)};【MCPHub】{format_time(mcphub_time)}；【Func】{format_time(func_time)}'
        )
