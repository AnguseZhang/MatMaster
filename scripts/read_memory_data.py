"""
Read and print MatMaster session memory via the memory HTTP service.

Requires: memory service running (uv run uvicorn memory_service.main:app --host 0.0.0.0 --port 8002)
Uses MEMORY_SERVICE_URL (default 127.0.0.1:8002).

Usage (from project root):
    uv run python scripts/read_memory_data.py
    uv run python scripts/read_memory_data.py --session <session_id>
    uv run python scripts/read_memory_data.py --limit 100
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Ensure project root is on path when running script directly
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import requests  # noqa: E402

SESSION_ID_METADATA_KEY = 'session_id'
DEFAULT_MEMORY_SERVICE_URL = os.environ.get('MEMORY_SERVICE_URL', '127.0.0.1:8002')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Read MatMaster session memory via the memory HTTP service'
    )
    parser.add_argument(
        '--url',
        default=DEFAULT_MEMORY_SERVICE_URL,
        help=f'Memory service base URL host:port (default: {DEFAULT_MEMORY_SERVICE_URL})',
    )
    parser.add_argument(
        '--session',
        default=None,
        help='Only show documents for this session_id',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Max number of documents to print (default: all)',
    )
    args = parser.parse_args()

    base_url = args.url if '://' in args.url else f'http://{args.url}'
    list_endpoint = f'{base_url.rstrip("/")}/api/v1/memory/list'

    t0 = time.perf_counter()
    try:
        resp = requests.post(
            list_endpoint,
            json={
                'session_id': args.session,
                'limit': args.limit,
            },
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        print(f'Request failed: {e}')
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(e.response.text)
            except Exception:
                pass
        sys.exit(1)

    elapsed = time.perf_counter() - t0
    print(f'[timer] read: {elapsed:.3f} s')
    print()

    data = payload.get('data', [])
    if not data:
        print('No documents in collection.')
        if args.session:
            print(f'(filtered by session_id={args.session!r})')
        return

    print(f'Total documents: {len(data)}')
    if args.session:
        print(f'Filtered by session_id: {args.session!r}')
    print()

    # Group by session_id for readability
    by_session: dict[str, list[dict]] = {}
    for item in data:
        meta = item.get('metadata', {})
        sid = meta.get(SESSION_ID_METADATA_KEY, '<no session_id>')
        by_session.setdefault(sid, []).append(item)

    for session_id, items in sorted(by_session.items()):
        print(f'--- session_id: {session_id} ({len(items)} item(s)) ---')
        for it in items:
            doc_id = it.get('id', '')
            doc = it.get('document', '')
            meta = it.get('metadata', {})
            print(f'  id: {doc_id}')
            print(f'  document: {doc[:200]}{"..." if len(doc) > 200 else ""}')
            extra = {k: v for k, v in meta.items() if k != SESSION_ID_METADATA_KEY}
            if extra:
                print(f'  metadata: {extra}')
            print()
        print()


if __name__ == '__main__':
    main()
