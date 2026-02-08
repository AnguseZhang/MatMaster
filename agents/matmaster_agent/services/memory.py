"""
HTTP client for the remote MatMaster memory service (FastAPI).

Provides: memory_write, memory_retrieve, memory_list, format_short_term_memory (all async).
Base URL is from constant (101.126.90.82:8002); scripts can override via base_url.
Timeouts: connect 3s, read 10s.
"""

import logging
from typing import Any, Optional

import aiohttp

from agents.matmaster_agent.constant import MEMORY_SERVICE_URL

logger = logging.getLogger(__name__)

_CONNECT_TIMEOUT = 3
_READ_TIMEOUT = 10
_MEMORY_PATH = '/api/v1/memory'


def _base(base_url: Optional[str] = None) -> str:
    url = (base_url or MEMORY_SERVICE_URL).strip()
    if not url.startswith('http'):
        url = f'http://{url}'
    return url.rstrip('/')


async def memory_write(
    session_id: str,
    text: str,
    metadata: Optional[dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> None:
    """Write one insight to the memory service for the given session."""
    payload = {
        'session_id': session_id,
        'text': text,
        'metadata': metadata or {},
    }
    try:
        timeout = aiohttp.ClientTimeout(
            connect=_CONNECT_TIMEOUT,
            total=_CONNECT_TIMEOUT + _READ_TIMEOUT,
        )
        async with aiohttp.ClientSession(timeout=timeout) as client:
            async with client.post(
                f'{_base(base_url)}{_MEMORY_PATH}/write',
                json=payload,
            ) as r:
                r.raise_for_status()
    except Exception as e:
        logger.warning('memory_write failed: %s', e)


async def memory_retrieve(
    session_id: str,
    query: str,
    limit: int = 10,
    base_url: Optional[str] = None,
) -> list[str]:
    """Retrieve relevant memory texts for the session and query. Returns list of text snippets."""
    payload = {
        'session_id': session_id,
        'query_text': query,
        'n_results': limit,
    }
    try:
        timeout = aiohttp.ClientTimeout(
            connect=_CONNECT_TIMEOUT,
            total=_CONNECT_TIMEOUT + _READ_TIMEOUT,
        )
        async with aiohttp.ClientSession(timeout=timeout) as client:
            async with client.post(
                f'{_base(base_url)}{_MEMORY_PATH}/retrieve',
                json=payload,
            ) as r:
                r.raise_for_status()
                data = await r.json()
        docs = data.get('data') or []
        if not isinstance(docs, list):
            return []
        return [
            (
                (d.get('document') or d.get('text') or '')
                if isinstance(d, dict)
                else str(d)
            )
            for d in docs
        ]
    except Exception as e:
        logger.debug('memory_retrieve failed: %s', e)
        return []


async def memory_list(
    session_id: Optional[str] = None,
    limit: Optional[int] = None,
    base_url: Optional[str] = None,
) -> list[dict[str, Any]]:
    """List stored documents (POST body). Server returns {data: [{id, document, metadata}, ...]}."""
    payload: dict[str, Any] = {}
    if session_id is not None:
        payload['session_id'] = session_id
    if limit is not None:
        payload['limit'] = limit
    try:
        timeout = aiohttp.ClientTimeout(
            connect=_CONNECT_TIMEOUT,
            total=_CONNECT_TIMEOUT + _READ_TIMEOUT,
        )
        async with aiohttp.ClientSession(timeout=timeout) as client:
            async with client.post(
                f'{_base(base_url)}{_MEMORY_PATH}/list',
                json=payload,
            ) as r:
                r.raise_for_status()
                data = await r.json()
        raw = data.get('data')
        if not isinstance(raw, list):
            return []
        return [
            (
                {
                    'id': d.get('id'),
                    'document': d.get('document', d.get('text', '')),
                    'metadata': d.get('metadata', {}),
                }
                if isinstance(d, dict)
                else d
            )
            for d in raw
        ]
    except Exception as e:
        logger.warning('memory_list failed: %s', e)
        return []


async def format_short_term_memory(
    query_text: str,
    session_id: str,
    base_url: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Retrieve session memory for the given query and format as a single block
    for injection into prompts. Returns empty string if no memory or on error.
    """
    texts = await memory_retrieve(
        session_id=session_id,
        query=query_text or 'general',
        limit=limit,
        base_url=base_url,
    )
    if not texts:
        return ''
    lines = [f'- {t.strip()}' for t in texts if (t and isinstance(t, str))]
    if not lines:
        return ''
    return 'Session Memory (relevant):\n' + '\n'.join(lines)
