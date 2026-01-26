#!/usr/bin/env python3
"""
Improve description_cn translations with better phrase-level translations
"""
import json
import re
from pathlib import Path

project_root = Path(__file__).parent.parent

def improve_translation(description_cn: str) -> str:
    """
    Improve the translation by fixing common issues from word-by-word translation.
    """
    if not description_cn:
        return ""
    
    # Fix common translation issues
    fixes = {
        # Fix "a到ms" -> "原子"
        r"a到ms": "原子",
        r"a到m": "原子",
        # Fix "c或rections" -> "修正"
        r"c或rections": "修正",
        r"c或rection": "修正",
        # Fix "of" in context
        r"of non-charged vacancy in metal 原子": "金属原子中非带电空位的",
        r"of (\w+)": r"\1的",
        # Fix "like" -> "如"
        r"like (\w+)": r"如 \1",
        # Fix "for" -> "用于" (but not when it's part of "for a structure")
        r" 用于 a structure": " 用于结构",
        r" 用于 a material": " 用于材料",
        r" 用于 calculation": " 进行计算",
        r" 用于 accuracy": " 以提高精度",
        # Fix "Plot of" -> "图"
        r"Plot of ": "",
        # Fix common phrases
        r"non-charged vacancy": "非带电空位",
        r"metal 原子": "金属原子",
        r"metal structures": "金属结构",
        r"phonon properties": "声子性质",
        r"thermal 修正": "热修正",
        r"electronic 能带结构": "电子能带结构",
        # Remove extra spaces
        r"  +": " ",
        r"^ ": "",
        r" $": "",
    }
    
    result = description_cn
    for pattern, replacement in fixes.items():
        result = re.sub(pattern, replacement, result)
    
    # Clean up multiple spaces
    result = re.sub(r' {2,}', ' ', result)
    
    return result


def main():
    json_file = project_root / "agents-tool.json"
    
    print(f"Reading {json_file}...")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("Improving translations...")
    updated = 0
    
    for tool in data["tools"]:
        name = tool.get("name", "")
        description_cn = tool.get("description_cn", "").strip()
        
        if description_cn:
            improved = improve_translation(description_cn)
            if improved != description_cn:
                tool["description_cn"] = improved
                updated += 1
    
    print(f"\nSaving improved JSON...")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Improved {updated} translations")
    print(f"✓ Updated {json_file}")


if __name__ == "__main__":
    main()

