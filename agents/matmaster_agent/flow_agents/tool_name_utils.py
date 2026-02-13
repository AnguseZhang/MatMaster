"""
工具名规范化：将 RAG/计划中的工具名（如 BUILD_BULK_STRUCTURE_BY_TEMPLATE）
规范为 ALL_TOOLS 的键（如 build_bulk_structure_by_template）。
独立模块避免 flow_agents.utils 与 recommend_summary_agent 等循环导入。
"""
from __future__ import annotations

from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS


def normalize_tool_name_to_canonical(tool_name: str) -> str | None:
    """
    将 RAG/计划中的工具名规范为 ALL_TOOLS 的键。
    大小写不敏感，- 与 _ 视为等价匹配。
    """
    if not tool_name or not str(tool_name).strip():
        return None
    name = str(tool_name).strip()
    if name in ALL_TOOLS:
        return name
    low = name.lower()
    if low in ALL_TOOLS:
        return low
    norm = low.replace("-", "_")
    for k in ALL_TOOLS:
        if k.lower().replace("-", "_") == norm:
            return k
    return name
