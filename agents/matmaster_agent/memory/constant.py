MEMORY_WRITER_AGENT_NAME = 'memory_writer_agent'

# Tool names whose results are stored to memory for session "expert intuition":
# structure/metadata, literature/search, and database query results.
MEMORY_TOOLS_STORE_RESULTS = frozenset(
    [
        # Structure and molecule metadata
        'get_structure_info',
        'get_molecule_info',
        # Literature and web search (Science Navigator, etc.)
        'search-papers-enhanced',
        'web-search',
        'extract_info_from_webpage',
        # Knowledge-base literature queries
        'query_heakb_literature',
        'query_ssekb_literature',
        'query_polymerkb_literature',
        'query_steelkb_literature',
        # Database schema and query results (perovskite and similar)
        'get_database_info',
        'sql_database_mcp',
    ]
)
