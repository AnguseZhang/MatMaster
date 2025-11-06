PAPER_METADATA_TABLE_NAME = '526kq03'
PAPER_TEXT_TABLE_NAME = '723wm02'
TABLE_FILED_INFO_NAME = '526kq04'
PAPER_FIGURE_TABLE_NAME = '526kq01'

SOLID_ELECTROLYTE_DB_TABLES = {
    'tables': [
        {
            'table_name': PAPER_METADATA_TABLE_NAME,
            'description': 'Solid state electrolyte metadata table: Contains information about solid-state battery-related materials, '
            'covering basic details such as unique identifiers, system types, electrolyte status, literature identifiers, ionic conductivity, air stability, synthesis recipes, etc... '
            'Among them, the field values of Li_Na_system, solid_state_electrolyte, and doping are yes or no. '
            'DOI must be included in the selected_fields for each query.',
        },
        {
            'table_name': PAPER_TEXT_TABLE_NAME,
            'description': 'Paper text content table: Contains the full text content of papers (main_text field), linked to other tables via DOI.',
        },
        {
            'table_name': PAPER_FIGURE_TABLE_NAME,
            'description': 'Paper figure table: Contains paper-related image URLs and captions, linked to other tables via DOI. '
            'Image URLs can be used for Markdown rendering to display image content.',
        },
        {
            'table_name': TABLE_FILED_INFO_NAME,
            'description': 'Table field information: Contains field names and detailed descriptions for all tables.',
        },
    ],
    'paper_text_table': PAPER_TEXT_TABLE_NAME,
    'paper_figure_table': PAPER_FIGURE_TABLE_NAME,
    'field_info_table': TABLE_FILED_INFO_NAME,
}
