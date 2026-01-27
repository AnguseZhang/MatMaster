import asyncio
import time
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client

from ..models import CaseResult, ToolCall, ToolSchema
from .oracle import check_oracle, extract_text
from .policy import repair_and_score_args


def parse_tool_schema(raw: Any) -> ToolSchema | None:
    if not isinstance(raw, dict):
        return None
    properties = raw.get("properties")
    if not isinstance(properties, dict):
        return None
    required = raw.get("required", [])
    if not isinstance(required, list):
        required = []
    required_str = [r for r in required if isinstance(r, str)]
    prop_map: dict[str, dict[str, Any]] = {}
    for k, v in properties.items():
        if isinstance(k, str) and isinstance(v, dict):
            prop_map[k] = v
    return ToolSchema(required=required_str, properties=prop_map)


async def list_tools(server_url: str, timeout_s: float) -> list[str]:
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=timeout_s)
            tools_response = await asyncio.wait_for(session.list_tools(), timeout=timeout_s)
            return [t.name for t in tools_response.tools]


async def get_tool_schema(server_url: str, tool_name: str, timeout_s: float) -> ToolSchema | None:
    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=timeout_s)
            tools_response = await asyncio.wait_for(session.list_tools(), timeout=timeout_s)
            tool = next((t for t in tools_response.tools if t.name == tool_name), None)
            if tool is None:
                return None
            raw = getattr(tool, "inputSchema", None)
            return parse_tool_schema(raw)


async def run_one_case(
    server_url: str,
    tool_call: ToolCall,
    timeout_s: float,
    *,
    tool_schema: ToolSchema | None,
    budget_n_results_max: int,
    case_id: str,
    expect: dict[str, Any] | None,
) -> CaseResult:
    start = time.perf_counter()
    args_used, policy_score, repairs, violations = repair_and_score_args(
        tool_schema,
        tool_call.args,
        budget_n_results_max=budget_n_results_max,
    )
    if violations:
        latency_ms = int((time.perf_counter() - start) * 1000)
        oracle_ok, oracle_error = check_oracle(expect=expect, error="policy_violation", output_text=None)
        return CaseResult(
            case_id=case_id,
            server_url=server_url,
            tool_name=tool_call.tool_name,
            args=tool_call.args,
            args_used=args_used,
            policy_score=policy_score,
            policy_repairs=repairs,
            policy_violations=violations,
            ok=oracle_ok,
            latency_ms=latency_ms,
            error="policy_violation",
            output_text=None,
            oracle_ok=oracle_ok,
            oracle_error=oracle_error,
        )

    try:
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await asyncio.wait_for(session.initialize(), timeout=timeout_s)
                result = await asyncio.wait_for(
                    session.call_tool(tool_call.tool_name, args_used),
                    timeout=timeout_s,
                )
                latency_ms = int((time.perf_counter() - start) * 1000)
                output_text = extract_text(result)
                oracle_ok, oracle_error = check_oracle(
                    expect=expect,
                    error=None,
                    output_text=output_text,
                )
                return CaseResult(
                    case_id=case_id,
                    server_url=server_url,
                    tool_name=tool_call.tool_name,
                    args=tool_call.args,
                    args_used=args_used,
                    policy_score=policy_score,
                    policy_repairs=repairs,
                    policy_violations=violations,
                    ok=oracle_ok,
                    latency_ms=latency_ms,
                    error=None,
                    output_text=output_text,
                    oracle_ok=oracle_ok,
                    oracle_error=oracle_error,
                )
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        err = f"{type(e).__name__}: {e}"
        oracle_ok, oracle_error = check_oracle(expect=expect, error=err, output_text=None)
        return CaseResult(
            case_id=case_id,
            server_url=server_url,
            tool_name=tool_call.tool_name,
            args=tool_call.args,
            args_used=args_used,
            policy_score=policy_score,
            policy_repairs=repairs,
            policy_violations=violations,
            ok=oracle_ok,
            latency_ms=latency_ms,
            error=err,
            output_text=None,
            oracle_ok=oracle_ok,
            oracle_error=oracle_error,
        )
