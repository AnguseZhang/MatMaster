#!/usr/bin/env python3
"""
Translate all descriptions in agents-tool.json to Chinese and update description_cn
"""
import json
import re
from pathlib import Path

project_root = Path(__file__).parent.parent

def translate_description(description: str) -> str:
    """
    Translate description to Chinese, preserving the structured format.
    """
    if not description:
        return ""
    
    # Section header translations
    section_map = {
        "What it does:": "功能：",
        "When to use:": "何时使用：",
        "Prerequisites / Inputs:": "前提条件/输入：",
        "Outputs:": "输出：",
        "Cannot do / Limits:": "无法做到/限制：",
        "Cost / Notes:": "成本/备注：",
    }
    
    lines = description.split('\n')
    translated_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            translated_lines.append("")
            continue
        
        # Check for section headers
        translated = False
        for eng_header, cn_header in section_map.items():
            if stripped.startswith(eng_header):
                content = stripped[len(eng_header):].strip()
                if content:
                    translated_content = translate_content(content)
                    translated_lines.append(f"{cn_header} {translated_content}")
                else:
                    translated_lines.append(cn_header)
                translated = True
                break
        
        if not translated:
            translated_lines.append(translate_content(stripped))
    
    return "\n".join(translated_lines)


def translate_content(text: str) -> str:
    """
    Translate content text to Chinese.
    Handles common technical terms and phrases in materials science.
    """
    # Comprehensive translation mapping
    translations = {
        # Actions
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
        "Evaluate": "评估",
        "Screen": "筛选",
        "Identify": "识别",
        "Parse": "解析",
        "Visualize": "可视化",
        
        # Technical terms
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
        "DOS": "DOS",
        "PDOS": "PDOS",
        "SCF calculation": "SCF 计算",
        "ground state energy": "基态能量",
        "relaxation": "弛豫",
        "optimization": "优化",
        "molecular dynamics": "分子动力学",
        "MD": "MD",
        "elastic constants": "弹性常数",
        "elastic properties": "弹性性质",
        "EOS": "EOS",
        "equation of state": "状态方程",
        "work function": "功函数",
        "Bader charge": "Bader 电荷",
        "electron localization function": "电子局域化函数",
        "ELF": "ELF",
        "NEB": "NEB",
        "nudged elastic band": "推弹性能带",
        "supercell": "超胞",
        "high-symmetry points": "高对称点",
        "k-path": "k 路径",
        "functional": "泛函",
        "spin polarization": "自旋极化",
        "DFT+U": "DFT+U",
        "magnetic moments": "磁矩",
        "ML potential": "机器学习势",
        "machine learning potential": "机器学习势",
        "ML-based": "基于机器学习",
        "DFT-based": "基于 DFT",
        
        # Common phrases
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
        "for": "用于",
        "from": "从",
        "to": "到",
        "with": "使用",
        "by": "通过",
        "and": "和",
        "or": "或",
    }
    
    # Apply translations (longest first to avoid partial matches)
    result = text
    for eng, cn in sorted(translations.items(), key=lambda x: -len(x[0])):
        # Case-insensitive replacement for most terms
        if eng.lower() == eng:  # Lowercase terms
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            result = pattern.sub(cn, result)
        else:  # Preserve case for acronyms and specific terms
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
        description = tool.get("description", "").strip()
        description_cn = tool.get("description_cn", "").strip()
        
        if description and not description_cn:
            translated = translate_description(description)
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

