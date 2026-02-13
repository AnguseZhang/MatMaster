#!/usr/bin/env python3
"""
RAG make_plan：根据用户问题与知识库上下文制定执行计划。
  - 检索实体+边、按边补召，再缩减为仅实体 function 传给 LLM
  - 校验时 tool_name 须来自上下文 Entities

用法：
    python run_make_plan.py --query "对 SiO₂ 液态熔体在 1200 K 下运行短时分子动力学" --root .
    python run_make_plan.py --query "..." --root . --out output/plan.txt --out-context output/context.txt
    python run_make_plan.py --query "..." --root . --out-context-full output/context_full.txt
    --query2：同进程再跑一条查询仅检索，验证 retrieve_imports≈0
"""
import argparse
import sys
import time
from pathlib import Path

from make_plan_rag import build_graphrag_context, run_make_plan_rag


def main():
    parser = argparse.ArgumentParser(
        description="RAG make_plan：仅实体 + function 传给 LLM，无边"
    )
    parser.add_argument("--query", type=str, required=True, help="用户查询")
    parser.add_argument("--settings", type=Path, default=Path("settings.yaml"), help="settings.yaml 路径")
    parser.add_argument("--root", type=Path, default=Path("."), help="GraphRAG 项目根目录")
    parser.add_argument("--out", type=Path, default=None, help="输出文件（默认 stdout）")
    parser.add_argument("--out-context", type=Path, default=None, dest="out_context", help="将传给 LLM 的 RAG 上下文（仅实体 function）写入该文件")
    parser.add_argument("--out-context-full", type=Path, default=None, dest="out_context_full", help="将缩减前的完整上下文（Entities+Relationships，含边）写入该文件")
    parser.add_argument("--query2", type=str, default=None, help="同进程再跑一条查询的检索（仅检索不调 LLM），用于验证第二次 retrieve_imports≈0")
    args = parser.parse_args()

    t0_total = time.perf_counter()
    timings = {}

    print("[1/5] 加载 LLM 配置...", file=sys.stderr)
    print("[1b/5] 预加载 graphrag 模块（首次约 10s，之后 retrieve_imports≈0）...", file=sys.stderr)
    print("[2/5] 构建 GraphRAG 上下文（实体+边 → 缩减为仅实体 function）...", file=sys.stderr)
    print("[3/5] 从上下文解析实体...", file=sys.stderr)
    print("[4/5] 构建用户消息（问题 + 仅实体 function 上下文）...", file=sys.stderr)
    print("[5/5] 调用 LLM 生成计划...", file=sys.stderr)

    try:
        result = run_make_plan_rag(
            "default",
            args.query,
            args.root,
            settings_path=args.settings,
            timings=timings,
            out_context=args.out_context,
            out_context_full=args.out_context_full,
        )
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    raw_output = result.raw_output
    is_valid = result.is_valid
    errors = result.errors
    parsed_data = result.parsed_data
    context_entity_names = result.context_entity_names

    print(f"      模型: (见 settings)  用时: {timings.get('1_load_llm_config', 0):.2f}s", file=sys.stderr)
    print(f"      用时: {timings.get('1b_warmup_imports', 0):.2f}s", file=sys.stderr)
    print(f"      检索+边补召 总用时: {timings.get('2a_build_context', 0):.2f}s", file=sys.stderr)
    for key in sorted(timings.keys()):
        if key.startswith("retrieve_"):
            print(f"        {key}: {timings[key]:.2f}s", file=sys.stderr)
    if args.out_context_full:
        print(f"      完整上下文（含边）已写入: {args.out_context_full}", file=sys.stderr)
    print(f"      缩减为仅 entity+function 用时: {timings.get('2b_reduce_to_function_only', 0):.2f}s", file=sys.stderr)
    print(f"      传给 LLM 的上下文长度: {len(result.context)} 字符", file=sys.stderr)
    if args.out_context:
        print(f"      RAG 上下文已写入: {args.out_context}", file=sys.stderr)
    print(f"[3/5] 从上下文解析到 {len(context_entity_names)} 个实体  用时: {timings.get('3_parse_entities', 0):.2f}s", file=sys.stderr)
    print(f"      用时: {timings.get('4_build_message', 0):.2f}s", file=sys.stderr)
    print(f"      用时: {timings.get('5_call_llm', 0):.2f}s", file=sys.stderr)
    print("校验输出 JSON...", file=sys.stderr)
    print(f"      用时: {timings.get('6_validate_json', 0):.2f}s", file=sys.stderr)

    total_elapsed = time.perf_counter() - t0_total
    print("", file=sys.stderr)
    print("--- 各步用时 ---", file=sys.stderr)
    main_keys = ["1_load_llm_config", "1b_warmup_imports", "2a_build_context", "2b_reduce_to_function_only",
                 "3_parse_entities", "4_build_message", "5_call_llm", "6_validate_json"]
    for name in main_keys:
        if name in timings:
            print(f"  {name}: {timings[name]:.2f}s", file=sys.stderr)
    for name in sorted(timings.keys()):
        if name.startswith("retrieve_"):
            print(f"  {name}: {timings[name]:.2f}s", file=sys.stderr)
    for name in sorted(timings.keys()):
        if name not in main_keys and not name.startswith("retrieve_"):
            print(f"  {name}: {timings[name]:.2f}s", file=sys.stderr)
    print(f"  总用时: {total_elapsed:.2f}s", file=sys.stderr)
    print("", file=sys.stderr)
    sys.stderr.flush()

    output_lines = [
        "=" * 60,
        "MatMaster make_plan（RAG：仅实体 function，无边）",
        "=" * 60,
        "",
        f"用户查询: {args.query}",
        f"上下文中实体数: {len(context_entity_names)}",
        "",
        "--- LLM 原始输出 ---",
        raw_output,
        "",
        "--- JSON 校验结果 ---",
        f"校验通过: {'✓ 是' if is_valid else '✗ 否'}",
    ]
    if errors:
        output_lines.append("")
        output_lines.append("校验错误:")
        for err in errors:
            output_lines.append(f"  - {err}")
    if parsed_data and is_valid:
        output_lines.append("")
        output_lines.append("--- 计划摘要 ---")
        for i, plan in enumerate(parsed_data.get("plans", [])):
            plan_id = plan.get("plan_id", f"plan_{i}")
            strategy = plan.get("strategy", "N/A")
            steps = plan.get("steps", [])
            output_lines.append("")
            output_lines.append(f"方案 {i + 1} [{plan_id}]: {strategy}")
            output_lines.append(f"  步骤数: {len(steps)}")
            for j, step in enumerate(steps):
                tool = step.get("tool_name") or "(无工具)"
                desc = (step.get("description") or "")[:60]
                output_lines.append(f"    {j + 1}. [{tool}] {desc}...")
    output_lines.append("")
    output_lines.append("=" * 60)

    text = "\n".join(output_lines)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"结果已写入: {args.out}", file=sys.stderr)
    else:
        print(text)

    if args.query2:
        print("", file=sys.stderr)
        print("[同进程 第二问] 仅检索（不调 LLM），验证 retrieve_imports 是否≈0 ...", file=sys.stderr)
        timings2 = {}
        t0_2 = time.perf_counter()
        context_full2 = build_graphrag_context(args.root, args.query2, timings=timings2)
        elapsed2 = time.perf_counter() - t0_2
        print(f"      检索+边补召 总用时: {elapsed2:.2f}s", file=sys.stderr)
        for key in sorted(timings2.keys()):
            if key.startswith("retrieve_"):
                print(f"        {key}: {timings2[key]:.2f}s", file=sys.stderr)
        if "retrieve_imports" in timings2:
            v = timings2["retrieve_imports"]
            print(f"      => retrieve_imports={v:.2f}s （同进程第二次应为≈0）", file=sys.stderr)
        sys.stderr.flush()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
