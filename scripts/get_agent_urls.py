#!/usr/bin/env python3
"""
Get agent URLs for all environments by parsing constant.py files
"""
import ast
import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def extract_urls_from_file(file_path: Path) -> dict:
    """
    Extract URLs for test, uat, prod from a constant.py file.
    Returns: {test: url, uat: url, prod: url}
    """
    urls = {'test': None, 'uat': None, 'prod': None}
    
    if not file_path.exists():
        return urls
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find URL variable name (look for variables ending in URL or ServerUrl)
        url_var_pattern = r'(\w*(?:URL|ServerUrl|_URL|_SERVER_URL))\s*='
        url_vars = re.findall(url_var_pattern, content)
        
        if not url_vars:
            return urls
        
        url_var = url_vars[0]  # Use first URL variable found
        
        # Extract URLs by finding the assignment and extracting the quoted string
        # Handle both single-line and multi-line assignments
        
        # Pattern for test/uat together
        test_uat_block = re.search(
            rf"if\s+CURRENT_ENV\s+in\s*\[['\"]test['\"],\s*['\"]uat['\"]\]:.*?{url_var}\s*=\s*",
            content,
            re.DOTALL
        )
        if test_uat_block:
            remaining = content[test_uat_block.end():]
            # Support multi-line assignments with parentheses
            lines = remaining.split('\n')
            url_found = None
            for i, line in enumerate(lines[:10]):
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                # Try to find URL on same line
                url_match = re.search(r"['\"]([^'\"]+)['\"]", line)
                if url_match:
                    url_found = url_match.group(1).strip()
                    break
                # If line ends with '(' or '=', check next line(s) for URL
                if line.rstrip().endswith(('(', '=')) or re.search(rf'{url_var}\s*=\s*\(', line):
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line.startswith('#'):
                            continue
                        url_match = re.search(r"['\"]([^'\"]+)['\"]", next_line)
                        if url_match:
                            url_found = url_match.group(1).strip()
                            break
                    if url_found:
                        break
                # Stop if we hit another conditional block
                if re.match(r'\s*(if|elif|else)\s*:', line):
                    break
            if url_found:
                urls['test'] = url_found
                urls['uat'] = url_found
        
        # Pattern for test only
        # Support both:
        #   if CURRENT_ENV == 'test':
        #   if CURRENT_ENV in ['test']:
        if not urls['test']:
            test_patterns = [
                rf"(if|elif)\s+CURRENT_ENV\s*==\s*['\"]test['\"]\s*:.*?{url_var}\s*=\s*",
                rf"(if|elif)\s+CURRENT_ENV\s+in\s*\[['\"]test['\"]\]\s*:.*?{url_var}\s*=\s*",
            ]
            for pattern in test_patterns:
                test_block = re.search(pattern, content, re.DOTALL)
                if test_block:
                    remaining = content[test_block.end():]
                    # Support multi-line assignments
                    lines = remaining.split('\n')
                    for i, line in enumerate(lines[:10]):
                        stripped = line.strip()
                        if stripped.startswith('#'):
                            continue
                        url_match = re.search(r"['\"]([^'\"]+)['\"]", line)
                        if url_match:
                            urls['test'] = url_match.group(1).strip()
                            break
                        # Check for multi-line assignment
                        if line.rstrip().endswith(('(', '=')) or re.search(rf'{url_var}\s*=\s*\(', line):
                            for j in range(i + 1, min(i + 5, len(lines))):
                                next_line = lines[j].strip()
                                if next_line.startswith('#'):
                                    continue
                                url_match = re.search(r"['\"]([^'\"]+)['\"]", next_line)
                                if url_match:
                                    urls['test'] = url_match.group(1).strip()
                                    break
                            if urls['test']:
                                break
                        if re.match(r'\s*(if|elif|else)\s*:', line):
                            break
                    if urls['test']:
                        break
        
        # Pattern for uat only
        # Support both:
        #   elif CURRENT_ENV == 'uat':
        #   elif CURRENT_ENV in ['uat']:
        if not urls['uat']:
            uat_patterns = [
                rf"elif\s+CURRENT_ENV\s*==\s*['\"]uat['\"]\s*:.*?{url_var}\s*=\s*",
                rf"elif\s+CURRENT_ENV\s+in\s*\[['\"]uat['\"]\]\s*:.*?{url_var}\s*=\s*",
            ]
            for pattern in uat_patterns:
                uat_block = re.search(pattern, content, re.DOTALL)
                if uat_block:
                    remaining = content[uat_block.end():]
                    # Support multi-line assignments
                    lines = remaining.split('\n')
                    for i, line in enumerate(lines[:10]):
                        stripped = line.strip()
                        if stripped.startswith('#'):
                            continue
                        url_match = re.search(r"['\"]([^'\"]+)['\"]", line)
                        if url_match:
                            urls['uat'] = url_match.group(1).strip()
                            break
                        # Check for multi-line assignment
                        if line.rstrip().endswith(('(', '=')) or re.search(rf'{url_var}\s*=\s*\(', line):
                            for j in range(i + 1, min(i + 5, len(lines))):
                                next_line = lines[j].strip()
                                if next_line.startswith('#'):
                                    continue
                                url_match = re.search(r"['\"]([^'\"]+)['\"]", next_line)
                                if url_match:
                                    urls['uat'] = url_match.group(1).strip()
                                    break
                            if urls['uat']:
                                break
                        if re.match(r'\s*(if|elif|else)\s*:', line):
                            break
                    if urls['uat']:
                        break
        
        # Pattern for prod (else block)
        # Find else block and then search for URL assignment in subsequent lines
        else_match = re.search(r'else\s*:', content)
        if else_match:
            remaining = content[else_match.end():]
            # Look for URL assignment in the else block (stop at next if/elif/else or end of function)
            # Find the URL assignment line (may be on same line or next few lines)
            # Support multi-line assignments with parentheses
            lines = remaining.split('\n')
            for i, line in enumerate(lines[:10]):  # Check first 10 lines after else
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                # Check if this line contains the URL assignment
                if url_var in line and '=' in line:
                    # Try to find URL on same line first
                    url_match = re.search(r"['\"]([^'\"]+)['\"]", line)
                    if url_match:
                        urls['prod'] = url_match.group(1).strip()
                        break
                    # If line ends with '(' or '=', check next line(s) for URL (multi-line assignment)
                    if line.rstrip().endswith(('(', '=')) or re.search(rf'{url_var}\s*=\s*\(', line):
                        # Look ahead for URL string in next few lines
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            if next_line.startswith('#'):
                                continue
                            url_match = re.search(r"['\"]([^'\"]+)['\"]", next_line)
                            if url_match:
                                urls['prod'] = url_match.group(1).strip()
                                break
                        if urls['prod']:
                            break
                # Stop if we hit another conditional block
                if re.match(r'\s*(if|elif|else)\s*:', line):
                    break
        
        # If no conditional found, look for direct assignment
        if not any(urls.values()):
            direct_match = re.search(rf"{url_var}\s*=\s*['\"]([^'\"]+)['\"]", content)
            if direct_match:
                url = direct_match.group(1).strip()
                urls['test'] = url
                urls['uat'] = url
                urls['prod'] = url
                
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
    
    return urls


def get_urls_for_all_environments():
    """
    Get URLs for all agents in all environments.
    Returns: {agent_name: {test: url, uat: url, prod: url}}
    """
    # Agent name to constant file path mapping
    agent_mappings = {
        'ABACUS_calculation_agent': project_root / 'agents/matmaster_agent/sub_agents/ABACUS_agent/constant.py',
        'apex_agent': project_root / 'agents/matmaster_agent/sub_agents/apex_agent/constant.py',
        'dpa_calculator_agent': project_root / 'agents/matmaster_agent/sub_agents/DPACalculator_agent/constant.py',
        'finetune_dpa_agent': project_root / 'agents/matmaster_agent/sub_agents/finetune_dpa_agent/constant.py',
        'LAMMPS_agent': project_root / 'agents/matmaster_agent/sub_agents/LAMMPS_agent/constant.py',
        'structure_generate_agent': project_root / 'agents/matmaster_agent/sub_agents/structure_generate_agent/constant.py',
        'convexhull_agent': project_root / 'agents/matmaster_agent/sub_agents/convexhull_agent/constant.py',
        'superconductor_agent': project_root / 'agents/matmaster_agent/sub_agents/superconductor_agent/constant.py',
        'thermoelectric_agent': project_root / 'agents/matmaster_agent/sub_agents/thermoelectric_agent/constant.py',
        'traj_analysis_agent': project_root / 'agents/matmaster_agent/sub_agents/traj_analysis_agent/constant.py',
        'visualizer_agent': project_root / 'agents/matmaster_agent/sub_agents/visualizer_agent/constant.py',
        'optimade_agent': project_root / 'agents/matmaster_agent/sub_agents/MrDice_agent/optimade_agent/constant.py',
        'bohriumpublic_agent': project_root / 'agents/matmaster_agent/sub_agents/MrDice_agent/bohriumpublic_agent/constant.py',
        'openlam_agent': project_root / 'agents/matmaster_agent/sub_agents/MrDice_agent/openlam_agent/constant.py',
        'mofdb_agent': project_root / 'agents/matmaster_agent/sub_agents/MrDice_agent/mofdb_agent/constant.py',
        'perovskite_research_agent': project_root / 'agents/matmaster_agent/sub_agents/perovskite_agent/constant.py',
        'doe_agent': project_root / 'agents/matmaster_agent/sub_agents/doe_agent/constant.py',
        'compdart_agent': project_root / 'agents/matmaster_agent/sub_agents/CompDART_agent/constant.py',
        'document_parser_agent': project_root / 'agents/matmaster_agent/sub_agents/document_parser_agent/constant.py',
        'electron_microscope_agent': project_root / 'agents/matmaster_agent/sub_agents/Electron_Microscope_agent/constant.py',
        'xrd_agent': project_root / 'agents/matmaster_agent/sub_agents/XRD_agent/constant.py',
        'tpd_agent': project_root / 'agents/matmaster_agent/sub_agents/TPD_agent/constant.py',
        'physical_adsorption_agent': project_root / 'agents/matmaster_agent/sub_agents/Physical_adsorption_agent/constant.py',
        'science_navigator_agent': project_root / 'agents/matmaster_agent/sub_agents/ScienceNavigator_agent/constant.py',
        'nmr_agent': project_root / 'agents/matmaster_agent/sub_agents/NMR_agent/constant.py',
        'vaspkit_agent': project_root / 'agents/matmaster_agent/sub_agents/vaspkit_agent/constant.py',
        'HEAkb_agent': project_root / 'agents/matmaster_agent/sub_agents/HEAkb_agent/constant.py',
        'SSEkb_agent': project_root / 'agents/matmaster_agent/sub_agents/SSEkb_agent/constant.py',
        'POLYMERkb_agent': project_root / 'agents/matmaster_agent/sub_agents/POLYMERkb_agent/constant.py',
        'STEELkb_agent': project_root / 'agents/matmaster_agent/sub_agents/STEELkb_agent/constant.py',
        'STEEL_PREDICT_agent': project_root / 'agents/matmaster_agent/sub_agents/STEEL_PREDICT_agent/constant.py',
        'unielf_agent': project_root / 'agents/matmaster_agent/sub_agents/chembrain_agent/unielf_agent/constant.py',
        'hea_calculator_agent': project_root / 'agents/matmaster_agent/sub_agents/HEACalculator_agent/constant.py',
        'HEA_assistant_agent': project_root / 'agents/matmaster_agent/sub_agents/HEA_assistant_agent/constant.py',
        'organic_reaction_agent': project_root / 'agents/matmaster_agent/sub_agents/organic_reaction_agent/constant.py',
        'piloteye_electro_agent': project_root / 'agents/matmaster_agent/sub_agents/piloteye_electro_agent/constant.py',
    }
    
    url_mapping = {}
    
    for agent_name, constant_file in agent_mappings.items():
        urls = extract_urls_from_file(constant_file)
        url_mapping[agent_name] = urls
    
    return url_mapping


if __name__ == "__main__":
    mapping = get_urls_for_all_environments()
    import json
    print(json.dumps(mapping, indent=2, ensure_ascii=False))

