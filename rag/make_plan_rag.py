"""
RAG make_plan 统一入口：构建上下文、加载 prompt、调 LLM、校验。
Prompt 外置，LLM/校验走 plan_llm。
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from context_builder import (
    build_local_context_entities_relations_only,
    parse_entity_names_from_context,
    reduce_context_to_entities_function_only,
    warmup_graphrag_imports,
)
from plan_llm import call_llm, load_llm_config, validate_plan_json

# mode -> 相对项目根的 prompt 文件名
PROMPT_FILES = {
    "default": "prompts/plan_make_rag.txt",
}


def load_plan_prompt(mode: str, root_dir: Path) -> str:
    """按 mode 加载 plan-make 的 system prompt。root_dir 为项目根（含 prompts/）。"""
    name = PROMPT_FILES.get(mode)
    if not name:
        raise ValueError(f"未知 mode: {mode}，支持: {list(PROMPT_FILES)}")
    path = Path(root_dir).resolve() / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt 文件不存在: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_graphrag_context(root_dir: Path, query: str, timings: dict | None = None) -> str:
    """仅实体+边、按边补召、不含 Source；返回完整 context_chunks（Entities+Relationships）。"""
    context_chunks, _ = build_local_context_entities_relations_only(
        root_dir,
        query,
        community_level=None,
        include_community=False,
        timings=timings,
    )
    return context_chunks or ""


def _build_context_reduced(root_dir: Path, query: str, timings: dict | None) -> tuple[str, str]:
    """先检索实体+边，再缩减为仅实体 function（无边）。返回 (context_full, context_reduced)。"""
    context_full = build_graphrag_context(root_dir, query, timings)
    t0 = time.perf_counter()
    context_reduced = reduce_context_to_entities_function_only(context_full)
    if timings is not None:
        timings["2b_reduce_to_function_only"] = time.perf_counter() - t0
    return context_full, context_reduced


def build_user_message(query: str, context: str, memory_context: str = "") -> str:
    """用户消息：问题 + 可选会话记忆 + 仅实体 function 的上下文。"""
    memory_block = ""
    if memory_context and memory_context.strip():
        memory_block = f"""
<会话补充上下文>
{memory_context.strip()}
</会话补充上下文>
"""
    return f"""用户原始问题: {query}{memory_block}

以下是从知识库检索到的工具/实体列表，每行仅包含实体名与其功能描述（function）。请仅根据此处出现的实体名称与功能推断可用工具，并制定执行计划。不要使用上下文中未出现的工具名。

<知识库上下文（仅实体与功能）>
{context}
</知识库上下文>

请根据用户问题和上述上下文，制定执行计划。工具名必须来自上文 Entities 中的实体名；若无合适工具则使用 tool_name = null。"""


@dataclass
class RunResult:
    """run_make_plan_rag 的返回结果。"""
    raw_output: str
    is_valid: bool
    errors: list[str]
    parsed_data: Any
    context_entity_names: list[str]
    context: str
    timings: dict


def run_make_plan_rag(
    mode: str,
    query: str,
    root_dir: Path,
    *,
    memory_context: str = "",
    settings_path: Path | None = None,
    timings: dict | None = None,
    out_context: Path | None = None,
    out_context_full: Path | None = None,
) -> RunResult:
    """
    执行 RAG make_plan 全流程：加载配置、warmup、构建上下文、调 LLM、校验。
    mode 目前仅支持 "default"。
    若传入 timings，会写入各步耗时；若传入 out_context/out_context_full，会写入对应文件。
    """
    root_dir = Path(root_dir).resolve()
    settings_path = settings_path or root_dir / "settings.yaml"
    if timings is None:
        timings = {}

    t0 = time.perf_counter()
    llm_config = load_llm_config(settings_path)
    timings["1_load_llm_config"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    warmup_graphrag_imports()
    timings["1b_warmup_imports"] = time.perf_counter() - t0

    if mode == "default":
        t0 = time.perf_counter()
        context_full, context = _build_context_reduced(root_dir, query, timings)
        timings["2a_build_context"] = time.perf_counter() - t0
        if out_context_full:
            out_context_full.parent.mkdir(parents=True, exist_ok=True)
            out_context_full.write_text(context_full, encoding="utf-8")
        if out_context:
            out_context.parent.mkdir(parents=True, exist_ok=True)
            out_context.write_text(context, encoding="utf-8")
    else:
        raise ValueError(f"未知 mode: {mode}")

    if not context or not context.strip():
        raise RuntimeError("RAG 上下文为空，请检查 --root 与知识库。")

    t0 = time.perf_counter()
    context_entity_names = parse_entity_names_from_context(context)
    timings["3_parse_entities"] = time.perf_counter() - t0

    system_prompt = load_plan_prompt(mode, root_dir)
    user_message = build_user_message(query, context, memory_context=memory_context)
    timings["4_build_message"] = 0.0  # 可忽略

    t0 = time.perf_counter()
    raw_output = call_llm(system_prompt, user_message, llm_config)
    timings["5_call_llm"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    is_valid, errors, parsed_data = validate_plan_json(raw_output, context_entity_names)
    timings["6_validate_json"] = time.perf_counter() - t0

    return RunResult(
        raw_output=raw_output,
        is_valid=is_valid,
        errors=errors,
        parsed_data=parsed_data,
        context_entity_names=context_entity_names,
        context=context,
        timings=timings,
    )
