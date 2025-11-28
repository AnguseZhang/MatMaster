from typing import Any, Dict, List

from pydantic import BaseModel


class AsyncToolParamsSchema(BaseModel):
    """单个异步工具的参数信息"""

    tool_name: str
    step_index: int
    description: str
    tool_args: Dict[str, Any]
    missing_tool_args: List[str]
    agent_name: str


class DflowParamsCollectionSchema(BaseModel):
    """所有异步工具的参数收集结果"""

    async_tools: List[AsyncToolParamsSchema]
    total_count: int
