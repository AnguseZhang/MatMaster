"""
为 local 上下文中的「实体表」和「关系表」设置 token 上限，保证裁剪后仍保留 Entities + Relationships + Sources。

GraphRAG 的 mixed_context 在 import 时绑定了 build_entity_context / build_relationship_context，
所以必须同时 patch local_context 与 mixed_context 两个模块，调用方才会用到 capped 版本。
"""
import graphrag.query.context_builder.local_context as _local_context
import graphrag.query.structured_search.local_search.mixed_context as _mixed_context

_ENTITY_TOKEN_CAP_ATTR = "_entity_token_cap_for_relationships"
_RELATIONSHIP_TOKEN_CAP_ATTR = "_relationship_token_cap"

# 原始函数
_orig_build_entity_context = _local_context.build_entity_context
_orig_build_relationship_context = _local_context.build_relationship_context


# 默认实体占比（当 per-call cap 未设置时仍为 Relationships 预留空间）
_DEFAULT_ENTITY_PROP = 0.50
_DEFAULT_RELATIONSHIP_PROP = 0.50


def _build_entity_context_capped(*args, max_context_tokens=8000, **kwargs):
    cap = getattr(_local_context, _ENTITY_TOKEN_CAP_ATTR, None)
    if cap is not None:
        max_context_tokens = min(max_context_tokens, cap)
    else:
        # 未设置 cap 时也强制上限，避免实体占满导致 Relationships 被 revert 掉
        max_context_tokens = max(1, int(max_context_tokens * _DEFAULT_ENTITY_PROP))
    return _orig_build_entity_context(*args, max_context_tokens=max_context_tokens, **kwargs)


def _build_relationship_context_capped(*args, max_context_tokens=8000, **kwargs):
    cap = getattr(_local_context, _RELATIONSHIP_TOKEN_CAP_ATTR, None)
    if cap is not None:
        max_context_tokens = min(max_context_tokens, cap)
    else:
        max_context_tokens = max(1, int(max_context_tokens * _DEFAULT_RELATIONSHIP_PROP))
    return _orig_build_relationship_context(*args, max_context_tokens=max_context_tokens, **kwargs)


def apply_entity_token_cap_patch(entity_prop: float = 0.55):
    """应用补丁：实体表与关系表分别限制 token；同时 patch 调用方 mixed_context。"""
    _local_context.build_entity_context = _build_entity_context_capped
    _local_context.build_relationship_context = _build_relationship_context_capped
    _mixed_context.build_entity_context = _build_entity_context_capped
    _mixed_context.build_relationship_context = _build_relationship_context_capped


def revert_entity_token_cap_patch():
    """恢复原始函数。"""
    _local_context.build_entity_context = _orig_build_entity_context
    _local_context.build_relationship_context = _orig_build_relationship_context
    _mixed_context.build_entity_context = _orig_build_entity_context
    _mixed_context.build_relationship_context = _orig_build_relationship_context


def set_entity_token_cap_for_this_call(cap: int | None):
    """在本次 _build_local_context 调用中，限制实体表 token 上限。"""
    setattr(_local_context, _ENTITY_TOKEN_CAP_ATTR, cap)


def set_relationship_token_cap_for_this_call(cap: int | None):
    """在本次 _build_local_context 调用中，限制关系表 token 上限。"""
    setattr(_local_context, _RELATIONSHIP_TOKEN_CAP_ATTR, cap)


def clear_entity_token_cap():
    setattr(_local_context, _ENTITY_TOKEN_CAP_ATTR, None)


def clear_relationship_token_cap():
    setattr(_local_context, _RELATIONSHIP_TOKEN_CAP_ATTR, None)


def wrap_build_local_context(original_build_local_context, entity_prop: float = 0.55):
    """返回包装后的 _build_local_context：在调用原方法前设置实体/关系 token 上限，调用后清除。"""

    def wrapped(self, selected_entities, max_context_tokens=8000, **kwargs):
        entity_cap = max(1, int(max_context_tokens * entity_prop))
        relationship_cap = max(1, int(max_context_tokens * (1.0 - entity_prop)))  # 剩余给关系
        set_entity_token_cap_for_this_call(entity_cap)
        set_relationship_token_cap_for_this_call(relationship_cap)
        try:
            return original_build_local_context(
                self, selected_entities=selected_entities, max_context_tokens=max_context_tokens, **kwargs
            )
        finally:
            clear_entity_token_cap()
            clear_relationship_token_cap()

    return wrapped


# 模块加载时即应用补丁，确保任何使用 mixed_context 的代码都能用到 capped 版本
apply_entity_token_cap_patch(0.55)
