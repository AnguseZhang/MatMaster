"""
GraphRAG 上下文构建：用户查询 → 实体映射 → 上下文构建，返回 context_chunks 供 MatMaster 计划构建使用。

可被 MatMaster evaluate 或 agent 通过 sys.path 或 RAG_ROOT 导入调用。
"""
import json
import re
import time
from pathlib import Path
from typing import Optional

# GraphRAG 上下文的五部分（section 标题，不区分大小写）
CONTEXT_PART_NAMES = ("reports", "entities", "relationships", "claims", "sources")

# 预编译正则，避免热路径重复编译
_CONTEXT_PART_SPLIT = re.compile(r"\n-----")
_JSON_FUNCTION_PATTERN = re.compile(r'"function"\s*:\s*"((?:[^"\\]|\\.)*)"')
# 固定注入实体名（边补召时始终加入），用 frozenset 便于快速差集
_FIXED_ENTITY_NAMES = frozenset({
    "WEB-SEARCH", "web-search",
    "LLM_TOOL", "llm_tool",
    "EXTRACT_INFO_FROM_WEBPAGE", "extract_info_from_webpage",
    "SEARCH-PAPERS-ENHANCED", "search-papers-enhanced",
    "FILE_PARSE", "file_parse",
})


def _section_name_from_part(part: str) -> str:
    """从块的首行解析 section 名，如 \"-----Reports-----\" 或 \"Entities-----\" -> \"reports\" / \"entities\"。"""
    first_line = part.split("\n")[0].strip()
    name = first_line.strip("-").strip()
    return name.lower() if name else ""


def keep_only_context_parts(context_chunks: str, include_parts: list[str] | None) -> str:
    """
    只保留指定的部分。include_parts 为部分名列表（不区分大小写），如
    ["reports", "entities", "relationships"]；为 None 或空列表时不截断。
    可选部分名：reports, entities, relationships, claims, sources。
    """
    if not context_chunks or not context_chunks.strip():
        return context_chunks
    if not include_parts:
        return context_chunks
    want = {p.strip().lower() for p in include_parts if p and p.strip()}
    if not want:
        return context_chunks
    parts = _CONTEXT_PART_SPLIT.split(context_chunks)
    kept = []
    for part in parts:
        if not part.strip():
            continue
        name = _section_name_from_part(part)
        if name and name in want:
            kept.append(part)
    if not kept:
        return context_chunks
    return "\n-----".join(kept)


def keep_only_first_three_context_parts(context_chunks: str) -> str:
    """兼容旧接口：只保留前三部分（reports, entities, relationships）。"""
    return keep_only_context_parts(context_chunks, ["reports", "entities", "relationships"])


def parse_entity_names_from_context(context: str) -> list[str]:
    """
    从 RAG 上下文的 Entities 块中解析实体名（第二列 entity）。
    返回去重且保持顺序的列表。供 make_plan 校验 tool_name 等使用。
    """
    seen: set[str] = set()
    names: list[str] = []
    parts = _CONTEXT_PART_SPLIT.split(context)
    for part in parts:
        if not part.strip():
            continue
        name = _section_name_from_part(part)
        if name != "entities":
            continue
        lines = part.strip().split("\n")
        header_idx = None
        for i, line in enumerate(lines):
            if "|" in line and "entity" in line.lower():
                header_idx = i
                break
        if header_idx is None:
            break
        for i in range(header_idx + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            cols = line.split("|", 2)
            if len(cols) >= 2:
                entity_name = cols[1].strip()
                if entity_name and entity_name not in seen:
                    seen.add(entity_name)
                    names.append(entity_name)
        break
    return names


def entities_only_cap(
    context_chunks: str,
    max_entities: int = 20,
    sort_by_entity_name: bool = True,
) -> str:
    """
    只保留 Entities 部分，最多 max_entities 条实体数据行；不包含 Relationships（边仅用于上游补召实体）。
    sort_by_entity_name=True 时对实体行按实体名（第二列）排序后再截断，便于多次运行结果一致。
    """
    if not context_chunks or not context_chunks.strip():
        return context_chunks
    parts = _CONTEXT_PART_SPLIT.split(context_chunks)
    entities_part = None
    for p in parts:
        if not p.strip():
            continue
        name = _section_name_from_part(p)
        if name == "entities":
            entities_part = p
            break
    if not entities_part:
        return ""
    lines = entities_part.strip().split("\n")
    # 定位表头行（id|entity|description|...），其前为 section 标题如 "Entities-----"
    header_idx = None
    for i, line in enumerate(lines):
        if "|" in line and "entity" in line.lower():
            header_idx = i
            break
    if header_idx is None:
        return entities_part.strip()
    section_header = "\n".join(lines[:header_idx]) if header_idx > 0 else ""
    column_header = lines[header_idx]
    data_lines = [ln for ln in lines[header_idx + 1 :] if ln.strip()]
    if not data_lines:
        return (section_header + "\n" + column_header).strip() if section_header else column_header
    if sort_by_entity_name:
        def _entity_key(ln: str) -> str:
            cols = ln.split("|", 2)
            return (cols[1].strip() if len(cols) >= 2 else "")
        data_lines = sorted(data_lines, key=_entity_key)
    capped = data_lines[:max_entities]
    block = [section_header, column_header] if section_header else [column_header]
    block.extend(capped)
    return "\n".join(block)


def _parse_entities_block(part: str) -> tuple[str, list[str], set[str]]:
    """解析 Entities 块，返回 (首行含标题, 数据行列表, 已出现的实体名集合)。"""
    lines = part.strip().split("\n")
    if not lines:
        return "", [], set()
    header = lines[0]
    data_lines = []
    entity_names = set()
    for line in lines[1:]:
        if not line.strip():
            continue
        # 格式: id|entity|description|number of relationships，description 可能不含 |
        parts = line.split("|", 3)
        if len(parts) >= 2:
            entity_names.add(parts[1].strip())
        data_lines.append(line)
    return header, data_lines, entity_names


def _parse_relationships_block(part: str) -> tuple[str, list[str], set[str]]:
    """解析 Relationships 块，返回 (首行含标题, 数据行列表, 边上的 source/target 实体名集合)。"""
    lines = part.strip().split("\n")
    if not lines:
        return "", [], set()
    header = lines[0]
    edge_names = set()
    data_lines = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) >= 3:
            edge_names.add(parts[1].strip())
            edge_names.add(parts[2].strip())
        data_lines.append(line)
    return header, data_lines, edge_names


def _extract_first_json_object(s: str):
    """从字符串中提取第一个完整 JSON 对象（按花括号匹配），解析失败返回 None。"""
    start = s.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[start : i + 1])
                except (json.JSONDecodeError, TypeError):
                    return None
    return None


def _extract_function_from_json_like_string(s: str) -> str:
    """
    从类 JSON 字符串中尽量抽出 function 字段的纯文本。
    优先用预编译正则提取（快），失败再尝试 JSON 解析，避免整段 JSON 泄露。
    """
    if not s or not s.strip():
        return ""
    s = s.strip()
    # 快路径：正则直接提取 "function":"..."，避免重复编译与完整 JSON 解析
    m = _JSON_FUNCTION_PATTERN.search(s)
    if m:
        raw = m.group(1)
        if raw:
            return raw.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")[:500]
    # 回退：完整 JSON 解析（处理嵌套等）
    obj = _extract_first_json_object(s)
    if isinstance(obj, dict) and "function" in obj:
        fn = obj.get("function")
        if isinstance(fn, str) and fn.strip():
            return fn.strip()
        if fn is not None:
            return str(fn).strip()
    if s.startswith("{"):
        return ""
    return s[:300].strip()


def reduce_context_to_entities_function_only(context_chunks: str) -> str:
    """
    将「Entities + Relationships」上下文缩减为仅「Entities」，且每行描述只保留 JSON 中的 function 字段；
    不包含 Relationships（边）。传给 LLM 的计划上下文更精简。
    description 可能带后缀（如 )<|COMPLETE|>|0），先提取首尾匹配的 JSON 再取 function；
    解析失败时用正则抽取 function，绝不输出整段 JSON 或 applicable_tasks 等。
    """
    if not context_chunks or not context_chunks.strip():
        return context_chunks
    parts = _CONTEXT_PART_SPLIT.split(context_chunks)
    entities_part = None
    for p in parts:
        if not p.strip():
            continue
        name = _section_name_from_part(p)
        if name == "entities":
            entities_part = p
            break
    if not entities_part:
        return ""
    lines = entities_part.strip().split("\n")
    if not lines:
        return ""
    out_lines = ["Entities-----", "id|entity|function"]
    header_idx = None
    for i, line in enumerate(lines):
        if "|" in line and "entity" in line.lower():
            header_idx = i
            break
    if header_idx is None:
        return entities_part.strip()
    for line in lines[header_idx + 1 :]:
        if not line.strip():
            continue
        cols = line.split("|", 3)
        if len(cols) < 3:
            continue
        id_part = cols[0].strip()
        entity_part = cols[1].strip()
        rest = cols[2].strip()
        sub = rest.rsplit("|", 1)
        desc_str = sub[0].strip() if sub else ""
        function_text = _extract_function_from_json_like_string(desc_str)
        if not function_text:
            function_text = "(无功能描述)"
        out_lines.append(f"{id_part}|{entity_part}|{function_text}")
    return "\n".join(out_lines)


def _expand_entities_by_edges_and_drop_sources(
    context_chunks: str,
    entities_list: list,
) -> str:
    """
    根据边补召实体：从 Relationships 中出现的 source/target 里，若某实体未出现在 Entities 中，
    则从 entities_list 中补入其 description（一行 id|entity|description|0）。
    返回仅包含 Entities + Relationships 的上下文，不含 Sources（也不含 Reports/Claims，若原本有则去掉）。
    entities_list: graphrag Entity 列表，每项需有 .short_id, .title, .description。
    """
    if not context_chunks or not context_chunks.strip():
        return context_chunks
    parts = _CONTEXT_PART_SPLIT.split(context_chunks)
    entities_part = None
    relationships_part = None
    for p in parts:
        if not p.strip():
            continue
        name = _section_name_from_part(p)
        if name == "entities":
            entities_part = p
        elif name == "relationships":
            relationships_part = p
    if not entities_part or not relationships_part:
        return keep_only_context_parts(context_chunks, ["entities", "relationships"])

    entity_header, entity_data_lines, entity_names = _parse_entities_block(entities_part)
    rel_header, rel_data_lines, edge_names = _parse_relationships_block(relationships_part)
    supplemental_names = (edge_names | _FIXED_ENTITY_NAMES) - entity_names
    if not supplemental_names:
        return keep_only_context_parts(context_chunks, ["entities", "relationships"])

    by_title = {}
    for e in entities_list:
        t = getattr(e, "title", None)
        if t:
            by_title[t] = e
    supplemental_rows = []
    for name in sorted(supplemental_names):
        e = by_title.get(name)
        if e is None:
            continue
        sid = getattr(e, "short_id", e.id)
        desc = getattr(e, "description", "") or ""
        if isinstance(desc, dict):
            desc = json.dumps(desc, ensure_ascii=False)
        supplemental_rows.append(f"{sid}|{name}|{desc}|0")

    new_entity_lines = [entity_header] + entity_data_lines + supplemental_rows
    new_entities_block = "\n".join(new_entity_lines)
    new_relationships_block = "\n".join([rel_header] + rel_data_lines)
    return new_entities_block + "\n\n-----" + new_relationships_block


def warmup_graphrag_imports() -> None:
    """
    预执行 build_local_context_only 所需的全部延迟 import，使首次检索时 retrieve_imports≈0。
    在调用 build_local_context_* 前调用一次即可（如 run_make_plan 开头）。
    """
    import asyncio  # noqa: F401
    import run_index_with_dashscope_fix
    run_index_with_dashscope_fix.apply_dashscope_patches()
    from graphrag.config.load_config import load_config  # noqa: F401
    from graphrag.config.embeddings import entity_description_embedding  # noqa: F401
    from graphrag.config.models.graph_rag_config import GraphRagConfig  # noqa: F401
    from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey  # noqa: F401
    from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext  # noqa: F401
    from graphrag.query.indexer_adapters import (
        read_indexer_entities,
        read_indexer_reports,
        read_indexer_text_units,
        read_indexer_relationships,
        read_indexer_covariates,
    )  # noqa: F401
    from graphrag.utils.api import get_embedding_store, create_storage_from_config  # noqa: F401
    from graphrag.utils.storage import load_table_from_storage, storage_has_table  # noqa: F401
    from graphrag.language_model.manager import ModelManager  # noqa: F401
    from graphrag.tokenizer.get_tokenizer import get_tokenizer  # noqa: F401
    from types import MethodType  # noqa: F401
    from patch_local_context_entity_cap import (
        apply_entity_token_cap_patch,
        wrap_build_local_context,
    )  # noqa: F401
    return None


# 延迟导入，避免未装 graphrag 时 MatMaster 无法启动
def build_local_context_only(
    root_dir: Path,
    query: str,
    community_level: int | None = None,
    include_community: bool = False,
    include_parts: list[str] | None = None,
    return_entities: bool = False,
    top_k_entities: int | None = None,
    top_k_relationships: int | None = None,
    timings: dict | None = None,
):
    """
    只执行：用户查询 → 实体映射 → 上下文构建；返回 (context_chunks, context_records) 或当 return_entities=True 时为 (context_chunks, context_records, entities_list)。
    include_parts 为要保留的部分名列表；top_k_entities / top_k_relationships 若传入则覆盖 config，用于加速（取更少实体/边）。
    timings 为可选的 mutable dict，若传入则写入各子步骤用时（秒）。
    """
    t0_entry = time.perf_counter()
    import asyncio
    _t = time.perf_counter
    # 与 run_index_with_dashscope_fix 一致：在任意 graphrag 导入前打补丁
    import run_index_with_dashscope_fix
    run_index_with_dashscope_fix.apply_dashscope_patches()

    from graphrag.config.load_config import load_config
    from graphrag.config.embeddings import entity_description_embedding
    from graphrag.config.models.graph_rag_config import GraphRagConfig
    from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
    from graphrag.query.structured_search.local_search.mixed_context import (
        LocalSearchMixedContext,
    )
    from graphrag.query.indexer_adapters import (
        read_indexer_entities,
        read_indexer_reports,
        read_indexer_text_units,
        read_indexer_relationships,
        read_indexer_covariates,
    )
    from graphrag.utils.api import get_embedding_store, create_storage_from_config
    from graphrag.utils.storage import load_table_from_storage, storage_has_table
    from graphrag.language_model.manager import ModelManager
    from graphrag.tokenizer.get_tokenizer import get_tokenizer
    from types import MethodType
    from patch_local_context_entity_cap import (
        apply_entity_token_cap_patch,
        wrap_build_local_context,
    )
    if timings is not None:
        timings["retrieve_imports"] = time.perf_counter() - t0_entry

    async def _load_tables_async(storage, names):
        return await asyncio.gather(*[load_table_from_storage(name=n, storage=storage) for n in names])

    def _load_dataframes(config: GraphRagConfig):
        storage = create_storage_from_config(config.output)
        names = ["entities", "communities", "community_reports", "text_units", "relationships"]
        # 并行加载前 5 张表，加速构建上下文；asyncio.run 需传入 coroutine 不能传 Future
        tables = asyncio.run(_load_tables_async(storage, names))
        result = dict(zip(names, tables))
        result["covariates"] = None
        if asyncio.run(storage_has_table("covariates", storage)):
            result["covariates"] = asyncio.run(load_table_from_storage(name="covariates", storage=storage))
        return result

    root = Path(root_dir).resolve()
    t0 = _t()
    config = load_config(root, None, {})
    if timings is not None:
        timings["retrieve_load_config"] = _t() - t0

    t0 = _t()
    dfs = _load_dataframes(config)
    if timings is not None:
        timings["retrieve_load_dataframes"] = _t() - t0
    entities_df = dfs["entities"]
    communities_df = dfs["communities"]
    community_reports_df = dfs["community_reports"]
    text_units_df = dfs["text_units"]
    relationships_df = dfs["relationships"]
    covariates_df = dfs["covariates"]

    t0 = _t()
    vector_store_args = {k: v.model_dump() for k, v in config.vector_store.items()}
    description_embedding_store = get_embedding_store(
        config_args=vector_store_args,
        embedding_name=entity_description_embedding,
    )
    embedding_config = config.get_language_model_config(config.local_search.embedding_model_id)
    embedding_model = ModelManager().get_or_create_embedding_model(
        name="local_search_embedding",
        model_type=embedding_config.type,
        config=embedding_config,
    )
    tokenizer = get_tokenizer(model_config=config.get_language_model_config(config.local_search.chat_model_id))
    if timings is not None:
        timings["retrieve_embedding_store_and_model"] = _t() - t0

    t0 = _t()
    entities_ = read_indexer_entities(entities_df, communities_df, community_level=community_level)
    reports = read_indexer_reports(community_reports_df, communities_df, community_level=community_level)
    text_units = read_indexer_text_units(text_units_df)
    relationships = read_indexer_relationships(relationships_df)
    covariates_ = read_indexer_covariates(covariates_df) if covariates_df is not None else []
    if timings is not None:
        timings["retrieve_read_indexers"] = _t() - t0

    t0 = _t()
    ls_config = config.local_search
    context_builder = LocalSearchMixedContext(
        community_reports=reports,
        text_units=text_units,
        entities=entities_,
        relationships=relationships,
        covariates={"claims": covariates_},
        entity_text_embeddings=description_embedding_store,
        text_embedder=embedding_model,
        tokenizer=tokenizer,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,
    )
    # 实体表最多占 local_tokens 的 55%，剩余给 Relationships
    apply_entity_token_cap_patch(entity_prop=0.55)
    wrapped = wrap_build_local_context(LocalSearchMixedContext._build_local_context, entity_prop=0.55)
    context_builder._build_local_context = MethodType(wrapped, context_builder)

    community_prop = 0.0 if not include_community else ls_config.community_prop
    n_ent = top_k_entities if top_k_entities is not None else ls_config.top_k_entities
    n_rel = top_k_relationships if top_k_relationships is not None else ls_config.top_k_relationships
    context_builder_params = {
        "text_unit_prop": ls_config.text_unit_prop,
        "community_prop": community_prop,
        "conversation_history_max_turns": ls_config.conversation_history_max_turns,
        "conversation_history_user_turns_only": True,
        "top_k_mapped_entities": n_ent,
        "top_k_relationships": n_rel,
        "include_entity_rank": True,
        "include_relationship_weight": True,
        "include_community_rank": False,
        "return_candidate_context": False,
        "max_context_tokens": ls_config.max_context_tokens,
    }
    if timings is not None:
        timings["retrieve_init_mixed_context"] = _t() - t0

    t0 = _t()
    result = context_builder.build_context(query=query, **context_builder_params)
    chunks = result.context_chunks
    if timings is not None:
        timings["retrieve_build_context"] = _t() - t0
    t0 = _t()
    if include_parts:
        chunks = keep_only_context_parts(chunks, include_parts)
    if timings is not None:
        timings["retrieve_keep_parts"] = _t() - t0
    if return_entities:
        return chunks, result.context_records, entities_
    return chunks, result.context_records


def build_local_context_entities_relations_only(
    root_dir: Path,
    query: str,
    community_level: int | None = None,
    include_community: bool = False,
    top_k_entities: int | None = None,
    top_k_relationships: int | None = None,
    timings: dict | None = None,
):
    """
    仅检索实体与边，根据边补召实体，不包含 Source（也不含 Reports/Claims）。
    返回 (context_chunks, context_records)。可选 top_k_entities/top_k_relationships 减小以加速。
    timings 为可选的 mutable dict，若传入则写入各子步骤用时（含 retrieve_* 与 expand_edges）。
    """
    chunks, records, entities_list = build_local_context_only(
        root_dir,
        query,
        community_level=community_level,
        include_community=include_community,
        include_parts=["entities", "relationships"],
        return_entities=True,
        top_k_entities=top_k_entities,
        top_k_relationships=top_k_relationships,
        timings=timings,
    )
    t0 = time.perf_counter()
    chunks = _expand_entities_by_edges_and_drop_sources(chunks, entities_list)
    if timings is not None:
        timings["retrieve_expand_edges"] = time.perf_counter() - t0
    return chunks, records


def get_graphrag_context_for_query(
    query: str,
    root_dir: Optional[Path] = None,
    community_level: int | None = None,
    include_parts: list[str] | None = None,
    entities_relations_only: bool = False,
) -> Optional[str]:
    """
    对给定 query 构建 GraphRAG 上下文，返回 context_chunks 字符串；失败返回 None。
    include_parts 为要保留的部分名列表（如 ["reports","entities","relationships"]），
    可选：reports, entities, relationships, claims, sources；None 表示不截断（全部）。
    entities_relations_only=True 时：仅实体+边、按边补召实体、不含 Source，忽略 include_parts。
    """
    if not query or not query.strip():
        return None
    root = root_dir or Path(__file__).resolve().parent
    try:
        if entities_relations_only:
            chunks, _ = build_local_context_entities_relations_only(
                root, query, community_level=community_level,
            )
        else:
            chunks, _ = build_local_context_only(
                root, query,
                community_level=community_level,
                include_parts=include_parts,
            )
        return chunks if chunks else None
    except Exception:
        return None
