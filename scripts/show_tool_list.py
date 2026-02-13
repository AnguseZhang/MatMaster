#!/usr/bin/env python3
"""
查看当前 MatMaster 的 tool list（ALL_TOOLS / ALL_AGENT_TOOLS_LIST）。
用法（在项目根 MatMaster-test 下）：
  uv run python scripts/show_tool_list.py
  uv run python scripts/show_tool_list.py --verbose   # 输出每个工具的 scene、description 摘要
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 保证项目根在 path 中
_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.sub_agents.mapping import ALL_AGENT_TOOLS_LIST


def main() -> None:
    parser = argparse.ArgumentParser(description="查看 MatMaster tool list")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="输出每个工具的 scene、description 摘要",
    )
    args = parser.parse_args()

    print(f"ALL_AGENT_TOOLS_LIST 数量: {len(ALL_AGENT_TOOLS_LIST)}")
    print(f"ALL_TOOLS 数量: {len(ALL_TOOLS)}")
    print()

    # 工具名列表（与 ALL_AGENT_TOOLS_LIST 一致）
    names = sorted(ALL_TOOLS.keys())
    print("工具名列表 (按字母序):")
    print("-" * 50)
    for i, name in enumerate(names, 1):
        print(f"  {i:3}. {name}")
    print()

    if args.verbose:
        print("每个工具详情 (scene + description 首行):")
        print("-" * 50)
        for name in names:
            info = ALL_TOOLS.get(name, {})
            scene = info.get("scene", [])
            scene_str = ", ".join(str(s) for s in scene)
            desc = info.get("description", "")
            first_line = desc.split("\n")[0][:80] + ("..." if len(desc) > 80 else "")
            print(f"  {name}")
            print(f"    scene: {scene_str}")
            print(f"    description: {first_line}")
            print()


if __name__ == "__main__":
    main()
