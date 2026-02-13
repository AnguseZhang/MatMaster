#!/usr/bin/env python3
"""
比对 RAG output 里实体表（entities.parquet）与当前 MatMaster ALL_TOOLS 的差异。
归一化规则：小写、连字符 - 视为下划线 _，再比较。

用法（在项目根 MatMaster-test 下）：
  uv run python scripts/compare_rag_entities_with_tools.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pandas as pd
from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS


def to_key(s: str) -> str:
    return s.lower().replace("-", "_")


def main() -> None:
    entities_path = _root / "rag" / "output" / "entities.parquet"
    if not entities_path.exists():
        print(f"未找到实体表: {entities_path}")
        sys.exit(1)

    df = pd.read_parquet(entities_path)
    rag_titles = df["title"].astype(str).str.strip().tolist()
    tool_names = list(ALL_TOOLS.keys())

    rag_by_key = {to_key(t): t for t in rag_titles}
    tools_by_key = {to_key(t): t for t in tool_names}

    in_rag_only = sorted([rag_by_key[k] for k in rag_by_key if k not in tools_by_key], key=str.lower)
    in_tools_only = sorted([tools_by_key[k] for k in tools_by_key if k not in rag_by_key], key=str.lower)
    in_both = sorted([rag_by_key[k] for k in rag_by_key if k in tools_by_key], key=str.lower)

    print("=" * 60)
    print("RAG 实体表 vs MatMaster ALL_TOOLS 比对")
    print("=" * 60)
    print(f"RAG 实体表 (entities.parquet): {len(rag_titles)} 个")
    print(f"当前 ALL_TOOLS: {len(tool_names)} 个")
    print()
    print("--- 仅在 RAG 中、不在 ALL_TOOLS 中 ---")
    print(f"共 {len(in_rag_only)} 个:")
    for x in in_rag_only:
        print(f"  {x}")
    print()
    print("--- 仅在 ALL_TOOLS 中、不在 RAG 实体表中 ---")
    print(f"共 {len(in_tools_only)} 个:")
    for x in in_tools_only:
        print(f"  {x}")
    print()
    print("--- 两边都有（名称可对应）---")
    print(f"共 {len(in_both)} 个")
    for x in in_both:
        print(f"  {x}")


if __name__ == "__main__":
    main()
