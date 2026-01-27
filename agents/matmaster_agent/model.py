from enum import Enum
from typing import Awaitable, Callable, List, Literal, Optional, TypeAlias, Union

from google.adk.tools import BaseTool
from pydantic import BaseModel, HttpUrl

CostFuncType: TypeAlias = Callable[[BaseTool, dict], Awaitable[tuple[int, int]]]


class JobStatus(str, Enum):
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'


class JobResultType(str, Enum):
    RegularFile = 'RegularFile'
    MatModelerFile = 'MatModelerFile'
    EchartsFile = 'EchartsFile'
    Value = 'Value'
    MarkdownCode = 'MarkdownCode'


class RenderTypeEnum(str, Enum):
    JOB_RESULT = 'job_result'
    LITERATURE = 'literature'
    WEB = 'web'
    MATRIX = 'matrix'


class JobResult(BaseModel):
    name: str
    data: Union[int, float, str]
    url: Optional[str] = ''
    type: JobResultType
    meta_type: Literal[tuple(RenderTypeEnum.__members__.values())] = (
        RenderTypeEnum.JOB_RESULT
    )


class BohrJobInfo(BaseModel):
    origin_job_id: str
    job_id: Union[int, str]
    job_detail_url: str
    job_status: JobStatus
    job_name: str
    job_result: Optional[List[JobResult]] = None
    job_in_ctx: bool = False
    agent_name: str
    resource_type: Optional[str] = 'sandbox'


class DFlowJobInfo(BaseModel):
    origin_job_id: str
    job_name: str
    job_status: JobStatus
    workflow_id: str
    workflow_uid: str
    workflow_url: str
    job_result: Optional[List[JobResult]] = None
    job_in_ctx: bool = False


class LiteratureItem(BaseModel):
    doi: str
    publicationEnName: str
    enName: str
    enAbstract: str
    authors: List[str]
    coverDateStart: str
    citationNums: int
    good: int
    paperUrl: Union[HttpUrl, str] = ''
    meta_type: Literal[tuple(RenderTypeEnum.__members__.values())] = (
        RenderTypeEnum.LITERATURE
    )


class WebSearchItem(BaseModel):
    title: str
    link: HttpUrl
    snippet: str
    meta_type: Literal[tuple(RenderTypeEnum.__members__.values())] = RenderTypeEnum.WEB


class Matrix(BaseModel):
    title: str
    values: List[List[float]]
    meta_type: Literal[tuple(RenderTypeEnum.__members__.values())] = (
        RenderTypeEnum.MATRIX
    )


class UserContent(BaseModel):
    language: str


class ToolCallInfoSchema(BaseModel):
    tool_name: str
    tool_args: dict
    missing_tool_args: List[str]
