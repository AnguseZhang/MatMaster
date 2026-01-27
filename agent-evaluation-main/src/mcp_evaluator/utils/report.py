import json
import os
from typing import Any


def truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "…"


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)


def write_text(path: str, text: str) -> None:
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")


def write_json(path: str, obj: Any) -> None:
    write_text(path, json.dumps(obj, ensure_ascii=False, indent=2))


def format_latency(ms: int) -> str:
    if ms < 1000:
        return f"{ms}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}m{rem_seconds:.1f}s"


def render_human_report(report: dict[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    cases = report.get("cases") if isinstance(report.get("cases"), list) else []

    total = int(summary.get("total") or len(cases) or 0)
    passed = int(summary.get("passed") or 0)
    avg_policy = summary.get("avg_policy_score")
    avg_latency = summary.get("avg_latency_ms")

    header_lines = [
        "测试报告",
        f"- Server: {report.get('server_url')}",
        f"- 总用例: {total}",
        f"- 通过: {passed}",
        f"- 失败: {max(0, total - passed)}",
    ]
    if isinstance(avg_policy, (int, float)):
        header_lines.append(f"- 平均策略分: {int(avg_policy)}")
    if isinstance(avg_latency, (int, float)):
        header_lines.append(f"- 平均耗时: {format_latency(int(avg_latency))}")

    by_tool: dict[str, list[dict[str, Any]]] = {}
    for c in cases:
        if not isinstance(c, dict):
            continue
        tool = c.get("tool_name")
        if not isinstance(tool, str) or not tool:
            tool = "<unknown>"
        by_tool.setdefault(tool, []).append(c)

    tool_lines: list[str] = []
    for tool in sorted(by_tool.keys()):
        items = by_tool[tool]
        tool_total = len(items)
        tool_passed = sum(1 for x in items if x.get("ok") is True)
        avg_tool_latency = int(
            sum(int(x.get("latency_ms") or 0) for x in items) / max(1, tool_total)
        )
        avg_tool_policy = int(
            sum(int(x.get("policy_score") or 0) for x in items) / max(1, tool_total)
        )
        tool_lines.append(
            f"- {tool}: {tool_passed}/{tool_total}  平均策略分 {avg_tool_policy}  平均耗时 {format_latency(avg_tool_latency)}"
        )

    failed_lines: list[str] = []
    failed = [c for c in cases if isinstance(c, dict) and c.get("ok") is not True]
    if failed:
        failed_lines.append("失败用例")
        for c in failed[:20]:
            case_id = c.get("case_id") if isinstance(c.get("case_id"), str) else "<unknown>"
            tool = c.get("tool_name") if isinstance(c.get("tool_name"), str) else "<unknown>"
            err = c.get("error") if isinstance(c.get("error"), str) else ""
            oracle_err = c.get("oracle_error") if isinstance(c.get("oracle_error"), str) else ""
            msg = err or oracle_err or "unknown"
            failed_lines.append(f"- {case_id} ({tool}): {msg}")

    repair_counts: dict[str, int] = {}
    violation_counts: dict[str, int] = {}
    for c in cases:
        if not isinstance(c, dict):
            continue
        repairs = c.get("policy_repairs")
        if isinstance(repairs, list):
            for r in repairs:
                if isinstance(r, dict) and isinstance(r.get("type"), str):
                    repair_counts[r["type"]] = repair_counts.get(r["type"], 0) + 1
        violations = c.get("policy_violations")
        if isinstance(violations, list):
            for v in violations:
                if isinstance(v, dict) and isinstance(v.get("type"), str):
                    violation_counts[v["type"]] = violation_counts.get(v["type"], 0) + 1

    policy_lines: list[str] = []
    if repair_counts or violation_counts:
        policy_lines.append("策略统计")
        for k, v in sorted(repair_counts.items()):
            policy_lines.append(f"- [修复] {k}: {v}")
        for k, v in sorted(violation_counts.items()):
            policy_lines.append(f"- [违规] {k}: {v}")

    return "\n".join(header_lines + [""] + tool_lines + [""] + failed_lines + [""] + policy_lines)


def render_human_report_md(report: dict[str, Any]) -> str:
    # This could be a single report or an aggregated report
    is_aggregated = "suites" in report
    
    md = ["# MCP 工具测试报告"]
    
    if is_aggregated:
        md.append(f"- **总套件数**: {len(report['suites'])}")
        md.append(f"- **总执行时间**: {report['created_at']}")
        
        summary = report.get("summary", {})
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        avg_latency = summary.get("avg_latency_ms", 0)
        avg_policy = summary.get("avg_policy_score", 0)
        
        md.append(f"- **总用例数**: {total}")
        md.append(f"- **总通过数**: {passed}")
        md.append(f"- **总体通过率**: {(passed/max(1, total)*100):.1f}%")
        md.append(f"- **平均策略分**: {int(avg_policy)}")
        md.append(f"- **平均耗时**: {format_latency(int(avg_latency))}")
        
        md.append("\n## 套件概览")
        md.append("| 套件名称 | 通过率 | 平均策略分 | 平均耗时 |")
        md.append("| :--- | :--- | :--- | :--- |")
        for s in report["suites"]:
            s_name = s.get("agent_name") or "Unknown"
            s_sum = s.get("summary", {})
            s_total = s_sum.get("total", 0)
            s_passed = s_sum.get("passed", 0)
            s_policy = s_sum.get("avg_policy_score", 0)
            s_latency = s_sum.get("avg_latency_ms", 0)
            md.append(f"| {s_name} | {s_passed}/{s_total} | {s_policy} | {format_latency(int(s_latency))} |")
            
        md.append("\n## 详细统计 (按套件)")
        for s in report["suites"]:
            s_name = s.get("agent_name") or "Unknown"
            md.append(f"\n### {s_name}")
            md.append(f"- **Server**: `{s.get('server_url')}`")
            
            cases = s.get("cases", [])
            by_tool: dict[str, list[dict[str, Any]]] = {}
            for c in cases:
                tool = c.get("tool_name") or "<unknown>"
                by_tool.setdefault(tool, []).append(c)
                
            md.append("| 工具 | 通过率 | 平均策略分 | 平均耗时 |")
            md.append("| :--- | :--- | :--- | :--- |")
            for tool in sorted(by_tool.keys()):
                items = by_tool[tool]
                t_total = len(items)
                t_passed = sum(1 for x in items if x.get("ok") is True)
                t_latency = int(sum(int(x.get("latency_ms") or 0) for x in items) / t_total)
                t_policy = int(sum(int(x.get("policy_score") or 0) for x in items) / t_total)
                md.append(f"| {tool} | {t_passed}/{t_total} | {t_policy} | {format_latency(t_latency)} |")
    else:
        summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
        cases = report.get("cases") if isinstance(report.get("cases"), list) else []

        total = int(summary.get("total") or len(cases) or 0)
        passed = int(summary.get("passed") or 0)
        avg_policy = summary.get("avg_policy_score")
        avg_latency = summary.get("avg_latency_ms")

        md.append(f"- **Agent**: `{report.get('agent_name', 'Unknown')}`")
        md.append(f"- **服务器**: `{report.get('server_url')}`")
        md.append(f"- **总用例**: {total}")
        md.append(f"- **通过**: {passed}")
        md.append(f"- **失败**: {total - passed}")
        
        if isinstance(avg_policy, (int, float)):
            md.append(f"- **平均策略分**: {int(avg_policy)}")
        if isinstance(avg_latency, (int, float)):
            md.append(f"- **平均耗时**: {format_latency(int(avg_latency))}")

        md.append("\n## 工具统计")
        by_tool: dict[str, list[dict[str, Any]]] = {}
        for c in cases:
            if isinstance(c, dict):
                tool = c.get("tool_name") or "<unknown>"
                by_tool.setdefault(tool, []).append(c)

        md.append("| 工具 | 通过率 | 平均策略分 | 平均耗时 |")
        md.append("| :--- | :--- | :--- | :--- |")
        for tool in sorted(by_tool.keys()):
            items = by_tool[tool]
            t_total = len(items)
            t_passed = sum(1 for x in items if x.get("ok") is True)
            t_latency = int(sum(int(x.get("latency_ms") or 0) for x in items) / t_total)
            t_policy = int(sum(int(x.get("policy_score") or 0) for x in items) / t_total)
            md.append(f"| {tool} | {t_passed}/{t_total} | {t_policy} | {format_latency(t_latency)} |")

        failed = [c for c in cases if isinstance(c, dict) and c.get("ok") is not True]
        if failed:
            md.append("\n## 失败用例详情")
            md.append("| 用例ID | 工具 | 错误原因 |")
            md.append("| :--- | :--- | :--- |")
            for c in failed[:50]:
                cid = c.get("case_id") or "N/A"
                tool = c.get("tool_name") or "N/A"
                err = c.get("error") or c.get("oracle_error") or "unknown"
                md.append(f"| {cid} | {tool} | {err} |")

    return "\n".join(md)
