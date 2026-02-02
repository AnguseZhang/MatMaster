"""
Memory kernel for MatMaster: single-session ChromaDB-backed storage.

Exposes the kernel singleton, session-scoped write/retrieve, and reader for prompt injection.
"""

from agents.matmaster_agent.memory.kernel import MemoryKernel, get_memory_kernel
from agents.matmaster_agent.memory.reader import format_short_term_memory

__all__ = ['MemoryKernel', 'get_memory_kernel', 'format_short_term_memory']
