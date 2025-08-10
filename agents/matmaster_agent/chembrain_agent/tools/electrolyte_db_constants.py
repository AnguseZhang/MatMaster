PAPER_METADATA_TABLE_NAME = "133ef07"
PAPER_TEXT_TABLE_NAME = "133ef08"
PAPER_FIGURE_TABLE_NAME = "133ef11"
MOLECULE_TABLE_NAME = "133ef12"
PERFORMANCE_TABLE_NAME = "133ef14"
TABLE_FILED_INFO_NAME = "133ef19"



ELECTROLYTE_DB_TABLES = {
    'tables': [
        {
            "table_name": PAPER_METADATA_TABLE_NAME,
            "description": "The table contains metadata about papers, including their titles, authors, publication dates, journal information, etc.",
        },
        {
            "table_name": PAPER_TEXT_TABLE_NAME,
            "description": "The table contains the full text of papers.",
        },
        {
            "table_name": PAPER_FIGURE_TABLE_NAME,
            "description": "The table contains the figures of papers.",
        },
        {
            "table_name": MOLECULE_TABLE_NAME,
            "description": "The table contains information about molecules used in electrolytes, including their full name, smiles, and CAS.",
        },
        # {
        #     "table_name": SOLUTION_TABLE_NAME,
        #     "description": "The table contains information about solutions used in electrolytes, including solvents, solutes, and additives.",
        # },
        {
            "table_name": PERFORMANCE_TABLE_NAME,
            "description": "The table contains information about the performance of electrolytes, including cathode, anode, and key performance.",
        },
    ],
    "paper_text_table": PAPER_TEXT_TABLE_NAME,
    "paper_figure_table": PAPER_FIGURE_TABLE_NAME,
    "field_info_table": TABLE_FILED_INFO_NAME,
}


