from enum import Enum
from typing import Awaitable, Callable, List, Optional, TypeAlias, Union

from google.adk.tools import BaseTool
from pydantic import BaseModel

CostFuncType: TypeAlias = Callable[[BaseTool, dict], Awaitable[tuple[int, int]]]


class JobStatus(str, Enum):
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'


class JobResultType(str, Enum):
    RegularFile = 'RegularFile'
    MatModelerFile = 'MatModelerFile'
    Value = 'Value'


class JobResult(BaseModel):
    name: str
    data: Union[int, float, str]
    url: Optional[str] = ''
    type: JobResultType


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


class ParamsCheckComplete(BaseModel):
    flag: bool
    reason: str
    analyzed_messages: List[str]


class UserContent(BaseModel):
    language: str


class ToolCallInfo(BaseModel):
    tool_name: str
    tool_args: dict
    missing_tool_args: List[str]
