BohriumPublicAgentName = 'bohriumpublic_agent'

BohriumPublicAgentToolDescription = (
    'What it does: Retrieve crystal structures from Bohrium Public database.\n'
    'When to use: For formula, elements, space group, atom count, formation energy, band gap queries.\n'
    'Prerequisites / Inputs: Filters like formula, elements, etc.\n'
    'Outputs: Structures in CIF or JSON.\n'
    'Cannot do / Limits: No logical expressions; faster than OPTIMADE.\n'
    'Cost / Notes: Low.'
)

BohriumPublicAgentArgsSetting = """
## PARAMETER CONSTRUCTION GUIDE

## Do not ask the user for confirmation; directly start retrieval when a query is made.

## FILTER OPTIONS
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
"""

BohriumPublicAgentSummaryPrompt = """
## RESPONSE FORMAT
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
