import csv
import io
import logging
from typing import List, Union

import aiohttp
from pydantic import BaseModel

from agents.matmaster_agent.constant import JOB_RESULT_KEY, MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.model import (
    JobResult,
    JobResultType,
    LiteratureItem,
    Matrix,
    RenderTypeEnum,
    WebSearchItem,
)
from agents.matmaster_agent.services.session_files import insert_session_files

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)


def flatten_dict(d, parent_key='', sep='_'):
    """
    将多层嵌套的字典拉平为一级字典

    参数:
        d: 要拉平的字典
        parent_key: 父级键名(递归时使用)
        sep: 嵌套键之间的分隔符

    返回:
        拉平后的一级字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 处理列表中的字典项
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(
                        flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    )
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


async def is_matmodeler_file(filename: str) -> bool:
    return (
        filename.endswith(
            (
                '.cif',
                '.poscar',
                '.contcar',
                '.vasp',
                '.xyz',
                '.mol',
                '.mol2',
                '.sdf',
                '.dump',
                '.lammpstrj',
            )
        )
        or filename.startswith('lammpstrj')
        or 'POSCAR' in filename
        or 'CONTCAR' in filename
        or filename == 'STRU'
    )


async def is_echarts_file(filename: str) -> bool:
    return filename.endswith('.echarts')


async def is_image_file(filename: str) -> bool:
    return filename.endswith(('.png', '.jpg', '.jpeg', '.svg'))


def is_sequence(data):
    return isinstance(data, (tuple, list))


async def is_float_sequence(data) -> bool:
    return is_sequence(data) and all(isinstance(x, float) for x in data)


async def is_str_sequence(data) -> bool:
    return is_sequence(data) and all(isinstance(x, str) for x in data)


async def is_literature_sequence(data) -> bool:
    return is_sequence(data) and validate_model_list(data, LiteratureItem)


async def is_web_search_sequence(data) -> bool:
    return is_sequence(data) and validate_model_list(data, WebSearchItem)


def is_matrix(data):
    return is_sequence(data) and all(is_sequence(row) for row in data)


async def is_float_matrix(data) -> bool:
    return is_matrix(data) and all(isinstance(x, float) for row in data for x in row)


def validate_model_list(data: list, model: type[BaseModel]) -> bool:
    for item in data:
        try:
            model.model_validate(item)
        except BaseException as e:
            logger.warning(e)
            return False
    return True


async def parse_result(
    ctx, result: dict
) -> List[Union[dict, WebSearchItem, JobResult]]:
    """
    Parse and flatten a nested dictionary result into a list of standardized JobResult objects.

    Processes a dictionary (potentially nested) and converts it into serialized JobResult objects.
    Handles various data types including numbers, strings, sequences, and file URLs.
    For image URLs, automatically generates both file reference and markdown representation.

    Args:
        result (dict): Input dictionary to parse. May contain:
                      - Nested dictionaries (automatically flattened)
                      - Primitive values (int, float, str)
                      - Sequences (of numbers or strings)
                      - URLs (regular files or MatModeler files)

    Returns:
        list: Serialized JobResult objects with appropriate types:
              - Value: For primitive types and sequences
              - MatModelerFile/RegularFile: For recognized file URLs
              - Additional markdown representation for image files
              - Error messages for unsupported types

    Example:
        >>> parse_result({"value": 42, "structure": "http://example.com/structure.cif", "phonon": "http://example.com/phonon.png"})

        >>> [
        >>>    {"name": "value", "data": 42, "type": "Value"},
        >>>    {"name": "structure", "data": "structure.cif", "type": "MatModelerFile", "url": "http://example.com/structure.cif"},
        >>>    {"name": "phonon", "data": "phonon.png", "type": "RegularFile", "url": "http://example.com/phonon.png"}
        >>>    {"name": "markdown_image_phonon", "data": "![phonon.png](http://example.com/phonon.png)", "type": "Value"}
        >>> ]
    """
    parsed_result = []
    new_result = {}
    for k, v in result.items():
        if type(v) is dict:
            new_result.update(**flatten_dict(v))
        else:
            new_result[k] = v

    for k, v in new_result.items():
        if type(v) in [int, float, bool]:
            parsed_result.append(
                JobResult(name=k, data=v, type=JobResultType.Value).model_dump(
                    mode='json'
                )
            )
        elif type(v) is str:
            if v.startswith('```') and v.endswith('```'):
                parsed_result.append(
                    JobResult(
                        name=k, data=v, type=JobResultType.MarkdownCode
                    ).model_dump(mode='json')
                )
            elif v.startswith('http'):
                # 写入数据库
                await insert_session_files(session_id=ctx.session.id, files=[v])

                # 按文件类型解析
                filename = v.split('/')[-1]
                if await is_matmodeler_file(filename):
                    parsed_result.append(
                        JobResult(
                            name=k,
                            data=filename,
                            type=JobResultType.MatModelerFile,
                            url=v,
                        ).model_dump(mode='json')
                    )
                elif await is_echarts_file(filename):
                    parsed_result.append(
                        JobResult(
                            name=k,
                            data=filename,
                            type=JobResultType.EchartsFile,
                            url=v,
                        ).model_dump(mode='json')
                    )
                else:
                    parsed_result.append(
                        JobResult(
                            name=k, data=filename, type=JobResultType.RegularFile, url=v
                        ).model_dump(mode='json')
                    )
                if await is_image_file(filename):
                    # Extra Add Markdown Image
                    parsed_result.append(
                        JobResult(
                            name=f"markdown_image_{k}",
                            data=f"![{filename}]({v})",
                            type=JobResultType.Value,
                        ).model_dump(mode='json')
                    )
            else:
                parsed_result.append(
                    JobResult(name=k, data=v, type=JobResultType.Value).model_dump(
                        mode='json'
                    )
                )
        elif await is_float_sequence(v):
            parsed_result.append(
                JobResult(
                    name=k,
                    data=f"{tuple([float(item) for item in v])}",
                    type=JobResultType.Value,
                ).model_dump(mode='json')
            )
        elif await is_str_sequence(v):
            parsed_result.append(
                JobResult(
                    name=k,
                    data=f"{tuple([str(item) for item in v])}",
                    type=JobResultType.Value,
                ).model_dump(mode='json')
            )
        elif await is_literature_sequence(v):
            for item in v:
                parsed_result.append(LiteratureItem(**item).model_dump(mode='json'))
        elif await is_web_search_sequence(v):
            for item in v:
                parsed_result.append(WebSearchItem(**item).model_dump(mode='json'))
        elif await is_float_matrix(v):
            parsed_result.append(Matrix(title=k, values=v).model_dump(mode='json'))
        else:
            parsed_result.append(
                {
                    'status': 'error',
                    'msg': f"{k}({type(v)}) is not supported parse, v={v}",
                }
            )
    return parsed_result


def get_kv_result(parsed_tool_result: List[dict]):
    return {
        'eventType': 1,
        'eventData': {
            'contentType': 1,
            'renderType': '@bohrium-chat/matmodeler/dialog-file',
            'content': {
                JOB_RESULT_KEY: [
                    item
                    for item in parsed_tool_result
                    if item.get('status', None) is None
                    and item.get('name')
                    and item.get('data')
                    and not (item.get('name') == 'code')
                    and not (item['name'].startswith('markdown_image'))
                ]
            },
        },
    }


def get_markdown_image_result(parsed_tool_result: List[JobResult]) -> List[JobResult]:
    return [
        item
        for item in parsed_tool_result
        if item.get('name') and item['name'].startswith('markdown_image')
    ]


def get_echarts_result(parsed_tool_result: List[JobResult]) -> List[JobResult]:
    return [
        item
        for item in parsed_tool_result
        if item.get('name') and item['type'] == JobResultType.EchartsFile
    ]


def get_matrix_result(
    parsed_tool_result: List[Union[JobResult, Matrix]],
) -> List[Matrix]:
    return [
        item
        for item in parsed_tool_result
        if item.get('meta_type') and item['meta_type'] == RenderTypeEnum.MATRIX
    ]


def get_csv_result(parsed_tool_result: List[JobResult]) -> List[JobResult]:
    return [
        item
        for item in parsed_tool_result
        if item.get('data')
        and type(item['data']) is str
        and item['data'].endswith('csv')
        and item['type'] == JobResultType.RegularFile
    ]


def get_markdown_code_result(parsed_tool_result: List[JobResult]) -> List[JobResult]:
    return [
        item
        for item in parsed_tool_result
        if item.get('data')
        and type(item['data']) is str
        and item['type'] == JobResultType.MarkdownCode
    ]


def matrix_to_markdown_table(matrix, auto_header=True):
    title, values = matrix['title'], matrix['values']

    if not values:
        return ''

    data_rows = values

    if auto_header:
        col_count = len(values[0])
        header = [f"Col{i + 1}" for i in range(col_count)]
    else:
        header = values[0]
        data_rows = values[1:]

    # markdown 拼接
    lines = []

    if title:
        lines.append(f"- {title}\n")

    # header 行
    if header:
        sep = ['---'] * len(header)
        lines.append(' | '.join(header))
        lines.append(' | '.join(sep))

    # 内容行
    for row in data_rows:
        lines.append(' | '.join(str(v) for v in row))

    return '\n'.join(lines)


async def csv_to_markdown_table(csv_url, title=None):
    """
    下载 CSV 文件并转换为 markdown 表格字符串
    """
    MAX_SIZE_BYTES = 1 * 1024 * 1024  # 1M

    async with aiohttp.ClientSession() as session:
        async with session.get(csv_url) as resp:
            resp.raise_for_status()

            # 检查 Content-Length 头部
            content_length = resp.content_length

            # 如果有 Content-Length 且超过限制，直接返回空字符串
            if content_length and content_length > MAX_SIZE_BYTES:
                logger.warning(
                    f"CSV 文件过大: {content_length} 字节 > {MAX_SIZE_BYTES} 字节"
                )
                return ''

            content = await resp.text()

    # 解析 CSV
    reader = csv.reader(io.StringIO(content))
    values = [row for row in reader]

    matrix = {'title': title, 'values': values}

    return matrix_to_markdown_table(matrix, auto_header=False)


if __name__ == '__main__':
    import asyncio

    csv_url = 'https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/13756/1760873/store/c1534529d88519fc8156c6c6e71207fdcac84f08/outputs/results_file/critical_temperature.csv'
    result = asyncio.run(csv_to_markdown_table(csv_url))
