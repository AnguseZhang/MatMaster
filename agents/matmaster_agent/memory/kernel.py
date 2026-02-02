"""
Memory Kernel: singleton ChromaDB backend for session-scoped insights.

- If MATMASTER_CHROMA_PERSIST_DIR is set: use that path (no repo data/), so
  multiple services on the same host can each use their own dir.
- If not set: use in-memory storage (no local disk), so nothing is written under
  the repo or shared filesystem.
- All writes carry session_id in metadata; all retrievals filter by session_id.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import Any, Optional

import chromadb
from chromadb.config import Settings

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)

# Metadata key used for session isolation; must be present on every document.
SESSION_ID_METADATA_KEY = 'session_id'

# Only use disk when explicitly set (e.g. in production); otherwise in-memory.
ENV_PERSIST_DIR = os.environ.get('MATMASTER_CHROMA_PERSIST_DIR')
COLLECTION_NAME = 'matmaster_session_memory'


class MemoryKernel:
    """
    Singleton manager for ChromaDB connection and the session-memory collection.

    - With MATMASTER_CHROMA_PERSIST_DIR set: persistent storage at that path.
    - Without it: in-memory only (no local data/), logic unchanged.
    - Write/retrieve always scope by session_id for single-session isolation.
    """

    _instance: Optional['MemoryKernel'] = None
    _initialized: bool = False

    def __new__(cls, persist_directory: Optional[str] = None) -> 'MemoryKernel':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, persist_directory: Optional[str] = None) -> None:
        if MemoryKernel._initialized:
            return
        persist_dir = persist_directory or ENV_PERSIST_DIR
        if persist_dir:
            self._persist_dir: Optional[str] = persist_dir
            Path(self._persist_dir).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self._persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
            logger.info(
                'MemoryKernel initialized with persistent path: %s',
                self._persist_dir,
            )
        else:
            self._persist_dir = None
            self._client = chromadb.Client(
                settings=Settings(anonymized_telemetry=False),
            )
            logger.info('MemoryKernel initialized (in-memory, no local data/)')
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={'description': 'MatMaster single-session working memory'},
        )
        MemoryKernel._initialized = True

    def write(
        self,
        text: str,
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Store one insight in the collection.

        session_id is required and is always written into metadata so that
        retrieval can filter by it. Other metadata fields are merged in.
        """
        if not session_id:
            raise ValueError('session_id is required for write')
        meta = dict(metadata or {})
        meta[SESSION_ID_METADATA_KEY] = session_id
        doc_id = str(uuid.uuid4())
        self._collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[meta],
        )
        logger.debug(
            'MemoryKernel.write session_id=%s id=%s len=%d',
            session_id,
            doc_id,
            len(text),
        )

    def retrieve(
        self,
        query_text: str,
        session_id: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Return the most relevant stored items for this session only.

        Query runs against the collection with a where filter on session_id,
        so only documents belonging to the current session are considered.
        """
        if not session_id:
            raise ValueError('session_id is required for retrieve')
        try:
            result = self._collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={SESSION_ID_METADATA_KEY: session_id},
            )
        except Exception as e:
            logger.warning('MemoryKernel.retrieve failed: %s', e)
            return []
        # Chroma returns ids, documents, metadatas as lists (one per query)
        ids = result.get('ids', [[]])[0]
        documents = result.get('documents', [[]])[0]
        metadatas = result.get('metadatas', [[]])[0]
        out = []
        for i, doc_id in enumerate(ids):
            out.append(
                {
                    'id': doc_id,
                    'document': documents[i] if i < len(documents) else '',
                    'metadata': metadatas[i] if i < len(metadatas) else {},
                }
            )
        return out


def get_memory_kernel(persist_directory: Optional[str] = None) -> MemoryKernel:
    """Return the singleton MemoryKernel, initializing it if needed."""
    return MemoryKernel(persist_directory=persist_directory)
