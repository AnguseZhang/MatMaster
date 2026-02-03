"""
Mock-write data to MatMaster session memory via the memory HTTP service.

Requires: memory service running (uv run uvicorn memory_service.main:app --host 0.0.0.0 --port 8002)
Uses MEMORY_SERVICE_URL (default 127.0.0.1:8002).

Usage (from project root):
    uv run python scripts/save_memory_data.py --session mock-session-1 --content "user prefers DPA for relaxation"
    uv run python scripts/save_memory_data.py --session s1 --count 5
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

DEFAULT_MEMORY_SERVICE_URL = os.environ.get('MEMORY_SERVICE_URL', '127.0.0.1:8002')
MOCK_DOC_TEMPLATE = 'mock insight #{n}: session_id={sid} (for testing read_memory_data)'


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Mock-write MatMaster session memory via the memory HTTP service'
    )
    parser.add_argument(
        '--url',
        default=DEFAULT_MEMORY_SERVICE_URL,
        help=f'Memory service base URL host:port (default: {DEFAULT_MEMORY_SERVICE_URL})',
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

    base_url = args.url if '://' in args.url else f'http://{args.url}'
    write_endpoint = f'{base_url.rstrip("/")}/api/v1/memory/write'

    if args.content is not None:
        texts = [args.content]
    else:
        n = max(1, args.count)
        texts = [
            MOCK_DOC_TEMPLATE.format(n=i + 1, sid=args.session)
            for i in range(n)
        ]

    t0 = time.perf_counter()
    for i, text in enumerate(texts):
        try:
            resp = requests.post(
                write_endpoint,
                json={
                    'session_id': args.session,
                    'text': text,
                    'metadata': {},
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f'Write failed (item {i + 1}): {e}')
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(e.response.text)
                except Exception:
                    pass
            sys.exit(1)

    elapsed = time.perf_counter() - t0
    print(f'[timer] save: {elapsed:.3f} s')
    print(f'Wrote {len(texts)} document(s) to session_id={args.session!r}')
    for i, doc in enumerate(texts):
        preview = doc[:80] + '...' if len(doc) > 80 else doc
        print(f'  {i + 1}. document={preview!r}')


if __name__ == '__main__':
    main()
