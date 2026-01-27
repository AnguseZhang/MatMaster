from typing import Any

from ..models import ToolSchema


def repair_and_score_args(
    tool_schema: ToolSchema | None,
    original_args: dict[str, Any],
    *,
    budget_n_results_max: int,
) -> tuple[dict[str, Any], int, list[dict[str, Any]], list[dict[str, Any]]]:
    args_used = dict(original_args)
    repairs: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    penalty = 0

    if tool_schema is None:
        violations.append(
            {
                "type": "schema_missing",
                "message": "tool input schema not available; skip validation",
            }
        )
        return args_used, 60, repairs, violations

    allowed_keys = set(tool_schema.properties.keys())
    unknown_keys = [k for k in list(args_used.keys()) if k not in allowed_keys]
    for k in unknown_keys:
        old = args_used.pop(k, None)
        repairs.append({"type": "drop_unknown", "field": k, "from": old, "to": None})
        penalty += 5

    for name in tool_schema.required:
        if name not in args_used or args_used.get(name) in (None, ""):
            default_available = (
                name in tool_schema.properties and "default" in tool_schema.properties[name]
            )
            if default_available:
                default = tool_schema.properties[name].get("default")
                args_used[name] = default
                repairs.append({"type": "fill_required_default", "field": name, "to": default})
                penalty += 10
            else:
                violations.append(
                    {
                        "type": "missing_required",
                        "field": name,
                    }
                )

    if "n_results" in args_used:
        try:
            n = int(args_used["n_results"])
            if n < 1:
                repairs.append({"type": "clip_min", "field": "n_results", "from": n, "to": 1})
                args_used["n_results"] = 1
                penalty += 10
            if n > budget_n_results_max:
                repairs.append(
                    {
                        "type": "clip_max_budget",
                        "field": "n_results",
                        "from": n,
                        "to": budget_n_results_max,
                    }
                )
                args_used["n_results"] = budget_n_results_max
                penalty += 10
        except Exception:
            violations.append({"type": "type_error", "field": "n_results"})

    if "output_formats" in args_used:
        of = args_used.get("output_formats")
        if isinstance(of, str):
            normalized = [s.strip() for s in of.split(",") if s.strip()]
            repairs.append({"type": "coerce_array", "field": "output_formats", "from": of, "to": normalized})
            args_used["output_formats"] = normalized
            penalty += 5
        elif isinstance(of, list):
            normalized = [x for x in of if isinstance(x, str) and x.strip()]
            if normalized != of:
                repairs.append({"type": "filter_array", "field": "output_formats", "from": of, "to": normalized})
                args_used["output_formats"] = normalized
                penalty += 5

        prop = tool_schema.properties.get("output_formats")
        if isinstance(prop, dict) and prop.get("type") == "array":
            allowed = None
            items = prop.get("items")
            if isinstance(items, dict) and isinstance(items.get("enum"), list):
                allowed = [x for x in items.get("enum") if isinstance(x, str)]
            if allowed is not None and isinstance(args_used.get("output_formats"), list):
                current = args_used["output_formats"]
                filtered = [x for x in current if x in allowed]
                if filtered != current:
                    if filtered:
                        repairs.append(
                            {
                                "type": "filter_enum",
                                "field": "output_formats",
                                "from": current,
                                "to": filtered,
                            }
                        )
                        args_used["output_formats"] = filtered
                        penalty += 15
                    else:
                        default = prop.get("default")
                        if not default and allowed:
                            default = [allowed[0]]
                        if default:
                            repairs.append(
                                {
                                    "type": "fallback_default",
                                    "field": "output_formats",
                                    "from": current,
                                    "to": default,
                                }
                            )
                            args_used["output_formats"] = default
                            penalty += 15
                        else:
                            violations.append({"type": "invalid_enum", "field": "output_formats"})

    return args_used, max(0, 100 - penalty), repairs, violations
