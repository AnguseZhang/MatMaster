#!/usr/bin/env python3
"""
补丁后执行 graphrag（index / query 等），解决 DashScope 兼容问题：
1) DashScope embedding 的 encoding_format 必须为 "float"/"base64"
2) create_final_text_units 写 text_units.parquet 时，entity_ids 等列为 numpy array，
   PyArrow 无法推断类型导致 ArrowInvalid，需先转为 list。
3) create_community_reports 调用 chat 时，DashScope 对 json_schema 会报 400/500，改为 json_object。
4) DashScope embedding 单次 input 条数不能超过 10，需把大批次拆成每批 ≤10 再合并结果。

index 与 query 都须通过本脚本调用，否则 query 会报 encoding_format 400。

用法（在已安装 graphrag 的环境中执行）：
     python run_index_with_dashscope_fix.py index --root .
     python run_index_with_dashscope_fix.py query --root . "你的问题"
     或：python run_index_with_dashscope_fix.py index -r .
"""
import sys


def _apply_dashscope_response_format_patch():
    """DashScope 用 json_schema 易出 400/500，对 DashScope 且 Pydantic 时改用 json_object。"""
    import inspect
    import litellm
    from pydantic import BaseModel

    _orig_acompletion = litellm.acompletion

    async def _patched_acompletion(**kwargs):
        api_base = kwargs.get("api_base") or ""
        rf = kwargs.get("response_format")
        if (
            "dashscope" in str(api_base).lower()
            and rf is not None
            and inspect.isclass(rf)
            and issubclass(rf, BaseModel)
        ):
            # 仅要求返回 JSON 对象，由 graphrag 侧用 Pydantic 解析，避免 DashScope 的 Postprocessor 500
            kwargs = {**kwargs, "response_format": {"type": "json_object"}}
        return await _orig_acompletion(**kwargs)

    litellm.acompletion = _patched_acompletion


def _apply_dashscope_embedding_patch():
    from graphrag.language_model.providers.litellm import embedding_model

    _original_get_kwargs = embedding_model.LitellmEmbeddingModel._get_kwargs

    def _patched_get_kwargs(self, **kwargs):
        result = _original_get_kwargs(self, **kwargs)
        api_base = getattr(self.config, "api_base", None) or ""
        if "dashscope" in api_base:
            result["encoding_format"] = "float"
        return result

    embedding_model.LitellmEmbeddingModel._get_kwargs = _patched_get_kwargs

    # DashScope embedding 单次 input 不能超过 10 条，对 aembed_batch / embed_batch 做分批
    _orig_aembed_batch = embedding_model.LitellmEmbeddingModel.aembed_batch
    _orig_embed_batch = embedding_model.LitellmEmbeddingModel.embed_batch
    _DASHSCOPE_EMBED_BATCH_SIZE = 10

    async def _patched_aembed_batch(self, text_list, **kwargs):
        api_base = getattr(self.config, "api_base", None) or ""
        if "dashscope" not in str(api_base).lower() or len(text_list) <= _DASHSCOPE_EMBED_BATCH_SIZE:
            return await _orig_aembed_batch(self, text_list, **kwargs)
        out = []
        for i in range(0, len(text_list), _DASHSCOPE_EMBED_BATCH_SIZE):
            chunk = text_list[i : i + _DASHSCOPE_EMBED_BATCH_SIZE]
            out.extend(await _orig_aembed_batch(self, chunk, **kwargs))
        return out

    def _patched_embed_batch(self, text_list, **kwargs):
        api_base = getattr(self.config, "api_base", None) or ""
        if "dashscope" not in str(api_base).lower() or len(text_list) <= _DASHSCOPE_EMBED_BATCH_SIZE:
            return _orig_embed_batch(self, text_list, **kwargs)
        out = []
        for i in range(0, len(text_list), _DASHSCOPE_EMBED_BATCH_SIZE):
            chunk = text_list[i : i + _DASHSCOPE_EMBED_BATCH_SIZE]
            out.extend(_orig_embed_batch(self, chunk, **kwargs))
        return out

    embedding_model.LitellmEmbeddingModel.aembed_batch = _patched_aembed_batch
    embedding_model.LitellmEmbeddingModel.embed_batch = _patched_embed_batch


def _apply_text_units_parquet_patch():
    """写 text_units.parquet 前把 entity_ids/relationship_ids/covariate_ids 转为 list，避免 ArrowInvalid。"""
    import graphrag.utils.storage as storage_mod

    _original = storage_mod.write_table_to_storage

    async def _patched_write_table_to_storage(table, name, storage):
        if name == "text_units" and hasattr(table, "columns"):
            df = table.copy()
            for col in ("entity_ids", "relationship_ids", "covariate_ids"):
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: list(x) if hasattr(x, "__iter__") and not isinstance(x, (str, bytes)) else x
                    )
            table = df
        return await _original(table, name, storage)

    storage_mod.write_table_to_storage = _patched_write_table_to_storage


def apply_dashscope_patches():
    """
    应用 DashScope 兼容补丁（与 main 中一致）。
    供 context_builder 等在被 MatMaster 调用前调用，确保 query 路径与「python run_index_with_dashscope_fix.py query」一致。
    """
    _apply_dashscope_response_format_patch()
    _apply_dashscope_embedding_patch()
    _apply_text_units_parquet_patch()


def main():
    # 必须在任何 from graphrag 之前打 response_format 补丁，否则 graphrag 已缓存 litellm.acompletion
    apply_dashscope_patches()
    # 保持与 graphrag 一致：argv[0]=程序名，后面为 index --root . 等
    sys.argv = ["graphrag"] + (sys.argv[1:] or ["index", "--root", "."])
    from graphrag.cli.main import app
    app()


if __name__ == "__main__":
    main()
