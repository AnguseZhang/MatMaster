"""
Read and print MatMaster session memory via the memory FastAPI service.

Uses agents.matmaster_agent.services.memory (same HTTP client as agent).
Default URL: 101.126.90.82:8002 (constant); override with --url.

Usage (from project root):
    uv run python scripts/read_memory_data.py
    uv run python scripts/read_memory_data.py --session <session_id>
    uv run python scripts/read_memory_data.py --limit 100
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is on path when running script directly
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agents.matmaster_agent.constant import MEMORY_SERVICE_URL  # noqa: E402
from agents.matmaster_agent.services.memory import memory_list  # noqa: E402

SESSION_ID_METADATA_KEY = 'session_id'


async def main() -> None:
    parser = argparse.ArgumentParser(
        description='Read MatMaster session memory via the memory FastAPI service'
    )
    parser.add_argument(
        '--url',
        default=MEMORY_SERVICE_URL,
        help=f'Memory service host:port (default: {MEMORY_SERVICE_URL})',
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

    t0 = time.perf_counter()
    data = memory_list(
        session_id=args.session,
        limit=args.limit,
        base_url=args.url,
    )
    elapsed = time.perf_counter() - t0
    print(f'[timer] read: {elapsed:.3f} s')
    print()

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
    asyncio.run(main())
