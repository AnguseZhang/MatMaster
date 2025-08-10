PAPER_METADATA_TABLE_NAME = "723wm03"
PAPER_TEXT_TABLE_NAME = "723wm02"

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
    # TODO: add field_info_table
}
