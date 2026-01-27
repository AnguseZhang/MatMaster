import sys
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables at the start
load_dotenv()

# Get paths from environment or use defaults
ROOT_DIR = os.path.abspath(os.getenv("ROOT_DIR", os.path.dirname(__file__)))
SRC_DIR = os.path.abspath(os.getenv("SRC_DIR", os.path.join(ROOT_DIR, "src")))
# MatMaster-main 根目录 (agent-evaluation-main 的上级目录)
MATMASTER_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))

# Add src and root to sys.path to allow imports
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
# 添加 MatMaster-main 根目录以支持 from agents.matmaster_agent 导入
if MATMASTER_ROOT not in sys.path:
    sys.path.insert(0, MATMASTER_ROOT)

def run_mcp():
    from mcp_evaluator.cli import main as mcp_main
    # Remove 'mcp' from sys.argv before passing to mcp_main
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        sys.argv.pop(1)
    return mcp_main()

def run_agent():
    # Call the new Python launcher
    from agent_evaluator.launcher import main as launcher_main
    # Remove 'agent' from sys.argv before passing to launcher_main
    if len(sys.argv) > 1 and sys.argv[1] == "agent":
        sys.argv.pop(1)
    
    # Also update os.environ for subprocesses
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    # 包含 MatMaster-main 根目录以支持 agents.matmaster_agent 导入
    # Windows 使用 ; 分隔，Unix 使用 :
    path_sep = ";" if os.name == "nt" else ":"
    new_pythonpath = path_sep.join([
        MATMASTER_ROOT,
        ROOT_DIR,
        SRC_DIR,
        os.path.join(SRC_DIR, 'agent_evaluator'),
        current_pythonpath
    ])
    os.environ["PYTHONPATH"] = new_pythonpath
    
    import asyncio
    return asyncio.run(launcher_main())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [mcp|agent] [options]")
        sys.exit(1)
        
    mode = sys.argv[1]
    if mode == "mcp":
        sys.exit(run_mcp())
    elif mode == "agent":
        sys.exit(run_agent())
    else:
        print(f"Unknown mode: {mode}. Use 'mcp' or 'agent'.")
        sys.exit(1)
