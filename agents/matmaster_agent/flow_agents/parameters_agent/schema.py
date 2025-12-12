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
    prev_step_index: int | None = None  # 前一个步骤的索引（如果存在）
    next_step_indices: List[int] = []  # 后续步骤的索引列表（如果存在）


class DflowParamsCollectionSchema(BaseModel):
    """所有异步工具的参数收集结果"""

    async_tools: List[AsyncToolParamsSchema]
    total_count: int
    function_declarations: List[Dict] = (
        []
    )  # 保存所有工具的 function_declarations，用于后续生成 JSON
