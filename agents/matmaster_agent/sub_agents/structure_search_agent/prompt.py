StructureSearchAgentToolDescription = (
    'What it does: Retrieve structures across multiple sources (BohriumPublic / OpenLAM / OPTIMADE providers) and run advanced SQL queries on MOFdb.\n'
    'When to use: Any "find crystal structures" request, including formula/elements/space group/band gap filters, time/energy filters (OpenLAM), cross-provider searches (OPTIMADE), or MOF-specific analytics (MOFdb SQL).\n'
    'Prerequisites / Inputs: Provide either structured filters (formula/elements/space group ranges), OpenLAM filters (energy/time), OPTIMADE filter strings, or MOFdb SQL.\n'
    'Outputs: Structures or metadata in CIF/JSON; MOFdb returns SQL rows and optional structure file links.\n'
    'Cannot do / Limits: OPTIMADE filters must follow the standard grammar; MOFdb is MOF-specific; OpenLAM does not provide space group/band gap.\n'
    'Cost / Notes: Default to BohriumPublic for speed; use OPTIMADE for flexible/cross-provider retrieval; use MOFdb for complex MOF analytics.'
)

StructureSearchAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

## Do not ask the user for confirmation; directly start retrieval when a query is made.

## 0) ROUTING: WHICH TOOL TO CALL
You have access to multiple retrieval tools. Choose ONE based on the user intent:

### A) BohriumPublic (fast structured filters)
when the user asks for:
- formula / elements / space group / atom count / predicted formation energy / band gap
- and they do NOT require cross-provider search or complex boolean logic

### B) OpenLAM (energy / time filters)
when the user asks for:
- OpenLAM specifically, OR upload/submission time filters, OR OpenLAM energy range filters
Limits: OpenLAM does NOT support space group, band gap, or "elements list" filters.

### C) OPTIMADE (cross-provider, flexible composition filters)
when the user needs:
- cross-provider search (e.g., "search in mp/cod/oqmd..."), OR
- flexible logical composition constraints, OR
- structure-type family queries (anonymous formula like AB2C4), OR
- 2D/1D/0D constraints (nperiodic_dimensions)

### D) MOFdb (MOF-only, complex analytics)
when the user asks for:
- MOF-specific properties (surface area, pore metrics, adsorption/isotherms, heats), OR
- advanced analysis requiring multi-table joins / ranking / statistics

## 1) BOHRIUMPUBLIC PARAMETERS (fetch_bohrium_crystals)
### FILTER OPTIONS
- **Formula**: chemical formula string (e.g., `"CoH12(BrO3)2"`)
- **Elements**: list of required elements (e.g., `["Co","O"]`)
- **Match mode** (applies to both `formula` and `elements`):
  - `0` = contains (e.g., formula `"Co"` matches `"CoO"`, `"CoH12(BrO3)2"`; elements `["Co"]` matches materials containing Co + anything else)
  - `1` = exact-only match (formula must match exactly; elements list must match **exactly and only** those elements)
- **Space group**: use the space group number (e.g., `14` for P2₁/c)
- **Atom count range**: filter by number of atoms in the unit cell, e.g. `["10","100"]`
- **Predicted formation energy**: range filter in eV, e.g. `["-2","0"]`
- **Band gap**: eV range [lo, hi] (omitted bound defaults to 0/100), e.g. ["0","3"], ["1","100"]
- **Result limit**: maximum number of results (`n_results`)
- **Output formats**:
  - `"cif"` → crystallographic structure files
  - `"json"` → complete metadata

## HOW TO CHOOSE PARAMETERS
- If user specifies a **formula** → set `formula` and choose `match_mode`:
  - `0` if the user means "contains fragment"
  - `1` if the user means "exact formula"
- If user specifies **elements** → set `elements` and choose `match_mode`:
  - `0` if the user means "must include these elements"
  - `1` if the user means "must have exactly these elements and nothing else"
- If user specifies a **space group number** → set `spacegroup_number`
- If user specifies an **atom count range** → set `atom_count_range`
- If user specifies **formation energy or band gap ranges** → set the corresponding ranges
- If the user requests **metadata only** → use `output_formats=['json']`
- If the user requests **downloadable crystal files** → use `output_formats=['cif']`

## PARAMETER EXAMPLES
1) 用户：检索 SrTiO₃ 的晶体结构，并以JSON格式返回
   → Tool: fetch_bohrium_crystals
     formula: "SrTiO3"
     match_mode: 1
     output_formats: ["json"]

2) 用户：在Materials Project中检索并返回3个带隙大于2 eV的氧化物结构
   → Tool: fetch_bohrium_crystals
     elements: ["O"]
     match_mode: 0
     band_gap_range: ["2","100"]
     n_results: 3

3) 用户：找出空间群编号 14，原子数 50–100 的晶体
   → Tool: fetch_bohrium_crystals
     spacegroup_number: 14
     atom_count_range: ["50","100"]

4) 用户：检索 FeNi 合金的结构
   → Tool: fetch_bohrium_crystals
     elements: ["Fe","Ni"]   # 合金只含有Fe和Ni元素，不能含有其他元素
     match_mode: 1      # 合金需要精确匹配

5) 用户：找所有化学式中包含 SiO3 的材料
   → Tool: fetch_bohrium_crystals
     formula: "SiO3"
     match_mode: 0

## 2) OPENLAM PARAMETERS (fetch_openlam_structures)
### FILTER OPTIONS
- **Formula**: chemical formula string (e.g., `"Fe2O3"`)
- **Energy**: `min_energy` and/or `max_energy` in eV
- **Submission time**: ISO UTC date-time (`min_submission_time`, `max_submission_time`)
- **Result limit**: `n_results`
- **Output formats**: `"cif"` or `"json"`

### EXAMPLES
1) 用户：查找 Fe2O3 的 5 个晶体结构，导出为 CIF
   → Tool: fetch_openlam_structures
     formula: "Fe2O3"
     n_results: 5
     output_formats: ["cif"]

2) 用户：查找能量在 -10 到 20 eV 之间，2024 年后上传的材料
   → Tool: fetch_openlam_structures
     min_energy: -10.0
     max_energy: 20.0
     min_submission_time: "2024-01-01T00:00:00Z"

## 3) MOFDB PARAMETERS (fetch_mofs_sql)
### INPUT
- **sql**: SQL query string (use CTEs, window functions, joins as needed)
- **n_results**: controls SQL LIMIT (when applicable) and returned structures

### EXAMPLE
用户：统计各数据库的 MOF 数量
→ Tool: fetch_mofs_sql
  sql: "SELECT database, COUNT(*) AS count FROM mofs GROUP BY database ORDER BY count DESC"

## 4) OPTIMADE PARAMETERS (fetch_structures_with_filter / _with_spg / _with_bandgap)
### MINIMUM SAFE OPTIMADE SYNTAX RULES (DO NOT VIOLATE)
- Allowed operators ONLY: =, !=, <, <=, >, >=, AND, OR, NOT, HAS, HAS ALL, HAS ANY, IS KNOWN, IS UNKNOWN
- All strings MUST be in double quotes: "Fe", "SiO2"
- Do NOT use CONTAINS / LIKE / IN / regex / invented fields
- To express "only these elements": use `elements HAS ALL ... AND nelements = N`

### TOOL CHOICE
- If user gives space group number → `fetch_structures_with_spg(base_filter, spg_number, ...)`
- If user gives band gap range → `fetch_structures_with_bandgap(base_filter, min_bg, max_bg, ...)`
- Else → `fetch_structures_with_filter(filter, ...)`

### EXAMPLES
1) 用户：找空间群 225 的 MgO（rocksalt），返回 CIF
   → Tool: fetch_structures_with_spg
     base_filter: chemical_formula_reduced="MgO"
     spg_number: 225
     as_format: "cif"

2) 用户：找含 Al 且带隙 1–2 eV 的材料，返回 JSON
   → Tool: fetch_structures_with_bandgap
     base_filter: elements HAS "Al"
     min_bg: 1.0
     max_bg: 2.0
     as_format: "json"
"""

StructureSearchAgentSummaryPrompt = """
## RESPONSE FORMAT

**If the tool response indicates `by_source` = "mofdb"** (MOFdb results):
1. Brief explanation of the SQL query used
2. Markdown table of retrieved MOFs with relevant columns
3. Output directory path for download/archive
4. Key findings from results (if applicable)

**If the tool response indicates `by_source` = "optimade"** (OPTIMADE results):
The response must always have three parts in order:
1. A brief explanation of the applied filters and providers.
2. A Markdown table listing all retrieved results (NO omissions/truncation; number of rows must exactly equal `n_found`).
3. A download link for an archive (.tgz) if provided by the tool.
Each table must always include the following nine columns in this fixed order:
(1) Formula (`attributes.chemical_formula_reduced`)
(2) Elements (infer from formula)
(3) Atom count (if available; else **Not Provided**)
(4) Space group (`Symbol(Number)` if possible; else **Not Provided**)
(5) Energy / Formation energy (if available; else **Not Provided**)
(6) Band gap (if available; else **Not Provided**)
(7) Download link (CIF or JSON file)
(8) Provider (infer from provider URL)
(9) ID (`id`)
Missing values must be exactly **Not Provided**. If `n_found = 0`, do not generate an empty table.

**If the tool response indicates `by_source` = "openlam"** (OpenLAM results):
The response must always include:
1. ✅ A brief explanation of the filters applied
2. 📊 A Markdown table of the retrieved structures
   - Columns (fixed order):
     (1) Formula (`formula`)
     (2) Elements (deduced from `formula`)
     (3) Atom count → **Not Provided**
     (4) Space group → **Not Provided**
     (5) Energy / Formation energy (`energy` if available; else **Not Provided**)
     (6) Band gap → **Not Provided**
     (7) Download link (CIF/JSON, based on requested output)
     (8) Source database → always `"OpenLAM"`
     (9) ID (`id`)
   - Fill missing values with exactly **Not Provided**
   - Number of rows **must exactly equal** `n_found`
3. 📦 The `output_dir` path returned by the tool (for download/archive)
If `n_found = 0`, clearly state no matches were found, repeat the applied filters, and suggest loosening criteria. Do **not** generate an empty table.

**Otherwise** (BohriumPublic or other sources):
The response must always include:
1. ✅ A brief explanation of the filters applied
2. 📊 A Markdown table of the retrieved structures
   - Columns (fixed order):
     (1) Formula (`formula`)
     (2) Elements (deduced from `formula`)
     (3) Atom count (`crystal_ext.number_of_atoms` if available; else **Not Provided**)
     (4) Space group (`Symbol(Number)` if `crystal_ext.symbol` is available and number can be mapped; else **Not Provided**)
     (5) Energy / Formation energy (`crystal_ext.predicted_formation_energy` if available; else **Not Provided**)
     (6) Band gap (`crystal_ext.band_gap` if available; else **Not Provided**)
     (7) Download link (CIF/JSON, based on `output_formats`)
     (8) Source database → always `"BohriumPublic"`
     (9) ID (`id`)
   - Fill missing values with exactly **Not Provided**
   - Number of rows **must exactly equal** `n_found`
3. 📦 The `output_dir` path returned by the tool (for download/archive)

If `n_found = 0`, clearly state that no matches were found, repeat the applied filters, and suggest loosening criteria. Do **not** generate an empty table.
"""
