from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseSyncAgent
from agents.matmaster_agent.constant import BohriumStorge
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.sub_agents.traj_analysis_agent.constant import (
    TrajAnalysisAgentName,
    TrajAnalysisMCPServerUrl,
)

traj_analysis_toolset = CalculationMCPToolset(
    connection_params=SseServerParams(url=TrajAnalysisMCPServerUrl),
    storage=BohriumStorge,
)


def init_traj_analysis_agent(llm_config: LLMConfig) -> BaseAgent:
    return BaseSyncAgent(
        model=llm_config.default_litellm_model,
        name=TrajAnalysisAgentName,
        description='An agent designed to perform trajectory analysis, including calculations like '
        'Solvation Structure Analysis, Mean Squared Displacement (MSD), Radial Distribution Function (RDF), '
        'Bond Length Analysis, and Reaction Network Analysis, with visualization support for MSD and RDF.',
        instruction="""
        This agent specializes in analyzing molecular dynamics (MD) simulation trajectories,
        with the following key functionalities:

        Solvation Structure Analysis:
        1. Analyze SSIP/CIP/AGG ratios for electrolytes
        2. Calculate coordination numbers of solvents

        Mean Squared Displacement (MSD) Analysis:
        - Calculates and plots MSD curves for the system
        - Supports exporting MSD calculation results as data files
        - Allows computation for specific atom groups (requires user-provided atom indices/types)
        - If no atoms are specified, calculates MSD for all atoms by default
        - Supports various trajectory formats including VASP (XDATCAR/vasprun.xml), LAMMPS (dump), GROMACS (.trr/.xtc), and extxyz
        - Provides visualization output of the MSD curve

        Radial Distribution Function (RDF) Analysis:
        - Computes and plots RDF curves for different atom pairs
        - Supports specifying central and neighboring atom types
        - If no atom types are specified, calculates RDF for all atom pairs by default
        - Supports various trajectory formats including VASP, LAMMPS, GROMACS, and extxyz
        - Provides visualization output of the RDF curve

        Bond Length Analysis:
        - Calculates bond length evolution over time for specified atom pairs
        - Supports defining bonds based on a cutoff distance
        - Provides data file outputs
        - Supports various trajectory formats including VASP, LAMMPS, GROMACS, and extxyz

        Reaction Network Analysis:
        - Performs comprehensive reaction network analysis using ReacNetGenerator
        - Identifies molecular species and tracks their transformations throughout the simulation
        - Generates reaction networks and pathways
        - Supports LAMMPS dump and extxyz trajectory formats

        Visualization Output:
        - Visualization is provided for MSD and RDF analyses only
        - Data files are provided for further analysis when applicable

        File Format Support:
        - VASP: XDATCAR, vasprun.xml (requires INCAR for some analyses)
        - LAMMPS: dump files (requires input file for some analyses)
        - GROMACS: .trr, .xtc (requires topology file)
        - extxyz: extended xyz format

        Atom Selection Syntax:
        Different trajectory formats use different atom selection syntaxes:
        - VASP/GROMACS: Use 'name', e.g., "name O" or ["name O","name H"]
        - LAMMPS: Use 'type', e.g., "type 1" or ["type 1","type 2"]
        - extxyz: Use 'type' with element symbols, e.g., "type Na" or ["type Na","type Cl"]
        - General MDAnalysis syntax also supported: 'index', 'resid', 'filter', etc.

        Example Queries:
        - "分析LiTFSI溶液的溶剂化结构"
        - "计算这个轨迹文件的MSD，原子组为O和H"
        - "计算Na和Cl之间的RDF"
        - "分析两个原子之间的键长随时间的变化"
        - "对这个分子动力学轨迹进行反应网络分析"
        """,
        tools=[traj_analysis_toolset],
    )
