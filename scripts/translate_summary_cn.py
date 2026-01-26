#!/usr/bin/env python3
"""
Translate summary_prompt to Chinese and update agents-tool.json
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import litellm
    from agents.matmaster_agent.llm_config import LLMConfig
    HAS_TRANSLATION = True
except ImportError:
    HAS_TRANSLATION = False
    print("Error: Translation libraries not available.", file=sys.stderr)
    sys.exit(1)


def translate_to_chinese(text: str, tool_name: str = "") -> str:
    """
    Translate English text to Chinese using LLM.
    
    Args:
        text: English text to translate
        tool_name: Tool name for logging
    
    Returns:
        Chinese translation
    """
    if not text:
        return ""
    
    try:
        llm_config = LLMConfig()
        model = llm_config.gpt_5_nano.model
        
        prompt = f"""Translate the following English text to Chinese (Simplified). 
Keep the technical terms, code blocks, markdown formatting, and structure exactly as they are.
Preserve all special characters, emojis, and formatting.
Only return the translation, no explanations, no additional markdown code blocks.

Text to translate:
{text}

Chinese translation:"""
        
        response = litellm.completion(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
        )
        
        translation = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present (but keep the content)
        if translation.startswith('```'):
            # Extract content from code blocks
            parts = translation.split('```')
            if len(parts) >= 3:
                translation = parts[1].strip() if len(parts[1].strip()) > 0 else parts[2].strip()
            else:
                translation = parts[-1].strip()
        
        if tool_name:
            print(f"  ✓ Translated summary for {tool_name}", file=sys.stderr)
        
        return translation
    except Exception as e:
        if tool_name:
            print(f"  ✗ Translation failed for {tool_name}: {e}", file=sys.stderr)
        return ""


def main():
    """Main function to translate and update JSON."""
    json_file = project_root / "agents-tool.json"
    
    # Read JSON file
    print(f"Reading {json_file}...", file=sys.stderr)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    tools = data.get("tools", [])
    total_tools = len(tools)
    tools_to_translate = [t for t in tools if t.get("summary_prompt", "").strip()]
    
    print(f"Found {len(tools_to_translate)} tools with summary_prompt to translate", file=sys.stderr)
    
    # Translate each tool's summary_prompt
    translated_count = 0
    for idx, tool in enumerate(tools, 1):
        tool_name = tool.get("name", "")
        summary_prompt = tool.get("summary_prompt", "").strip()
        
        if summary_prompt:
            # Check if already translated
            summary_cn = tool.get("summary_cn", "").strip()
            if summary_cn:
                print(f"  ⊙ Skipping {tool_name} (already translated)", file=sys.stderr)
                continue
            
            print(f"[{idx}/{total_tools}] Translating {tool_name}...", file=sys.stderr)
            translated = translate_to_chinese(summary_prompt, tool_name)
            
            if translated:
                tool["summary_cn"] = translated
                translated_count += 1
            else:
                print(f"  ⚠ Warning: Translation returned empty for {tool_name}", file=sys.stderr)
    
    # Save updated JSON
    print(f"\nSaving updated JSON...", file=sys.stderr)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully translated {translated_count} summaries", file=sys.stderr)
    print(f"✓ Updated {json_file}", file=sys.stderr)


if __name__ == "__main__":
    main()

