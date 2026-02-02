"""
Mock-write data to data/chroma_memory (MatMaster session memory) for testing.

Usage (from project root):
    uv run python scripts/save_memory_data.py --session mock-session-1 --content "user prefers DPA for relaxation"
    uv run python scripts/save_memory_data.py --session s1 --count 5   # write 5 mock docs to session s1
    uv run python scripts/save_memory_data.py --path data/chroma_memory --session s2 --content "test"
"""

import argparse
import os
import sys
import time
import uuid
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

MOCK_DOC_TEMPLATE = 'mock insight #{n}: session_id={sid} (for testing read_memory_data)'


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Mock-write MatMaster ChromaDB memory data to data/chroma_memory'
    )
    parser.add_argument(
        '--path',
        default=DEFAULT_PERSIST_DIR,
        help=f'ChromaDB persist directory (default: {DEFAULT_PERSIST_DIR})',
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

    path = Path(args.path)
    path.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    client = chromadb.PersistentClient(
        path=str(path),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={'description': 'MatMaster single-session working memory'},
    )

    if args.content is not None:
        ids = [str(uuid.uuid4())]
        documents = [args.content]
        metadatas = [{SESSION_ID_METADATA_KEY: args.session}]
    else:
        n = max(1, args.count)
        ids = [str(uuid.uuid4()) for _ in range(n)]
        documents = [
            MOCK_DOC_TEMPLATE.format(n=i + 1, sid=args.session) for i in range(n)
        ]
        metadatas = [{SESSION_ID_METADATA_KEY: args.session} for _ in range(n)]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    elapsed = time.perf_counter() - t0
    print(f'[timer] save: {elapsed:.3f} s')
    print(f'Wrote {len(ids)} document(s) to session_id={args.session!r}')
    for i, (doc_id, doc) in enumerate(zip(ids, documents)):
        preview = doc[:80] + '...' if len(doc) > 80 else doc
        print(f'  {i + 1}. id={doc_id}  document={preview!r}')


if __name__ == '__main__':
    main()
