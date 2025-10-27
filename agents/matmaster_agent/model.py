from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from agents.matmaster_agent.ABACUS_agent.constant import ABACUS_AGENT_NAME
from agents.matmaster_agent.apex_agent.constant import ApexAgentName
from agents.matmaster_agent.chembrain_agent.constant import CHEMBRAIN_AGENT_NAME
from agents.matmaster_agent.CompDART_agent.constant import COMPDART_AGENT_NAME
from agents.matmaster_agent.document_parser_agent.constant import (
    DocumentParserAgentName,
)
from agents.matmaster_agent.DPACalculator_agent.constant import DPACalulator_AGENT_NAME
from agents.matmaster_agent.finetune_dpa_agent.constant import FinetuneDPAAgentName
from agents.matmaster_agent.HEA_assistant_agent.constant import HEA_assistant_AgentName
from agents.matmaster_agent.HEACalculator_agent.constant import HEACALCULATOR_AGENT_NAME
from agents.matmaster_agent.MrDice_agent.constant import MrDice_Agent_Name
from agents.matmaster_agent.organic_reaction_agent.constant import (
    ORGANIC_REACTION_AGENT_NAME,
)
from agents.matmaster_agent.perovskite_agent.constant import PerovskiteAgentName
from agents.matmaster_agent.piloteye_electro_agent.constant import (
    PILOTEYE_ELECTRO_AGENT_NAME,
)
from agents.matmaster_agent.ssebrain_agent.constant import SSEBRAIN_AGENT_NAME
from agents.matmaster_agent.structure_generate_agent.constant import (
    StructureGenerateAgentName,
)
from agents.matmaster_agent.superconductor_agent.constant import SuperconductorAgentName
from agents.matmaster_agent.thermoelectric_agent.constant import ThermoelectricAgentName
from agents.matmaster_agent.traj_analysis_agent.constant import TrajAnalysisAgentName


class JobStatus(str, Enum):
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'


class JobResultType(str, Enum):
    RegularFile = 'RegularFile'
    MatModelerFile = 'MatModelerFile'
    Value = 'Value'


class JobResult(BaseModel):
    name: str
    data: Union[int, float, str]
    url: Optional[str] = ''
    type: JobResultType


class BohrJobInfo(BaseModel):
    origin_job_id: str
    job_id: Union[int, str]
    job_detail_url: str
    job_status: JobStatus
    job_name: str
    job_result: Optional[List[JobResult]] = None
    job_in_ctx: bool = False
    agent_name: str
    resource_type: Optional[str] = 'sandbox'


class DFlowJobInfo(BaseModel):
    origin_job_id: str
    job_name: str
    job_status: JobStatus
    workflow_id: str
    workflow_uid: str
    workflow_url: str
    job_result: Optional[List[JobResult]] = None
    job_in_ctx: bool = False


class ParamsCheckComplete(BaseModel):
    flag: bool
    reason: str
    analyzed_messages: List[str]


class MatMasterTargetAgentEnum(str, Enum):
    ABACUSAgent = ABACUS_AGENT_NAME
    APEXAgent = ApexAgentName
    ChemBrainAgent = CHEMBRAIN_AGENT_NAME
    DocumentParserAgent = DocumentParserAgentName
    DPACalculatorAgent = DPACalulator_AGENT_NAME
    HEAAssistantAgent = HEA_assistant_AgentName
    HEACalculatorAgent = HEACALCULATOR_AGENT_NAME
    CompDARTAgent = COMPDART_AGENT_NAME
    MrDiceAgent = MrDice_Agent_Name
    OrganicReactionAgent = ORGANIC_REACTION_AGENT_NAME
    PerovskiteAgent = PerovskiteAgentName
    PiloteyeElectroAgent = PILOTEYE_ELECTRO_AGENT_NAME
    SSEBrainAgent = SSEBRAIN_AGENT_NAME
    StructureGenerateAgent = StructureGenerateAgentName
    SuperConductorAgent = SuperconductorAgentName
    ThermoElectricAgent = ThermoelectricAgentName
    TrajAnalysisAgent = TrajAnalysisAgentName
    FinetuneDPAAgent = FinetuneDPAAgentName


class UserContent(BaseModel):
    language: str
