"""
Memory reader: retrieve session-scoped snippets and format for prompt injection.
"""

import logging

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.logger import PrefixFilter
from agents.matmaster_agent.memory.kernel import get_memory_kernel

logger = logging.getLogger(__name__)
logger.addFilter(PrefixFilter(MATMASTER_AGENT_NAME))
logger.setLevel(logging.INFO)

# Section header used when injecting into planner prompt.
SHORT_TERM_MEMORY_HEADER = '短期工作记忆 (Short-term working memory)'


def format_short_term_memory(
    query_text: str,
    session_id: str,
    n_results: int = 5,
) -> str:
    """
    Retrieve relevant snippets for the current session and format as a single block.

    Returns a string suitable for insertion into the planner system prompt,
    or an empty string if no relevant memory is found.
    """
    if not session_id:
        logger.debug('format_short_term_memory skipped: empty session_id')
        return ''
    kernel = get_memory_kernel()
    results = kernel.retrieve(
        query_text=query_text,
        session_id=session_id,
        n_results=n_results,
    )
    if not results:
        logger.info(
            'format_short_term_memory session_id=%s query_len=%d n_results=%d -> 0 hits',
            session_id,
            len(query_text),
            n_results,
        )
        return ''
    lines = [f'### {SHORT_TERM_MEMORY_HEADER}', '']
    for i, item in enumerate(results, 1):
        doc = item.get('document', '')
        if doc:
            lines.append(f'- [{i}] {doc}')
    if len(lines) <= 2:
        return ''
    lines.append('')
    logger.info(
        'format_short_term_memory session_id=%s query_len=%d -> %d snippet(s)',
        session_id,
        len(query_text),
        len(results),
    )
    return '\n'.join(lines)
