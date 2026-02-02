MEMORY_WRITER_AGENT_NAME = 'memory_writer_agent'

# Tool names whose results are stored to memory (e.g. structure info for later plans/params).
MEMORY_TOOLS_STORE_RESULTS = frozenset(
    [
        'get_structure_info',
        # Add more as needed: e.g. 'get_table_field_info', 'query_table', etc.
    ]
)
