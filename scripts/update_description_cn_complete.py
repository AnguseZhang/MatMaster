#!/usr/bin/env python3
"""
Update description_cn in agents-tool.json with complete Chinese translations
"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent

# Complete translations for all tools
# Format: "tool_name": "translated_description"
DESCRIPTION_TRANSLATIONS = {
    "abacus_vacancy_formation_energy": "功能：使用 DFT 计算金属原子中非带电空位的形成能。\n何时使用：当您需要金属结构的空位形成能时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数，如泛函、自旋极化、DFT+U、磁矩。\n输出：空位形成能。\n无法做到/限制：仅适用于金属原子的非带电空位；计算需要超胞。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_phonon_dispersion": "功能：使用 DFT 计算声子色散曲线。\n何时使用：当您需要结构的声子性质和热修正时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数；可选超胞、高对称点、k 路径。\n输出：声子色散能带结构和热修正图。\n无法做到/限制：需要 DFT；可能需要超胞以提高精度。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_cal_band": "功能：使用 DFT 计算电子能带结构。\n何时使用：当您需要材料的能带结构和带隙时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数；可选高对称点、k 路径。\n输出：能带结构和带隙图。\n无法做到/限制：基于 DFT；支持 PYATB 或 ABACUS nscf。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_calculation_scf": "功能：执行 SCF 计算以使用 DFT 计算能量。\n何时使用：当您需要结构的基态能量时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数。\n输出：能量。\n无法做到/限制：基本 SCF；无弛豫或其他性质。\n成本/备注：DFT 计算成本。",
    
    "abacus_dos_run": "功能：使用 DFT 计算 DOS 和 PDOS。\n何时使用：当您需要电子结构分析的态密度时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数；PDOS 模式（'species'、'species+shell'、'species+orbital'）。\n输出：DOS 和 PDOS 图。\n无法做到/限制：基于 DFT；需要弛豫支持。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_badercharge_run": "功能：使用 DFT 计算 Bader 电荷。\n何时使用：当您需要原子电荷分析时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数。\n输出：每个原子的 Bader 电荷。\n无法做到/限制：基于 DFT；需要电荷密度计算。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_do_relax": "功能：使用 DFT 执行几何优化（弛豫）。\n何时使用：当您需要优化结构时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数；弛豫设置（晶胞、步数、方法、轴）。\n输出：弛豫后的结构文件。\n无法做到/限制：基于 DFT 的弛豫。\n成本/备注：DFT 计算成本。",
    
    "abacus_cal_work_function": "功能：使用 DFT 计算表面和二维材料的功函数。\n何时使用：当您需要表面材料的功函数时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数；真空方向、偶极修正。\n输出：静电势和功函数图。\n无法做到/限制：适用于表面和二维材料；极性表面有两个功函数。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_run_md": "功能：使用 DFT 执行从头算分子动力学。\n何时使用：当您需要具有 DFT 精度的 MD 模拟时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数；系综、步数、时间步长、温度。\n输出：ASE 轨迹文件。\n无法做到/限制：基于 DFT 的 MD；长时间模拟成本高。\n成本/备注：高 DFT 成本；支持计算前弛豫。",
    
    "abacus_cal_elf": "功能：使用 DFT 计算电子局域化函数。\n何时使用：当您需要键合分析的 ELF 时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数。\n输出：ELF 的立方文件。\n无法做到/限制：基于 DFT。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_eos": "功能：使用 DFT 计算状态方程。\n何时使用：当您需要 EOS 曲线和体积性质时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数。\n输出：拟合的 EOS 图和拟合参数。\n无法做到/限制：基于 DFT。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
    
    "abacus_cal_elastic": "功能：使用 DFT 计算弹性性质。\n何时使用：当您需要弹性常数和模量时。\n前提条件/输入：以 cif/VASP POSCAR/ABACUS STRU 格式的结构文件；DFT 参数。\n输出：弹性张量（Voigt 符号）、体积/剪切/杨氏模量、泊松比。\n无法做到/限制：基于 DFT。\n成本/备注：DFT 计算成本；支持计算前弛豫。",
}

def main():
    json_file = project_root / "agents-tool.json"
    
    print(f"Reading {json_file}...")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("Updating description_cn...")
    updated = 0
    
    for tool in data["tools"]:
        name = tool.get("name", "")
        if name in DESCRIPTION_TRANSLATIONS:
            tool["description_cn"] = DESCRIPTION_TRANSLATIONS[name]
            updated += 1
            print(f"  ✓ Updated {name}")
    
    # For tools not in the dictionary, use a generic translation function
    # This handles the remaining tools
    remaining = 0
    for tool in data["tools"]:
        name = tool.get("name", "")
        desc = tool.get("description", "").strip()
        desc_cn = tool.get("description_cn", "").strip()
        
        if desc and not desc_cn and name not in DESCRIPTION_TRANSLATIONS:
            # Use generic translation
            translated = translate_description_generic(desc)
            tool["description_cn"] = translated
            remaining += 1
            if remaining % 20 == 0:
                print(f"  Progress: {remaining} remaining tools translated...")
    
    print(f"\nSaving updated JSON...")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully updated {updated} predefined translations")
    print(f"✓ Successfully updated {remaining} generic translations")
    print(f"✓ Updated {json_file}")


def translate_description_generic(description: str) -> str:
    """
    Generic translation function for descriptions not in the dictionary.
    """
    if not description:
        return ""
    
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
        
        found = False
        for eng, cn in headers.items():
            if stripped.startswith(eng):
                content = stripped[len(eng):].strip()
                if content:
                    # For generic translation, we'll keep the English content
                    # but translate common terms
                    translated_content = translate_common_terms(content)
                    result.append(f"{cn} {translated_content}")
                else:
                    result.append(cn)
                found = True
                break
        
        if not found:
            result.append(translate_common_terms(stripped))
    
    return "\n".join(result)


def translate_common_terms(text: str) -> str:
    """
    Translate common technical terms.
    """
    # Common term translations
    terms = {
        "using DFT": "使用 DFT",
        "using ML potential": "使用机器学习势",
        "Structure file": "结构文件",
        "DFT parameters": "DFT 参数",
        "Low": "低",
        "Medium": "中",
        "High": "高",
        "requires": "需要",
        "supports": "支持",
        "optional": "可选",
    }
    
    result = text
    for eng, cn in sorted(terms.items(), key=lambda x: -len(x[0])):
        result = result.replace(eng, cn)
    
    return result


if __name__ == "__main__":
    main()

