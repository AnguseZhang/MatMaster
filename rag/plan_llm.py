"""
Plan 相关 LLM 与校验：供 make_plan 统一复用。
- load_llm_config: 从 settings.yaml 读 default_chat_model
- call_llm: 调用大模型（litellm 或 openai）
- validate_plan_json: 校验 plan JSON 并规范 tool_name
"""
import json
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import find_dotenv, load_dotenv


def _resolve_env_value(raw_value: Any) -> str:
    """
    Resolve config values that may reference environment variables.
    Supports:
    - ${VAR_NAME}
    - plain string (returned as-is)
    """
    value = "" if raw_value is None else str(raw_value).strip()
    if value.startswith("${") and value.endswith("}") and len(value) > 3:
        env_name = value[2:-1].strip()
        return os.getenv(env_name, "").strip()
    return value


def load_llm_config(settings_path: Path) -> dict:
    """从 settings.yaml 读取 default_chat_model 配置。"""
    # Ensure .env is available for local runs (prefer project/root .env if exists)
    load_dotenv(find_dotenv(), override=False)

    with open(settings_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)
    chat_cfg = settings["models"]["default_chat_model"]
    api_key = _resolve_env_value(chat_cfg.get("api_key"))
    api_base = _resolve_env_value(chat_cfg.get("api_base"))
    model = _resolve_env_value(chat_cfg.get("model"))
    if not api_key:
        raise ValueError(
            "default_chat_model.api_key is empty. "
            "Please set PLAN_MAKE_API_KEY in .env or provide api_key in settings.yaml."
        )
    return {
        "api_key": api_key,
        "api_base": api_base,
        "model": model,
    }


def call_llm(
    prompt: str,
    user_query: str,
    llm_config: dict,
) -> str:
    """使用 litellm 或 openai 调用大模型（OpenAI 兼容接口）。"""
    try:
        from litellm import completion
    except ImportError:
        import openai

        client = openai.OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["api_base"],
        )
        response = client.chat.completions.create(
            model=llm_config["model"],
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0,
        )
        return response.choices[0].message.content

    model = llm_config["model"]
    if not model.startswith(("openai/", "azure/", "litellm_proxy/")):
        model = f"openai/{model}"
    response = completion(
        model=model,
        api_key=llm_config["api_key"],
        api_base=llm_config["api_base"],
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def validate_plan_json(raw_output: str, valid_tool_names: list[str]) -> tuple[bool, list[str], Any]:
    """
    校验 LLM 输出的 plan JSON：
    - 存在 plans 字段，每个 plan 有 steps
    - 每个 step 的 tool_name 在 valid_tool_names 中或为 null，status == "plan"
    返回 (is_valid, errors, parsed_json)；校验时会把 step["tool_name"] 规范为 canonical 名。
    """
    errors = []
    text = raw_output.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start_idx = 1 if lines[0].startswith("```") else 0
        end_idx = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[start_idx:end_idx])

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return False, [f"JSON 解析失败: {e}"], None

    if "plans" not in data:
        errors.append("缺少 'plans' 字段")
        return False, errors, data

    plans = data["plans"]
    if not isinstance(plans, list):
        errors.append("'plans' 不是列表")
        return False, errors, data

    if len(plans) == 0:
        errors.append("'plans' 列表为空")

    lower_to_canonical = {t.lower(): t for t in valid_tool_names}

    for i, plan in enumerate(plans):
        plan_id = plan.get("plan_id", f"plan_{i}")
        if "steps" not in plan:
            errors.append(f"Plan '{plan_id}' 缺少 'steps' 字段")
            continue
        steps = plan["steps"]
        if not isinstance(steps, list):
            errors.append(f"Plan '{plan_id}' 的 'steps' 不是列表")
            continue
        for j, step in enumerate(steps):
            step_desc = f"Plan '{plan_id}' Step {j + 1}"
            tool_name = step.get("tool_name")
            if tool_name is not None:
                tool_lower = tool_name.lower()
                if tool_lower not in lower_to_canonical:
                    errors.append(f"{step_desc}: tool_name '{tool_name}' 不在可用工具列表中")
                else:
                    step["tool_name"] = lower_to_canonical[tool_lower]
            status = step.get("status")
            if status != "plan":
                errors.append(f"{step_desc}: status 应为 'plan'，实际为 '{status}'")
            if "description" not in step:
                errors.append(f"{step_desc}: 缺少 'description' 字段")

    return len(errors) == 0, errors, data
