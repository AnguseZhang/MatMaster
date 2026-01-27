import json
from typing import Any

from ..models import SuiteCase


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_suite_cases(raw: Any) -> list[SuiteCase]:
    if isinstance(raw, dict) and isinstance(raw.get("cases"), list):
        items = raw["cases"]
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError("cases.json must be a list or an object with cases")

    cases: list[SuiteCase] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("case item must be object")
        case_id = item.get("case_id")
        tool_name = item.get("tool_name")
        args = item.get("args")
        expect = item.get("expect")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("case_id must be string")
        if not isinstance(tool_name, str) or not tool_name:
            raise ValueError("tool_name must be string")
        if not isinstance(args, dict):
            raise ValueError("args must be object")
        if expect is not None and not isinstance(expect, dict):
            raise ValueError("expect must be object")
        cases.append(SuiteCase(case_id=case_id, tool_name=tool_name, args=args, expect=expect))
    return cases
