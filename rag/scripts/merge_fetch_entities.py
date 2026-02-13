#!/usr/bin/env python3
"""
将 RAG output 中 6 个 FETCH_* 实体合并为 FETCH_STRUCTURES_FROM_DB，
并合并 relationships 中涉及这 6 个的边为统一指向/来自 FETCH_STRUCTURES_FROM_DB 的边。

用法（在 MatMaster-test 或 rag 目录下）：
  python rag/scripts/merge_fetch_entities.py
  或 cd rag && python scripts/merge_fetch_entities.py
"""
from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd

# rag/scripts/merge_fetch_entities.py -> rag/output
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
ENTITIES_PATH = OUTPUT_DIR / "entities.parquet"
RELATIONSHIPS_PATH = OUTPUT_DIR / "relationships.parquet"

FETCH_OLD = [
    "FETCH_BOHRIUM_CRYSTALS",
    "FETCH_MOFS_SQL",
    "FETCH_OPENLAM_STRUCTURES",
    "FETCH_STRUCTURES_WITH_BANDGAP",
    "FETCH_STRUCTURES_WITH_FILTER",
    "FETCH_STRUCTURES_WITH_SPG",
]
FETCH_NEW = "FETCH_STRUCTURES_FROM_DB"

# 与 tools.py / structure_search_agent.prompt 中 StructureSearchAgentToolDescription 一致，保持简短
FETCH_STRUCTURES_FROM_DB_DESCRIPTION = (
    "What it does: Retrieve structures across multiple sources (BohriumPublic / OpenLAM / OPTIMADE providers) and run advanced SQL queries on MOFdb. "
    "When to use: Any \"find crystal structures\" request, including formula/elements/space group/band gap filters, time/energy filters (OpenLAM), cross-provider searches (OPTIMADE), or MOF-specific analytics (MOFdb SQL). "
    "Prerequisites / Inputs: Provide either structured filters (formula/elements/space group ranges), OpenLAM filters (energy/time), OPTIMADE filter strings, or MOFdb SQL. "
    "Outputs: Structures or metadata in CIF/JSON; MOFdb returns SQL rows and optional structure file links. "
    "Cannot do / Limits: OPTIMADE filters must follow the standard grammar; MOFdb is MOF-specific; OpenLAM does not provide space group/band gap. "
    "Cost / Notes: Default to BohriumPublic for speed; use OPTIMADE for flexible/cross-provider retrieval; use MOFdb for complex MOF analytics."
)


def main() -> None:
    if not ENTITIES_PATH.exists():
        raise FileNotFoundError(f"entities not found: {ENTITIES_PATH}")
    if not RELATIONSHIPS_PATH.exists():
        raise FileNotFoundError(f"relationships not found: {RELATIONSHIPS_PATH}")

    # ---- entities ----
    e = pd.read_parquet(ENTITIES_PATH)
    fetch_mask = e["title"].isin(FETCH_OLD)
    fetch_rows = e[fetch_mask]
    if len(fetch_rows) > 0:
        other_entities = e[~fetch_mask]
        new_id = str(uuid.uuid4())
        new_hr_id = int(e["human_readable_id"].max()) + 1 if len(e) else 0
        tu_ids = fetch_rows["text_unit_ids"].dropna()
        if len(tu_ids) and hasattr(tu_ids.iloc[0], "__iter__") and not isinstance(tu_ids.iloc[0], str):
            all_tu = []
            for x in tu_ids:
                all_tu.extend(x if x is not None else [])
            merged_tu_ids = list(dict.fromkeys(all_tu))
        else:
            merged_tu_ids = tu_ids.astype(str).str.cat(sep=",").split(",") if len(tu_ids) else []
            merged_tu_ids = [x.strip() for x in merged_tu_ids if x.strip()]
        merged_row = pd.DataFrame(
            [
                {
                    "id": new_id,
                    "human_readable_id": new_hr_id,
                    "title": FETCH_NEW,
                    "type": fetch_rows["type"].iloc[0],
                    "description": FETCH_STRUCTURES_FROM_DB_DESCRIPTION,
                    "text_unit_ids": merged_tu_ids if merged_tu_ids else None,
                    "frequency": int(fetch_rows["frequency"].sum()),
                    "degree": int(fetch_rows["degree"].sum()),
                    "x": float(fetch_rows["x"].mean()),
                    "y": float(fetch_rows["y"].mean()),
                }
            ]
        )
        entities_new = pd.concat([other_entities, merged_row], ignore_index=True)
        entities_new.to_parquet(ENTITIES_PATH, index=False)
        print(f"entities: 已删除 6 个 FETCH_*，新增 1 个 {FETCH_NEW}，当前共 {len(entities_new)} 条")
    else:
        print("entities: 未发现 6 个 FETCH_*，跳过合并")

    # 确保 FETCH_STRUCTURES_FROM_DB 的 description 为简短版（与 tools.py 一致）
    e2 = pd.read_parquet(ENTITIES_PATH)
    idx = e2["title"] == FETCH_NEW
    if idx.any():
        e2.loc[idx, "description"] = FETCH_STRUCTURES_FROM_DB_DESCRIPTION
        e2.to_parquet(ENTITIES_PATH, index=False)
        print(f"entities: 已把 {FETCH_NEW} 的 description 设为 tools.py 简短描述")

    # ---- relationships ----
    r = pd.read_parquet(RELATIONSHIPS_PATH)
    if r["source"].isin(FETCH_OLD).any() or r["target"].isin(FETCH_OLD).any():
        r = r.copy()
        r["source"] = r["source"].replace(FETCH_OLD, FETCH_NEW)
        r["target"] = r["target"].replace(FETCH_OLD, FETCH_NEW)
        agg = {
            "id": "first",
            "human_readable_id": "first",
            "description": lambda s: " | ".join(s.dropna().astype(str).unique()) if s.notna().any() else None,
            "weight": "sum",
            "combined_degree": "max",
            "text_unit_ids": "first",
        }
        rel_merged = r.groupby(["source", "target"], as_index=False).agg(agg)
        rel_merged = rel_merged[list(r.columns)]
        rel_merged.to_parquet(RELATIONSHIPS_PATH, index=False)
        print(f"relationships: 已合并边，当前共 {len(rel_merged)} 条")
    else:
        print("relationships: 未发现 6 个 FETCH_*，跳过合并")

    # ---- output 下 .txt / .md 中的边名统一替换为 FETCH_STRUCTURES_FROM_DB ----
    for path in OUTPUT_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in (".txt", ".md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            new_text = text
            for old in FETCH_OLD:
                new_text = new_text.replace(old, FETCH_NEW)
            if new_text != text:
                path.write_text(new_text, encoding="utf-8")
                print(f"  已替换边名: {path.relative_to(OUTPUT_DIR)}")
    print("done.")


if __name__ == "__main__":
    main()
