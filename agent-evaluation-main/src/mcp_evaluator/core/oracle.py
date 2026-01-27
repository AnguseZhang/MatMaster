import json
from typing import Any


def extract_text(result: Any) -> str | None:
    content = getattr(result, "content", None)
    if not content:
        return None
    parts: list[str] = []
    for item in content:
        text = getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(parts) if parts else None


def try_parse_json(text: str | None) -> Any | None:
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def check_oracle(
    *,
    expect: dict[str, Any] | None,
    error: str | None,
    output_text: str | None,
) -> tuple[bool, str | None]:
    if expect is None:
        return True, None

    kind = expect.get("kind")
    if kind == "policy_violation":
        ok = error == "policy_violation"
        return ok, None if ok else "expected policy_violation"

    if error is not None:
        return False, error

    if kind == "any":
        return True, None

    if kind == "text_in":
        values = expect.get("values")
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
            return False, "invalid oracle: values"
        if not isinstance(output_text, str):
            return False, "missing output_text"
        ok = output_text.strip() in values
        return ok, None if ok else f"text not in allowed values: {output_text.strip()}"

    if kind == "text_contains":
        needle = expect.get("text")
        if not isinstance(needle, str):
            return False, "invalid oracle: text"
        if not isinstance(output_text, str):
            return False, "missing output_text"
        ok = needle in output_text
        return ok, None if ok else f"text not contains: {needle}"

    if kind == "json":
        parsed = try_parse_json(output_text)
        if parsed is None:
            return False, "output not valid json"
        equals = expect.get("equals")
        if isinstance(equals, dict) and isinstance(parsed, dict):
            for k, v in equals.items():
                if parsed.get(k) != v:
                    return False, f"json field mismatch: {k}"
        must_have = expect.get("must_have")
        if isinstance(must_have, list) and isinstance(parsed, dict):
            for k in must_have:
                if isinstance(k, str) and k not in parsed:
                    return False, f"json missing key: {k}"
        return True, None

    return False, f"unknown oracle kind: {kind}"
