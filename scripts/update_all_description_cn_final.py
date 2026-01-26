#!/usr/bin/env python3
"""
Update all description_cn in agents-tool.json with Chinese translations
"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent

def translate_description(description: str) -> str:
    """
    Translate description to Chinese, preserving structure.
    """
    if not description:
        return ""
    
    # Section headers
    headers = {
        "What it does:": "功能：",
        "When to use:": "何时使用：",
        "Prerequisites / Inputs:": "前提条件/输入：",
        "Outputs:": "输出：",
        "Cannot do / Limits:": "无法做到/限制：",
        "Cost / Notes:": "成本/备注：",
    }
    
    lines = description.split('\n')
    result = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("")
            continue
        
        # Check for headers
        found = False
        for eng, cn in headers.items():
            if stripped.startswith(eng):
                content = stripped[len(eng):].strip()
                if content:
                    # Translate the content
                    translated_content = translate_content_phrase(content)
                    result.append(f"{cn} {translated_content}")
                else:
                    result.append(cn)
                found = True
                break
        
        if not found:
            result.append(translate_content_phrase(stripped))
    
    return "\n".join(result)


def translate_content_phrase(text: str) -> str:
    """
    Translate content phrases to Chinese.
    This handles common technical terms in materials science.
    """
    # Comprehensive translation mapping for common phrases
    # This is a simplified version - for production use proper translation service
    
    # Common technical terms
    translations = {
        "Calculate": "计算",
        "Perform": "执行",
        "Run": "运行",
        "Generate": "生成",
        "Build": "构建",
        "Create": "创建",
        "Extract": "提取",
        "Analyze": "分析",
        "Predict": "预测",
        "Optimize": "优化",
        "Search": "搜索",
        "Query": "查询",
        "Retrieve": "检索",
        "Fetch": "获取",
        "Execute": "执行",
        "using DFT": "使用 DFT",
        "using ML potential": "使用机器学习势",
        "Structure file": "结构文件",
        "in cif/VASP POSCAR/ABACUS STRU format": "以 cif/VASP POSCAR/ABACUS STRU 格式",
        "DFT parameters": "DFT 参数",
        "formation energy": "形成能",
        "vacancy formation energy": "空位形成能",
        "phonon dispersion": "声子色散",
        "band structure": "能带结构",
        "band gap": "带隙",
        "density of states": "态密度",
        "When you need": "当您需要",
        "supports": "支持",
        "before calculation": "计算前",
        "DFT calculation cost": "DFT 计算成本",
        "Low": "低",
        "Medium": "中",
        "High": "高",
        "requires": "需要",
        "may need": "可能需要",
        "optional": "可选",
        "only": "仅",
        "specific to": "特定于",
        "limited to": "仅限于",
    }
    
    # Simple replacement
    result = text
    for eng, cn in sorted(translations.items(), key=lambda x: -len(x[0])):
        result = result.replace(eng, cn)
    
    return result


def main():
    json_file = project_root / "agents-tool.json"
    
    print(f"Reading {json_file}...")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("Translating all descriptions to Chinese...")
    updated = 0
    
    for tool in data["tools"]:
        name = tool.get("name", "")
        desc = tool.get("description", "").strip()
        desc_cn = tool.get("description_cn", "").strip()
        
        if desc and not desc_cn:
            translated = translate_description(desc)
            tool["description_cn"] = translated
            updated += 1
            
            if updated % 20 == 0:
                print(f"  Progress: {updated} tools translated...")
    
    print(f"\nSaving updated JSON...")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully updated {updated} descriptions")
    print(f"✓ Updated {json_file}")


if __name__ == "__main__":
    main()

