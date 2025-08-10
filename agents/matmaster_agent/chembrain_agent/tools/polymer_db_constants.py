POLY_TABLE_NAME = "polym00"
PAPER_METADATA_TABLE_NAME = "690hd00"
PAPER_TEXT_TABLE_NAME = "690hd02"
TABLE_FILED_INFO_NAME = "690hd14"
TABLE_MONOMER_INFO_NAME = "690hd16"

POLYMER_DB_TABLES = {
    'tables': [
        {
            "table_name": POLY_TABLE_NAME,
            "description": "The table contains information about polymers, including their properties, synthesis methods, and applications.",
        },
        {
            "table_name": PAPER_METADATA_TABLE_NAME,
            "description": "The table contains metadata about papers, including their titles, authors, publication dates, journal information, etc.",
        },
        {
            "table_name": PAPER_TEXT_TABLE_NAME,
            "description": "The table contains the full text of papers.",
        },
        {
            "table_name": TABLE_MONOMER_INFO_NAME,
            "description": "The table contains information about monomers, including their abbreviations, names, SMILES and paper doi."
        }
    ],
    "paper_text_table": PAPER_TEXT_TABLE_NAME,
    "paper_figure_table": None,
    "field_info_table": TABLE_FILED_INFO_NAME,
}
