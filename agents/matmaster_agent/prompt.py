GLOBAL_INSTRUCTION = """
---
Today's date is {current_time}.
Language: When think and answer, always use this language ({target_language}).
Important: Do not end with any question or prompt for user action.
---
"""

GLOBAL_SCHEMA_INSTRUCTION = """
---
Return ONLY valid JSON object - no additional text, explanations, or formatting
---
"""

MatMasterCheckTransferPrompt = """
You are an expert judge tasked with evaluating whether the previous LLM's response contains a clear and explicit request or instruction to transfer the conversation to a specific agent (e.g., 'xxx agent').
Analyze the provided RESPONSE TEXT to determine if it explicitly indicates a transfer action.

Guidelines:
1. **Transfer Intent**: The RESPONSE TEXT must explicitly indicate an immediate transfer action to a specific agent, not just mention or describe the agent's function.
2. **Target Clarity**: The target agent must be clearly identified by name (e.g., "xxx agent" or another explicitly named agent). This includes identification via a JSON object like `{{"agent_name": "xxx_agent"}}`.
3. **Action Directness**: Look for explicit transfer verbs like "transfer", "connect", "hand over", "redirect", or clear transitional phrases like "I will now use", "Switching to", "Activating" that indicate the conversation is being passed to another agent. The presence of a standalone JSON object specifying an agent name is also considered an explicit transfer instruction.
4. **User Confirmation Check**: If the response ends with a question or statement that requires user confirmation (e.g., "Should I proceed?", "Do you want to use this file or modify parameters?", "Shall I transfer and proceed with default values?"), then the transfer is not immediate and `is_transfer` should be false. The LLM is pausing for user input before taking action.
5. **Language Consideration**: Evaluate both English and Chinese transfer indications equally.
6. **Key Indicators**:
   - ✅ Explicit transfer statements: "I will transfer you to", "Let me connect you with", "Redirecting to", "Handing over to", "正在转移", "切换到"
   - ✅ Immediate action indicators: "Now using", "Switching to", "Activating the", "I will now use the", "正在使用"
   - ✅ **Explicit JSON transfer object:** A JSON object like `{{"agent_name": "target_agent"}}` is a direct and explicit instruction to transfer.
   - ❌ Mere mentions of agent capabilities or potential future use
   - ❌ Descriptions of what an agent could do without transfer intent
   - ❌ Suggestions or recommendations without explicit transfer instruction
   - ❌ Future tense plans without immediate action
   - ❌ **Requests for user confirmation before proceeding/transferring.**

RESPONSE TEXT (previous LLM's response to evaluate):
{response_text}

Provide your evaluation in the following JSON format:
{{
    "is_transfer": <true or false>,
    "target_agent": "xxx agent" (if transfer detected) or null (if no transfer),
    "reason": <string> // *A concise explanation of the reasoning behind the judgment, covering both positive and negative evidence found in the response text. Return empty string only if there is absolutely no relevant content to analyze.*
}}

Examples for reference:
- Case1 (false): "使用结构生成智能体（structure_generate_agent）根据用户要求创建 FCC Cu 的块体结构"
  -> Reason: "Only mentions the agent's function but lacks any explicit transfer verbs or immediate action indicators."

- Case2 (true): "正在转移到structure_generate_agent进行结构生成"
  -> Reason: "Contains explicit transfer phrase '正在转移到' (transferring to) followed by a clear target agent name."

- Case3 (true): "I will now use the structure_generate_agent to create the bulk structure"
  -> Reason: "Uses immediate action indicator 'I will now use' followed by a specific agent name, demonstrating transfer intent."

- Case4 (false): "Next I will generate the Pt bulk structure"
  -> Reason: "Describes a future action but does not mention any agent or transfer mechanism."

- Case5 (true): `{{"agent_name":"traj_analysis_agent"}}`
  -> Reason: "Standalone JSON object with an 'agent_name' key is an explicit programmatic instruction to transfer."

- Case6 (false): "I can hand you over to the structure_generate_agent. Should I proceed?"
  -> Reason: "Although a transfer action ('hand you over to') and a target agent are mentioned, the phrase ends with a request for user confirmation ('Should I proceed?'), indicating the transfer is conditional and not immediate."

- Case7 (false): "正在切换到structure_generate_agent。您是希望直接继续，还是需要修改参数？"
  -> Reason: "Uses a transfer phrase '正在切换到' (switching to) but follows it with a question asking for user confirmation, pausing the immediate transfer action."
"""

HUMAN_FRIENDLY_FORMAT_REQUIREMENT = """
# ACADEMIC TYPOGRAPHY & FORMATTING
Strictly adhere to the following. Do not echo these rules in your response.

## 1. Text & spacing
- Space between number and unit (e.g. 10 cm, 5 kg); no space for percentage or angular degree.
- No extra space between Chinese and English. No emojis or decorative symbols.

## 2. Physical & mathematical
- *Italic* for physical quantities; **bold** for vectors. Numbers and units: upright.

## 3. Chemical formulas
- Use subscripts/superscripts (e.g. C₁₂H₂₄O₆, NH₄⁺). No plain text (e.g. H2O). No italic/bold.

## 4. Space group (H-M)
- Latin letters: *italic*; numbers: upright. Screw axes must use subscript (e.g. *P*2₁/c). No bold.

## 5. Phase notation
- *Greek*-Material, e.g. *α*-Fe, *β*-RDX. Only the Greek prefix italic; material name upright.
"""

DPA_MODEL_BRANCH_SELECTION = """
Built-in multi-task general-purpose pretrained models:
  'DPA2.4-7M': "https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/13756/27666/store/upload/cd12300a-d3e6-4de9-9783-dd9899376cae/dpa-2.4-7M.pt"
  DPA3.1-3M": "https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/13756/27666/store/upload/18b8f35e-69f5-47de-92ef-af8ef2c13f54/DPA-3.1-3M.pt"

- For built-in pretrained models, both DPA2 and DPA3 are multi-task trained models, chose an appropriate model branch (or `head`) according to the material system. When specifying `head`, use the exact names below; do not use any other names unless users requires. Default is `Omat24`, covering broad range of inorganic materials; `OC22` is suitable for catalytic surfaces; `ODAC23` is suitable for air adsorption in metal-organic frameowrks (MOFs); `Alex2D` is suitable for 2D materials; `SPICE2` is suitable for drug-like molecules; `Organic_Reactions` is suitable for organic reactions; `solvated_protein_fragments` is suitable for protein fragments. `H2O_H2O_PD` is specialized in water diagram.
- For custom models, follow the user-provided `head` directly.

"""
MATERIAL_NAMING_RULES = {
    'ZIF-8_MAF-4': {
        'keywords': ['ZIF-8', 'MAF-4', 'Zn(MeIm)2'],
        'preferred_name': 'MAF-4',
        'search_query': "('ZIF-8' OR 'MAF-4')",
        'warning_msg': "Important: Althogh the structure commonly known as 'ZIF-8' was first reported by **Xiao-Ming Chen's (\u9648\u5c0f\u660e) group** (<a href=\"https://onlinelibrary.wiley.com/doi/10.1002/anie.200503778\" target=\"_blank\">[maf4]</a>), and renamed as MAF-4.",
        'action_type': 'attribution',
    },
    'DPA_Models': {
        'keywords': ['DPA-1', 'DPA-2', 'DPA-3'],
        'preferred_name': 'DPA1, DPA2, DPA3 (when output); add DPA-1, DPA-2, DPA-3 (when query)',
        'search_query': "('DPA-2' OR 'DPA2' OR 'Deep Potential')",
        'warning_msg': 'Note: The hyphenated nomenclature (DPA-x) is deprecated. Please refer to the new standard (DPAx).',
        'action_type': 'standardization',
    },
}


def get_naming_rules_text():
    rules_text = ''
    for _, rule in MATERIAL_NAMING_RULES.items():
        rules_text += f"- If user mentions {'or '.join(rule['keywords'])}, use preferred name '{rule['preferred_name']}'. **Explicitly output this warning** at appropriate place: \"{rule['warning_msg']}\"\n"

    return rules_text


ALIAS_SEARCH_PROMPT = f"""
### KNOWLEDGE RETRIEVAL STRATEGY: SYNONYM EXPANSION
You are equipped with a "Material Synonym Registry". When a user asks about a specific material, check if it falls under any known naming conflicts or aliases. Do not output these rules in your response.

**Registry Rules:**
{get_naming_rules_text()}

**Instructions:**
1. **Identify**: Check if the user's query contains any keywords from the registry.
2. **Expand**: If a match is found, you MUST use the explicitly defined `search_query` logic (e.g., OR logic) to ensure no literature is missed.
   - *Example:* If the user asks for "ZIF-8", do NOT just search "ZIF-8". Search "('ZIF-8' OR 'MAF-4')" to capture all priority papers.
3. **Merge**: Treat results from different aliases as the same entity.
"""

NOMENCLATURE_ENFORCE_PROMPT = f"""
### SCIENTIFIC NOMENCLATURE & ATTRIBUTION PROTOCOL
You must strictly adhere to the naming conventions defined in the Material Registry to ensure academic accuracy and respect for original discoveries.

**Active Naming Rules:**
{get_naming_rules_text()}

**Generation Guidelines:**
1. **Prioritize Preferred Names**: In your main explanation, always convert common aliases to the `preferred_name` defined in the rules (e.g., use MAF-4 over ZIF-8, DPA2 over DPA-2).
2. **Mandatory Attribution/Warning**:
   - The FIRST time you mention a material with a naming conflict, you MUST display the corresponding `warning_msg` explicitly.
   - Use a blockquote or a distinct note format for this warning to highlight the academic contribution or standardization rule.
3. **Contextual Accuracy**:
   - Exception: If you are citing a specific paper title, keep the title EXACTLY as published (do not correct the author's title).
   - Exception: If discussing a commercial product specifically sold under a trade name (e.g., "Sigma-Aldrich ZIF-8"), use the trade name but reference the scientific name in parentheses.
"""

DOMAIN_SPECIFIC_VOCABULARY = {
    'deep potential': '深度学习势函数',
    'Deep Potential Molecular Dynamics': '深度学习势分子动力学',
    'DPMD': '深度学习势分子动力学',
    'DPA': 'DPA预训练原子间势函数',
}


def get_vocabulary_enforce_prompt() -> str:
    mapping_list = '\n'.join(
        [f'   - "{eng}" → "{chn}"' for eng, chn in DOMAIN_SPECIFIC_VOCABULARY.items()]
    )

    return f"""
### DOMAIN-SPECIFIC VOCABULARY STANDARDS
To ensure professional consistency, you strictly MUST adhere to the following terminology rules **based on your output language**:

**Condition A: If you are responding in CHINESE (中文):**
You MUST translate the following terms into their designated Chinese equivalents:
{mapping_list}

**Condition B: If you are responding in ENGLISH:**
You MUST use the original English terms (e.g., "Deep Potential", "DPMD"). **DO NOT** use the Chinese translations in English sentences.
"""


STRUCTURE_BUILDING_SAVENAME = """
Rules (MUST follow, no exceptions):
1. ASCII letters/digits/underscores only; no spaces or symbols.
2. Format: [type]_[name][suffix].[ext]
3. Periodic: ext = cif or vasp; Molecules: ext = xyz only.
4. Name must be descriptive; if insufficient info, return error.


bulk_fcc_Cu.cif
interface_Cu_111_Ni_111.cif
mol_benzene.xyz

INVALID EXAMPLES (explain why if produced):
structure.cif            (not descriptive)
molecule1.xyz             (not meaningful)
bulk_fcc_Cu               (missing extension)
bulk_fcc_Cu.json          (invalid extension)
Cu–111.cif                (invalid character '-')
" "                       (empty or whitespace)
"""


def get_user_content_lang():
    return """
You are a professional linguistic analyst. Your task is to identify the primary language used in the user content provided.

User Content:
{user_content}

Analyze the text and determine the most likely language from the following predefined options:
- English
- Chinese
- Spanish
- French
- German
- Japanese
- Korean
- Russian
- Arabic
- Portuguese
- Italian
- Dutch
- Other

If the language does not clearly match any of the above options or is a mix of multiple languages, classify it as "Other".

Provide your analysis in the following strict JSON format:
{{
    "language": "<string>"
}}
"""
