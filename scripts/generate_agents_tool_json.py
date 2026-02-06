#!/usr/bin/env python3
"""
Generate agents-tool.json from tools_opt.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.matmaster_agent.sub_agents.tools_opt import ALL_TOOLS
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum

# Import URL extraction function
try:
    from scripts.get_agent_urls import get_urls_for_all_environments
    AGENT_URL_MAPPING = get_urls_for_all_environments()
except Exception as e:
    print(f"Warning: Could not load agent URLs: {e}", file=sys.stderr)
    AGENT_URL_MAPPING = {}


# Scene ID Mapping (Scene Name -> Scene ID)
# This mapping is generated automatically based on the scenes used in ALL_TOOLS
# Scene IDs are assigned sequentially starting from 001, sorted alphabetically by scene name
# 
# Scene ID -> Scene Name:
# 001 -> ABACUS
# 002 -> APEX
# 005 -> COMPOSITION_OPTIMIZATION
# 007 -> CONVEXHULL
# 008 -> DATABASE_SEARCH
# 010 -> DOE
# 011 -> DPA
# 015 -> Electron_Microscope
# 016 -> HIGH_ENTROPY_ALLOY
# 019 -> LITERATURE
# 020 -> MOLECULAR_DYNAMICS
# 021 -> NMR
# 023 -> OPTIMIZE_STRUCTURE
# 024 -> PEROVSKITE_RESEARCH
# 026 -> PHYSICAL_ADSORPTION
# 027 -> PILOTEYE_ELECTRO
# 028 -> POLYMER
# 029 -> POST_MD_ANALYSIS
# 030 -> REACTION
# 033 -> STEEL
# 034 -> STRUCTURE_GENERATE
# 035 -> STRUCTURE_SANITIZE
# 036 -> SUPERCONDUCTOR
# 038 -> Solid_State_Electrolyte
# 039 -> THERMOELECTRIC
# 040 -> TPD
# 041 -> UNIVERSAL
# 043 -> VISUALIZE_DATA
# 045 -> XRD
# 000 -> None (empty scene)

# Create SceneEnum to numeric ID mapping (starting from 001)
def create_scene_id_mapping():
    """Create a mapping from SceneEnum to numeric ID (001, 002, ...)."""
    scene_id_map = {}
    scene_id_counter = 1
    
    # Get all unique scenes from ALL_TOOLS
    all_scenes = set()
    for tool_config in ALL_TOOLS.values():
        scenes = tool_config.get("scene", [])
        for scene in scenes:
            if isinstance(scene, SceneEnum):
                all_scenes.add(scene)
    
    # Sort scenes by name for consistent ordering
    sorted_scenes = sorted(all_scenes, key=lambda x: x.name)
    
    # Create mapping
    for scene in sorted_scenes:
        scene_id_map[scene] = f"{scene_id_counter:03d}"
        scene_id_counter += 1
    
    # Handle empty scene case
    scene_id_map[None] = "000"
    
    return scene_id_map


SCENE_ID_MAP = create_scene_id_mapping()


def get_scene_name(scene_enum):
    """Convert SceneEnum to string name."""
    if isinstance(scene_enum, SceneEnum):
        return scene_enum.name
    return str(scene_enum)


def get_scene_id(scene_enum):
    """Get numeric ID for a scene."""
    if isinstance(scene_enum, SceneEnum):
        return SCENE_ID_MAP.get(scene_enum, "000")
    return "000"


def parse_description(description: str) -> dict:
    """
    Parse description string into dictionary format.
    
    Args:
        description: Description string with sections separated by newlines
    
    Returns:
        Dictionary with keys: "What it does", "When to use", "Input", "Output", "Notes", "Costs"
    """
    # Normalize description to string (supports tuple/list concatenation)
    if not description:
        return {}
    if isinstance(description, (tuple, list)):
        # Join multi-part descriptions safely with newlines
        description = "\n".join(str(part) for part in description)
    else:
        description = str(description)
    
    result = {}
    lines = description.split('\n')
    
    current_key = None
    current_value = []
    input_value = []
    output_value = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for section headers
        if line.startswith('What it does:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "What it does"
            current_value = [line.replace('What it does:', '').strip()]
        elif line.startswith('When to use:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "When to use"
            current_value = [line.replace('When to use:', '').strip()]
        elif line.startswith('Prerequisites / Inputs:') or line.startswith('Inputs:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "Input"
            prefix = 'Prerequisites / Inputs:' if line.startswith('Prerequisites / Inputs:') else 'Inputs:'
            input_value = [line.replace(prefix, '').strip()]
            current_value = input_value
        elif line.startswith('Outputs:'):
            # Save input if exists
            if current_key == "Input":
                if input_value:
                    result["Input"] = ' '.join(input_value).strip()
            elif current_key:
                result[current_key] = ' '.join(current_value).strip()
            
            current_key = "Output"
            output_value = [line.replace('Outputs:', '').strip()]
            current_value = output_value
        elif line.startswith('Cannot do / Limits:') or line.startswith('Limits:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            prefix = 'Cannot do / Limits:' if line.startswith('Cannot do / Limits:') else 'Limits:'
            current_key = "Notes"
            current_value = [line.replace(prefix, '').strip()]
        elif line.startswith('Cost / Notes:') or line.startswith('Costs:') or line.startswith('Cost:'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            prefix = 'Cost / Notes:' if line.startswith('Cost / Notes:') else ('Costs:' if line.startswith('Costs:') else 'Cost:')
            current_key = "Costs"
            current_value = [line.replace(prefix, '').strip()]
        else:
            # Continue current section
            if current_key:
                current_value.append(line)
                if current_key == "Input":
                    input_value.append(line)
                elif current_key == "Output":
                    output_value.append(line)
    
    # Add last section
    if current_key:
        result[current_key] = ' '.join(current_value).strip()
    
    return result


def parse_description_cn(description_cn: str) -> dict:
    """
    Parse Chinese description string into dictionary format.
    
    Args:
        description_cn: Chinese description string with sections separated by newlines
    
    Returns:
        Dictionary with keys: "工具简介", "使用场景", "输入", "输出", "注意事项", "成本"
    """
    # Normalize Chinese description to string (supports tuple/list concatenation)
    if not description_cn:
        return {}
    if isinstance(description_cn, (tuple, list)):
        description_cn = "\n".join(str(part) for part in description_cn)
    else:
        description_cn = str(description_cn)
    
    result = {}
    lines = description_cn.split('\n')
    
    current_key = None
    current_value = []
    input_value = []
    output_value = []
    in_usage_method = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for section headers
        if line.startswith('功能：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "工具简介"
            current_value = [line.replace('功能：', '').strip()]
        elif line.startswith('使用场景：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "使用场景"
            current_value = [line.replace('使用场景：', '').strip()]
            in_usage_method = False
        elif current_key == "使用场景" and (',' in line or line.isupper() or line.isdigit()):
            # Skip tag lines like "ABACUS,空位形成能" that appear after "使用场景："
            continue
        elif current_key == "使用场景" and not line.startswith(('功能：', '使用场景：', '使用方法：', '1. 输入：', '1.输入：', '2. 输出：', '2.输出：', '3. 注意事项：', '3.注意事项：', '4. 成本/备注：', '4.成本/备注：', '前置条件/输入：', '输入：', '输出：', '不能做/限制：', '限制：', '注意事项：', '成本/备注：', '成本：')):
            # Skip tag lines between "使用场景：" and "使用方法：" (e.g., "结构生成")
            # These are typically scene names or tags that should not be part of the usage scenario
            continue
        elif line.startswith('使用方法：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            in_usage_method = True
            current_key = None
            current_value = []
            input_value = []
            output_value = []
        elif line.startswith('1. 输入：') or line.startswith('1.输入：'):
            if in_usage_method:
                if current_key:
                    result[current_key] = ' '.join(current_value).strip()
                current_key = "输入"
                prefix = '1. 输入：' if line.startswith('1. 输入：') else '1.输入：'
                content = line.replace(prefix, '').strip()
                # Skip if empty (the actual content is on next lines)
                if content:
                    input_value = [content]
                    current_value = input_value
                else:
                    input_value = []
                    current_value = input_value
        elif line.startswith('2. 输出：') or line.startswith('2.输出：'):
            if in_usage_method:
                if current_key == "输入":
                    if input_value:
                        result["输入"] = ' '.join(input_value).strip()
                elif current_key:
                    result[current_key] = ' '.join(current_value).strip()
                current_key = "输出"
                prefix = '2. 输出：' if line.startswith('2. 输出：') else '2.输出：'
                content = line.replace(prefix, '').strip()
                # Skip if empty (the actual content is on next lines)
                if content:
                    output_value = [content]
                    current_value = output_value
                else:
                    output_value = []
                    current_value = output_value
        elif line.startswith('3. 注意事项：') or line.startswith('3.注意事项：'):
            if in_usage_method:
                if current_key == "输出":
                    if output_value:
                        result["输出"] = ' '.join(output_value).strip()
                elif current_key:
                    result[current_key] = ' '.join(current_value).strip()
                in_usage_method = False
                current_key = "注意事项"
                prefix = '3. 注意事项：' if line.startswith('3. 注意事项：') else '3.注意事项：'
                content = line.replace(prefix, '').strip()
                current_value = [content] if content else []
        elif line.startswith('4. 成本/备注：') or line.startswith('4.成本/备注：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "成本"
            prefix = '4. 成本/备注：' if line.startswith('4. 成本/备注：') else '4.成本/备注：'
            content = line.replace(prefix, '').strip()
            current_value = [content] if content else []
            in_usage_method = False
        elif line.startswith('前置条件/输入：') or line.startswith('输入：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            current_key = "输入"
            prefix = '前置条件/输入：' if line.startswith('前置条件/输入：') else '输入：'
            input_value = [line.replace(prefix, '').strip()]
            current_value = input_value
            in_usage_method = False
        elif line.startswith('输出：'):
            # Save input if exists
            if current_key == "输入":
                if input_value:
                    result["输入"] = ' '.join(input_value).strip()
            elif current_key:
                result[current_key] = ' '.join(current_value).strip()
            
            current_key = "输出"
            output_value = [line.replace('输出：', '').strip()]
            current_value = output_value
            in_usage_method = False
        elif line.startswith('不能做/限制：') or line.startswith('限制：') or line.startswith('注意事项：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            prefix = '不能做/限制：' if line.startswith('不能做/限制：') else ('限制：' if line.startswith('限制：') else '注意事项：')
            current_key = "注意事项"
            current_value = [line.replace(prefix, '').strip()]
            in_usage_method = False
        elif line.startswith('成本/备注：') or line.startswith('成本：'):
            if current_key:
                result[current_key] = ' '.join(current_value).strip()
            prefix = '成本/备注：' if line.startswith('成本/备注：') else '成本：'
            current_key = "成本"
            current_value = [line.replace(prefix, '').strip()]
            in_usage_method = False
        else:
            # Continue current section
            if current_key:
                # Remove leading whitespace from indented lines
                cleaned_line = line.lstrip()
                if cleaned_line:
                    # Only append to current_value, input_value/output_value are references
                    current_value.append(cleaned_line)
            elif in_usage_method:
                # Skip lines like "ABACUS,空位形成能" that appear before "使用方法："
                pass
    
    # Add last section
    if current_key:
        result[current_key] = ' '.join(current_value).strip()
    
    # Handle remaining input/output if in usage method
    if in_usage_method:
        if current_key == "输入" and input_value:
            result["输入"] = ' '.join(input_value).strip()
        elif current_key == "输出" and output_value:
            result["输出"] = ' '.join(output_value).strip()
    
    return result


def generate_tool_id(tool_name: str, primary_scene, scene_index: int) -> str:
    """
    Generate unique tool_id in format: {SCENE_ID}-{TOOL_PREFIX}-{INDEX:03d}
    
    Args:
        tool_name: Tool name
        primary_scene: Primary scene (SceneEnum or None)
        scene_index: Index within the scene (starting from 1)
    
    Returns:
        Unique tool_id string
    """
    # Get scene ID
    scene_id = get_scene_id(primary_scene)
    
    # Get tool prefix (first 8 chars, remove underscores, uppercase)
    tool_prefix = tool_name.replace("_", "")[:8].upper()
    
    # Format: 001-TOOLPREFIX-001
    return f"{scene_id}-{tool_prefix}-{scene_index:03d}"


def process_tool(tool_name: str, tool_config: dict, scene_index: int, primary_scene, zh_tool_config: dict = None) -> dict:
    """
    Process a single tool configuration into JSON format.
    
    Args:
        tool_name: Tool name (key in ALL_TOOLS)
        tool_config: Tool configuration dictionary
        scene_index: Index within the scene (starting from 1)
        primary_scene: Primary scene for this tool
        zh_tool_config: Optional Chinese tool configuration (for _zh suffix tools)
    
    Returns:
        Dictionary with tool information in JSON format
    """
    # Extract scenes and convert to string list
    scenes = tool_config.get("scene", [])
    scene_names = [get_scene_name(s) for s in scenes]
    
    # Generate tool_id (use base name without _zh suffix)
    base_tool_name = tool_name.replace('_zh', '')
    tool_id = generate_tool_id(base_tool_name, primary_scene, scene_index)
    
    # Get summary_prompt and translate it
    summary_prompt = tool_config.get("summary_prompt", "")
    summary_cn = summary_prompt
    
    # Get agent URL
    belonging_agent = tool_config.get("belonging_agent", "")
    url_info = AGENT_URL_MAPPING.get(belonging_agent, {"test": None, "uat": None, "prod": None})
    
    # Parse description into dictionary format
    description_str = tool_config.get("description", "")
    description_dict = parse_description(description_str) if description_str else {}
    
    # Get description_cn from zh_tool_config if available, otherwise from tool_config
    if zh_tool_config:
        description_cn_str = zh_tool_config.get("description", "")
    else:
        description_cn_str = tool_config.get("description_cn", "")
    
    description_cn_dict = parse_description_cn(description_cn_str) if description_cn_str else {}
    
    # Build result dictionary (use base name without _zh suffix)
    result = {
        "tool_id": tool_id,
        "name": base_tool_name,
        "description": description_dict,
        "description_cn": description_cn_dict,
        "belonging_agent": belonging_agent,
        "scenes": scene_names,
        "alternative_tools": tool_config.get("alternative", []),
        "summary_prompt": summary_prompt,
        "summary_cn": summary_cn,
        "self_check": tool_config.get("self_check", False),
        "args_setting": tool_config.get("args_setting", None),
        "server": url_info,
    }
    
    # Remove server field if all values are None
    if all(v is None for v in url_info.values()):
        result.pop("server", None)
    
    # Add optional fields if they exist
    if "bypass_confirmation" in tool_config:
        result["bypass_confirmation"] = tool_config["bypass_confirmation"]
    
    # Remove None values for cleaner JSON (but keep empty strings for summary fields)
    result = {
        k: v for k, v in result.items() 
        if v is not None or k in ["args_setting", "summary_prompt", "summary_cn"]
    }
    
    return result


def main():
    """Main function to generate agents-tool.json."""
    # Separate English and Chinese tools
    en_tools = {}
    zh_tools = {}
    
    for tool_name, tool_config in ALL_TOOLS.items():
        if tool_name.endswith('_zh'):
            base_name = tool_name[:-3]  # Remove '_zh' suffix
            zh_tools[base_name] = tool_config
        else:
            en_tools[tool_name] = tool_config
    
    # Group English tools by primary scene (first scene in the list)
    tools_by_scene = defaultdict(list)
    
    for tool_name, tool_config in en_tools.items():
        scenes = tool_config.get("scene", [])
        primary_scene = scenes[0] if scenes else None
        tools_by_scene[primary_scene].append((tool_name, tool_config))
    
    # Process tools grouped by scene
    tools_list = []
    
    # Sort scenes for consistent ordering (None goes last)
    def scene_sort_key(scene):
        if scene is None:
            return ("ZZZ", "")
        if isinstance(scene, SceneEnum):
            return ("AAA", scene.name)
        return ("ZZZ", str(scene))
    
    sorted_scenes = sorted(tools_by_scene.keys(), key=scene_sort_key)
    
    total_tools = sum(len(tools_by_scene[s]) for s in sorted_scenes)
    processed = 0
    
    for primary_scene in sorted_scenes:
        scene_tools = tools_by_scene[primary_scene]
        scene_name = get_scene_name(primary_scene) if primary_scene else "UNIVERSAL"
        
        print(f"Processing scene: {scene_name} ({len(scene_tools)} tools)", file=sys.stderr)
        
        # Process each tool in this scene, resetting index for each scene
        for scene_index, (tool_name, tool_config) in enumerate(scene_tools, start=1):
            try:
                # Get corresponding Chinese tool config if available
                zh_tool_config = zh_tools.get(tool_name)
                tool_json = process_tool(tool_name, tool_config, scene_index, primary_scene, zh_tool_config)
                tools_list.append(tool_json)
                processed += 1
                if processed % 10 == 0:
                    print(f"  Progress: {processed}/{total_tools} tools", file=sys.stderr)
            except Exception as e:
                print(f"Error processing tool {tool_name}: {e}", file=sys.stderr)
                continue
    
    # Create output dictionary
    output = {
        "tools": tools_list,
        "total_count": len(tools_list),
    }
    
    # Write to JSON file
    output_file = project_root / "agents-tool.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully generated {output_file}")
    print(f"Total tools: {len(tools_list)}")
    print(f"Scene ID mapping: {len(SCENE_ID_MAP)} scenes")


if __name__ == "__main__":
    main()

