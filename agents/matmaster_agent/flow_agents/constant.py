from agents.matmaster_agent.flow_agents.expand_agent.constant import EXPAND_AGENT
from agents.matmaster_agent.flow_agents.intent_agent.constant import INTENT_AGENT
from agents.matmaster_agent.flow_agents.plan_confirm_agent.constant import (
    PLAN_CONFIRM_AGENT,
)
from agents.matmaster_agent.flow_agents.scene_agent.constant import SCENE_AGENT

# Agent Constants
MATMASTER_SUPERVISOR_AGENT = 'matmaster_supervisor_agent'

# Function-Call Constants
MATMASTER_FLOW = 'matmaster_flow'
MATMASTER_FLOW_PLANS = 'matmaster_flow_plans'
MATMASTER_GENERATE_NPS = 'matmaster_generate_nps'

UNIVERSAL_CONTEXT_FILTER_KEYWORDS = [
    INTENT_AGENT,
    EXPAND_AGENT.replace('_agent', '_schema'),
    SCENE_AGENT,
    PLAN_CONFIRM_AGENT,
]
