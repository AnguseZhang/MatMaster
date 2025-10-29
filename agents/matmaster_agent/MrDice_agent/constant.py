from enum import Enum

MrDice_Agent_Name = 'MrDice_agent'


class MrDiceTargetAgentEnum(Enum):
    """MrDice 子代理枚举"""

    BOHRIUMPUBLIC_AGENT = 'bohriumpublic_agent'
    OPTIMADE_AGENT = 'optimade_agent'
    OPENLAM_AGENT = 'openlam_agent'
    MOFDB_AGENT = 'mofdb_agent'
