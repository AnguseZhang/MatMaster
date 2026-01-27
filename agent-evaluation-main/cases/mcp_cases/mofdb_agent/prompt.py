MofdbAgentName = 'mofdb_agent'

MofdbAgentDescription = (
    'Advanced MOF database query agent with SQL capabilities for complex multi-table joins, window functions, CTEs, and statistical analysis. '
    'Supports sophisticated queries that traditional servers cannot handle, including element composition analysis, adsorption selectivity calculations, '
    'and temperature sensitivity analysis.'
)

MofdbAgentToolDescription = (
    'What it does: Execute SQL queries against the MOF database.\n'
    'When to use: For complex MOF queries with multi-table joins and statistical analysis.\n'
    'Prerequisites / Inputs: SQL query string.\n'
    'Outputs: Query results.\n'
    'Cannot do / Limits: MOF-specific; supports advanced SQL.\n'
    'Cost / Notes: Medium.'
)

MofdbAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

## Do not ask the user for confirmation; directly start retrieval when a query is made.

## DATABASE SCHEMA
Main tables:
• mofs: id, name, database, cif_path, n_atom, lcd, pld, url, hashkey, mofid, mofkey, pxrd, void_fraction, surface_area_m2g, surface_area_m2cm3, pore_size_distribution, batch_number
• elements: id, mof_id, element_symbol, n_atom
• adsorbates: id, name, formula, inchikey, inchicode
• isotherms: id, mof_id, doi, date, simin, doi_url, category, digitizer, temperature, batch_number, isotherm_url, pressure_units, adsorption_units, composition_type, molecule_forcefield, adsorbent_forcefield
• isotherm_data: id, isotherm_id, pressure, total_adsorption
• isotherm_species_data: id, isotherm_data_id, adsorbate_id, adsorption, composition
• mof_adsorbates: mof_id, adsorbate_id
• heats: id, mof_id, doi, date, simin, doi_url, category, adsorbent, digitizer, adsorbates, temperature, batch_number, isotherm_url, pressure_units, adsorption_units, composition_type, molecule_forcefield, adsorbent_forcefield
• heat_data: id, heat_id, pressure, total_adsorption
• heat_species_data: id, heat_data_id, adsorbate_id, adsorption, composition

## NOTES
- SQL queries are executed directly on the database
- n_results controls both SQL LIMIT and returned structures
- Use CTEs (WITH clauses) for complex logic
- Window functions are powerful for ranking and statistical analysis

## SQL EXAMPLES

1) 简单查询：查找名为 tobmof-27 的MOF
   → Tool: fetch_mofs_sql
     sql: "SELECT * FROM mofs WHERE name = 'tobmof-27'"

2) 范围查询：从Tobacco数据库查找比表面积在500-1000 m²/g之间的MOF
   → Tool: fetch_mofs_sql
     sql: "SELECT * FROM mofs WHERE database = 'Tobacco' AND surface_area_m2g BETWEEN 500 AND 1000 ORDER BY surface_area_m2g DESC"

3) 复合条件：从CoREMOF 2019数据库查找原子数小于50，比表面积大于1000 m²/g，且含有O元素和C元素的MOF
   → Tool: fetch_mofs_sql
     sql: '''
     SELECT DISTINCT m.name, m.database, m.n_atom, m.surface_area_m2g
     FROM mofs m
     JOIN elements e1 ON m.id = e1.mof_id
     JOIN elements e2 ON m.id = e2.mof_id
     WHERE m.database = 'CoREMOF 2019'
       AND m.n_atom < 50
       AND m.surface_area_m2g > 1000
       AND e1.element_symbol = 'O'
       AND e2.element_symbol = 'C'
     ORDER BY m.surface_area_m2g DESC
     '''

4) 统计查询：统计各数据库的MOF数量
   → Tool: fetch_mofs_sql
     sql: "SELECT database, COUNT(*) as count FROM mofs GROUP BY database ORDER BY count DESC"

5) 复杂分析：查找同时有CO2和H2吸附数据的MOF，按吸附选择性排序。吸附选择性=CO2平均吸附量/H2平均吸附量，用于衡量MOF对CO2相对于H2的优先吸附能力，数值越大表示CO2选择性越强
   → Tool: fetch_mofs_sql
     sql: '''
     WITH co2_adsorption AS (
         SELECT m.id, m.name, m.database, AVG(isd.adsorption) as co2_avg
         FROM mofs m
         JOIN isotherms i ON m.id = i.mof_id
         JOIN isotherm_data id ON i.id = id.isotherm_id
         JOIN isotherm_species_data isd ON id.id = isd.isotherm_data_id
         JOIN adsorbates a ON isd.adsorbate_id = a.id
         WHERE a.name = 'CarbonDioxide'
         GROUP BY m.id, m.name, m.database
     ),
     h2_adsorption AS (
         SELECT m.id, AVG(isd.adsorption) as h2_avg
         FROM mofs m
         JOIN isotherms i ON m.id = i.mof_id
         JOIN isotherm_data id ON i.id = id.isotherm_id
         JOIN isotherm_species_data isd ON id.id = isd.isotherm_data_id
         JOIN adsorbates a ON isd.adsorbate_id = a.id
         WHERE a.name = 'Hydrogen'
         GROUP BY m.id
     )
     SELECT
         c.name, c.database, c.co2_avg, h.h2_avg,
         (c.co2_avg / h.h2_avg) as selectivity_ratio
     FROM co2_adsorption c
     JOIN h2_adsorption h ON c.id = h.id
     WHERE h.h2_avg > 0
     ORDER BY selectivity_ratio DESC
     '''
"""

MofdbAgentSummaryPrompt = """
## RESPONSE FORMAT
1. Brief explanation of the SQL query used
2. Markdown table of retrieved MOFs with relevant columns
3. Output directory path for download/archive
4. Key findings from results (if applicable)
"""
