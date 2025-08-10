PAPER_METADATA_TABLE_NAME = "723wm09"
PAPER_TEXT_TABLE_NAME = "723wm02"
TABLE_FILED_INFO_NAME = "723wm08"
# PAPER_FIGURE_TABLE_NAME = ""

SOLID_ELECTROLYTE_DB_TABLES = {
    'tables': [
        {
            "table_name": PAPER_METADATA_TABLE_NAME,
            "description": "The table contains information about solid-state battery-related materials, "
                           "covering basic details such as unique identifiers, system types, electrolyte status, and literature identifiers..."
                           " Among them, the field values of Li/Na-system, solidelectrolyte, and doping are yes or no."
                           " DOI must be in the selected_fields each query time",
        },
        {
            "table_name": PAPER_TEXT_TABLE_NAME,
            "description": "The table contains the full text of papers.",
        },

    ],
    "paper_text_table": PAPER_TEXT_TABLE_NAME,
    "paper_figure_table": None,
    "field_info_table": TABLE_FILED_INFO_NAME,
}
