from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    tool_name: str
    args: dict[str, Any]


@dataclass
class SuiteCase:
    case_id: str
    tool_name: str
    args: dict[str, Any]
    expect: dict[str, Any] | None


@dataclass
class CaseResult:
    case_id: str
    server_url: str
    tool_name: str
    args: dict[str, Any]
    args_used: dict[str, Any]
    policy_score: int
    policy_repairs: list[dict[str, Any]]
    policy_violations: list[dict[str, Any]]
    ok: bool
    latency_ms: int
    error: str | None
    output_text: str | None
    oracle_ok: bool
    oracle_error: str | None


@dataclass
class ToolSchema:
    required: list[str]
    properties: dict[str, dict[str, Any]]
