#!/usr/bin/env python3
"""
Generate agents-tool.json from tools.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.matmaster_agent.sub_agents.tools import ALL_TOOLS
from agents.matmaster_agent.flow_agents.scene_agent.model import SceneEnum

try:
    import litellm
    from agents.matmaster_agent.llm_config import LLMConfig
    HAS_TRANSLATION = True
except ImportError:
    HAS_TRANSLATION = False
    print("Warning: Translation libraries not available. summary_cn will be empty.", file=sys.stderr)


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
    
    if not HAS_TRANSLATION:
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


def process_tool(tool_name: str, tool_config: dict, scene_index: int, primary_scene) -> dict:
    """
    Process a single tool configuration into JSON format.
    
    Args:
        tool_name: Tool name (key in ALL_TOOLS)
        tool_config: Tool configuration dictionary
        scene_index: Index within the scene (starting from 1)
        primary_scene: Primary scene for this tool
    
    Returns:
        Dictionary with tool information in JSON format
    """
    # Extract scenes and convert to string list
    scenes = tool_config.get("scene", [])
    scene_names = [get_scene_name(s) for s in scenes]
    
    # Generate tool_id
    tool_id = generate_tool_id(tool_name, primary_scene, scene_index)
    
    # Get summary_prompt and translate it
    summary_prompt = tool_config.get("summary_prompt", "")
    summary_cn = translate_to_chinese(summary_prompt, tool_name) if summary_prompt else ""
    
    # Build result dictionary
    result = {
        "tool_id": tool_id,
        "name": tool_name,
        "description": tool_config.get("description", ""),
        "description_cn": "",  # Placeholder for Chinese description
        "belonging_agent": tool_config.get("belonging_agent", ""),
        "scenes": scene_names,
        "alternative_tools": tool_config.get("alternative", []),
        "summary_prompt": summary_prompt,
        "summary_cn": summary_cn,
        "self_check": tool_config.get("self_check", False),
        "args_setting": tool_config.get("args_setting", None),
    }
    
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
    # Group tools by primary scene (first scene in the list)
    tools_by_scene = defaultdict(list)
    
    for tool_name, tool_config in ALL_TOOLS.items():
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
                tool_json = process_tool(tool_name, tool_config, scene_index, primary_scene)
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

