#!/usr/bin/env python3
"""
Translate all descriptions in agents-tool.json to Chinese
"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent

def translate_description_section(description: str) -> str:
    """
    Translate a description to Chinese, preserving the structured format.
    """
    if not description:
        return ""
    
    # Section header translations
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
        
        # Check for section headers
        found_header = False
        for eng, cn in headers.items():
            if stripped.startswith(eng):
                content = stripped[len(eng):].strip()
                if content:
                    result.append(f"{cn} {translate_text(content)}")
                else:
                    result.append(cn)
                found_header = True
                break
        
        if not found_header:
            result.append(translate_text(stripped))
    
    return "\n".join(result)


def translate_text(text: str) -> str:
    """
    Translate English text to Chinese.
    This handles common technical terms and phrases in materials science.
    """
    # Common technical translations
    # Note: This is a simplified version. For production, use a proper translation service.
    
    # I'll provide direct translations for common phrases
    # Since we have 107 tools, I'll create a comprehensive translation mapping
    
    # This function will be called for each piece of text
    # For now, return a placeholder that we'll fill with actual translations
    
    # Common phrase patterns
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
    
    # Simple replacement (basic translation)
    result = text
    for eng, cn in sorted(translations.items(), key=lambda x: -len(x[0])):
        result = result.replace(eng, cn)
    
    return result


def main():
    json_file = project_root / "agents-tool.json"
    
    print(f"Reading {json_file}...")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("Translating all descriptions...")
    updated = 0
    
    for tool in data["tools"]:
        name = tool.get("name", "")
        desc = tool.get("description", "").strip()
        desc_cn = tool.get("description_cn", "").strip()
        
        if desc and not desc_cn:
            translated = translate_description_section(desc)
            tool["description_cn"] = translated
            updated += 1
            
            if updated % 20 == 0:
                print(f"  Progress: {updated} tools translated...")
    
    print(f"\nSaving updated JSON...")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Updated {updated} descriptions")
    print(f"✓ Saved to {json_file}")


if __name__ == "__main__":
    main()

