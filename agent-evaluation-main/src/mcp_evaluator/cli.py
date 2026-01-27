import argparse
import asyncio
import json
import os
import time
from dataclasses import asdict
from typing import Any, List

from .core import get_tool_schema, list_tools, run_one_case
from .models import ToolCall, ToolSchema
from .utils import (
    load_json,
    render_human_report,
    render_human_report_md,
    write_json,
    write_text,
    parse_suite_cases,
)

DEFAULT_SERVER_URL = "http://bowd1412840.bohrium.tech:50001/sse"


async def run_suite(
    suite_dir: str | None,
    config_path: str | None,
    cases_path: str | None,
    server_url_override: str | None,
    timeout_s_cli: float | None,
    budget_n_results_max_cli: int | None,
    print_tools_cli: bool | None,
    threads_cli: int | None,
    report_path_cli: str | None,
    report_detail_path_cli: str | None,
    report_md_path_cli: str | None,
    global_config: dict[str, Any],
) -> dict[str, Any] | None:
    config: dict[str, Any] = {}
    agent_name = ""

    if suite_dir:
        config_path = config_path or os.path.join(suite_dir, "config.json")
        cases_path = cases_path or os.path.join(suite_dir, "cases.json")
        agent_name = os.path.basename(suite_dir.rstrip(os.sep))

    if config_path and os.path.exists(config_path):
        raw = load_json(config_path)
        if isinstance(raw, dict):
            config = raw

    # Hierarchical resolution
    def get_setting(key: str, cli_val: Any = None, default: Any = None) -> Any:
        if cli_val is not None:
            return cli_val
        if key in config:
            return config[key]
        if key in global_config:
            return global_config[key]
        return default

    # Special resolution for server_url
    server_url = server_url_override
    if not server_url or server_url == DEFAULT_SERVER_URL:
        if "server_url" in config:
            server_url = config["server_url"]
        elif agent_name and "agents" in global_config and agent_name in global_config["agents"]:
            server_url = global_config["agents"][agent_name]
        else:
            server_url = server_url or DEFAULT_SERVER_URL

    timeout_s = float(get_setting("timeout_s", timeout_s_cli, 20.0))
    budget_n_results_max = int(get_setting("budget_n_results_max", budget_n_results_max_cli, 50))
    print_tools = bool(get_setting("print_tools", print_tools_cli, False))
    threads = int(get_setting("threads", threads_cli, 1))

    if not cases_path or not os.path.exists(cases_path):
        print(f"Skipping {agent_name or suite_dir}: cases.json not found at {cases_path}")
        return None

    print(f"\n>>> Running suite: {agent_name or suite_dir}")
    if threads > 1:
        print(f"    Concurrent threads: {threads}")

    # Path resolution
    report_detail_path = report_detail_path_cli or report_path_cli or config.get("report_detail_path") or config.get("report_path")
    report_md_path = report_md_path_cli or config.get("report_md_path")

    if not report_detail_path or not report_md_path:
        base_report_path = report_path_cli or global_config.get("report_path")
        if base_report_path and agent_name:
            target_dir = os.path.join(base_report_path, agent_name)
            if not report_detail_path:
                report_detail_path = os.path.join(target_dir, "report_detail.json")
            if not report_md_path:
                report_md_path = os.path.join(target_dir, "report.md")

    if suite_dir:
        if not report_detail_path:
            report_detail_path = os.path.join(suite_dir, "report_detail.json")
        if not report_md_path:
            report_md_path = os.path.join(suite_dir, "report.md")

    suite_cases = parse_suite_cases(load_json(cases_path))
    
    tools: list[str] | None = None
    if print_tools:
        try:
            tools = await list_tools(server_url, timeout_s=timeout_s)
        except Exception as e:
            print(f"    Warning: Failed to list tools: {e}")

    schema_cache: dict[str, ToolSchema | None] = {}
    schema_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(threads)

    async def get_cached_schema(tool_name: str) -> ToolSchema | None:
        async with schema_lock:
            if tool_name not in schema_cache:
                try:
                    schema = await get_tool_schema(server_url, tool_name=tool_name, timeout_s=timeout_s)
                    schema_cache[tool_name] = schema
                except Exception:
                    schema_cache[tool_name] = None
            return schema_cache[tool_name]

    async def run_with_semaphore(c):
        async with semaphore:
            schema = await get_cached_schema(c.tool_name)
            return await run_one_case(
                server_url,
                ToolCall(tool_name=c.tool_name, args=c.args),
                timeout_s=timeout_s,
                tool_schema=schema,
                budget_n_results_max=budget_n_results_max,
                case_id=c.case_id,
                expect=c.expect,
            )

    tasks = [run_with_semaphore(c) for c in suite_cases]
    results = await asyncio.gather(*tasks)

    passed = sum(1 for r in results if r.ok)
    avg_latency = int(sum(r.latency_ms for r in results) / max(1, len(results)))
    avg_policy = int(sum(r.policy_score for r in results) / max(1, len(results)))
    
    report = {
        "version": "l1-mvp-1",
        "agent_name": agent_name,
        "server_url": server_url,
        "timestamp_ms": int(time.time() * 1000),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tools": tools,
        "cases": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "passed": passed,
            "avg_policy_score": avg_policy,
            "avg_latency_ms": avg_latency,
        },
    }

    print(f"    Results: {passed}/{len(results)} passed.")

    if report_detail_path:
        write_json(report_detail_path, report)
        print(f"    Detailed report: {report_detail_path}")
    if report_md_path:
        write_text(report_md_path, render_human_report_md(report))
        print(f"    Markdown report: {report_md_path}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(prog="mcp-evaluator")
    parser.add_argument("--render-report", help="Path to report.json to render as human-readable text")
    parser.add_argument("--report-detail-path", help="Path to save detailed JSON report")
    parser.add_argument("--report-md-path", help="Path to save Markdown report")
    parser.add_argument("--suite-dir", help="Directory containing config.json and cases.json")
    parser.add_argument("--config-path", help="Path to config.json")
    parser.add_argument("--cases-path", help="Path to cases.json")
    parser.add_argument(
        "--server-url",
        help="MCP server SSE URL",
    )
    parser.add_argument("--timeout-s", type=float, help="Timeout for each tool call")
    parser.add_argument("--budget-n-results-max", type=int, help="Max n_results allowed by policy")
    parser.add_argument("--print-tools", action="store_true", help="List available tools before running")
    parser.add_argument("--threads", type=int, help="Number of concurrent tool calls")
    parser.add_argument("--report-path", help="Base path for reports")
    args = parser.parse_args()

    if args.render_report:
        raw = load_json(args.render_report)
        if not isinstance(raw, dict):
            raise SystemExit("report.json must be an object")
        print(render_human_report(raw))
        return 0

    # Load global config from cases/config.json
    global_config: dict[str, Any] = {}
    global_config_path = os.path.join("cases", "config.json")
    if os.path.exists(global_config_path):
        try:
            global_config = load_json(global_config_path)
        except Exception as e:
            print(f"Warning: Failed to load global config from {global_config_path}: {e}")

    async def run_all():
        suites_to_run = []
        
        # If specific suite/cases provided, run only those
        if args.suite_dir or args.cases_path:
            suites_to_run.append({
                "suite_dir": args.suite_dir,
                "config_path": args.config_path,
                "cases_path": args.cases_path
            })
        else:
            # Auto-discover all suites in cases/ folder
            cases_root = "cases"
            if os.path.exists(cases_root) and os.path.isdir(cases_root):
                for item in sorted(os.listdir(cases_root)):
                    item_path = os.path.join(cases_root, item)
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "cases.json")):
                        suites_to_run.append({
                            "suite_dir": item_path,
                            "config_path": None,
                            "cases_path": None
                        })

        if not suites_to_run:
            print("No test suites found to run.")
            return

        all_reports = []
        for s in suites_to_run:
            report = await run_suite(
                suite_dir=s["suite_dir"],
                config_path=s["config_path"],
                cases_path=s["cases_path"],
                server_url_override=args.server_url,
                timeout_s_cli=args.timeout_s,
                budget_n_results_max_cli=args.budget_n_results_max,
                print_tools_cli=args.print_tools if args.print_tools else None,
                threads_cli=args.threads,
                report_path_cli=args.report_path,
                report_detail_path_cli=args.report_detail_path,
                report_md_path_cli=args.report_md_path,
                global_config=global_config,
            )
            if report:
                all_reports.append(report)

        # Print summary of all suites
        if len(all_reports) > 1:
            print("\n" + "="*50)
            print("OVERALL SUMMARY")
            print("="*50)
            total_cases = sum(r["summary"]["total"] for r in all_reports)
            total_passed = sum(r["summary"]["passed"] for r in all_reports)
            print(f"Total Suites: {len(all_reports)}")
            print(f"Total Cases:  {total_passed}/{total_cases} passed ({(total_passed/total_cases*100):.1f}%)")
            print("="*50)

    asyncio.run(run_all())
    return 0

