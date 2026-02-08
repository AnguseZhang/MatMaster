"""
Mock-write data to MatMaster session memory via the memory FastAPI service.

Uses agents.matmaster_agent.services.memory (same HTTP client as agent).
Default URL: 101.126.90.82:8002 (constant); override with --url.

Usage (from project root):
    uv run python scripts/save_memory_data.py --session mock-session-1 --content "user prefers DPA for relaxation"
    uv run python scripts/save_memory_data.py --session s1 --count 5
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
from agents.matmaster_agent.services.memory import memory_write  # noqa: E402

MOCK_DOC_TEMPLATE = 'mock insight #{n}: session_id={sid} (for testing read_memory_data)'


async def main() -> None:
    parser = argparse.ArgumentParser(
        description='Mock-write MatMaster session memory via the memory FastAPI service'
    )
    parser.add_argument(
        '--url',
        default=MEMORY_SERVICE_URL,
        help=f'Memory service host:port (default: {MEMORY_SERVICE_URL})',
    )
    parser.add_argument(
        '--session',
        required=True,
        help='session_id to attach to written documents',
    )
    parser.add_argument(
        '--content',
        default=None,
        help='Single document text to write (default: use --count mock docs)',
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='When --content not set, number of mock documents to write (default: 1)',
    )
    args = parser.parse_args()

    if args.content is not None:
        texts = [args.content]
    else:
        n = max(1, args.count)
        texts = [MOCK_DOC_TEMPLATE.format(n=i + 1, sid=args.session) for i in range(n)]

    t0 = time.perf_counter()
    for text in texts:
        memory_write(
            session_id=args.session,
            text=text,
            metadata={},
            base_url=args.url,
        )
    elapsed = time.perf_counter() - t0
    print(f'[timer] save: {elapsed:.3f} s')
    print(f'Wrote {len(texts)} document(s) to session_id={args.session!r}')
    for i, doc in enumerate(texts):
        preview = doc[:80] + '...' if len(doc) > 80 else doc
        print(f'  {i + 1}. document={preview!r}')


if __name__ == '__main__':
    asyncio.run(main())
