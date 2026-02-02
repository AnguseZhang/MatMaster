"""
Read and print data stored under data/chroma_memory (MatMaster session memory).

Usage (from project root):
    uv run python scripts/read_memory_data.py
    uv run python scripts/read_memory_data.py --path data/chroma_memory
    uv run python scripts/read_memory_data.py --session <session_id>   # filter by session
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

import chromadb
from chromadb.config import Settings

COLLECTION_NAME = 'matmaster_session_memory'
SESSION_ID_METADATA_KEY = 'session_id'

DEFAULT_PERSIST_DIR = os.environ.get(
    'MATMASTER_CHROMA_PERSIST_DIR',
    str(_PROJECT_ROOT / 'data' / 'chroma_memory'),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Read MatMaster ChromaDB memory data from data/chroma_memory'
    )
    parser.add_argument(
        '--path',
        default=DEFAULT_PERSIST_DIR,
        help=f'ChromaDB persist directory (default: {DEFAULT_PERSIST_DIR})',
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

    path = Path(args.path)
    if not path.exists():
        print(f'Path does not exist: {path}')
        sys.exit(1)

    t0 = time.perf_counter()
    client = chromadb.PersistentClient(
        path=str(path),
        settings=Settings(anonymized_telemetry=False),
    )

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f'Collection {COLLECTION_NAME!r} not found or error: {e}')
        sys.exit(1)

    where = {SESSION_ID_METADATA_KEY: args.session} if args.session else None
    result = collection.get(
        include=['documents', 'metadatas'],
        where=where,
        limit=args.limit,
    )
    elapsed = time.perf_counter() - t0
    print(f'[timer] read: {elapsed:.3f} s')
    print()

    ids = result.get('ids', [])
    documents = result.get('documents', [])
    metadatas = result.get('metadatas', [])

    if not ids:
        print('No documents in collection.')
        if args.session:
            print(f'(filtered by session_id={args.session!r})')
        return

    print(f'Total documents: {len(ids)}')
    if args.session:
        print(f'Filtered by session_id: {args.session!r}')
    print()

    # Group by session_id for readability
    by_session: dict[str, list[tuple[str, str, dict]]] = {}
    for i, doc_id in enumerate(ids):
        doc = documents[i] if i < len(documents) else ''
        meta = metadatas[i] if i < len(metadatas) else {}
        sid = meta.get(SESSION_ID_METADATA_KEY, '<no session_id>')
        by_session.setdefault(sid, []).append((doc_id, doc, meta))

    for session_id, items in sorted(by_session.items()):
        print(f'--- session_id: {session_id} ({len(items)} item(s)) ---')
        for doc_id, doc, meta in items:
            print(f'  id: {doc_id}')
            print(f'  document: {doc[:200]}{"..." if len(doc) > 200 else ""}')
            extra = {k: v for k, v in meta.items() if k != SESSION_ID_METADATA_KEY}
            if extra:
                print(f'  metadata: {extra}')
            print()
        print()


if __name__ == '__main__':
    main()
