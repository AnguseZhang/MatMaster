from agents.matmaster_agent.flow_agents.expand_agent.constant import EXPAND_AGENT
from agents.matmaster_agent.flow_agents.intent_agent.constant import INTENT_AGENT
from agents.matmaster_agent.flow_agents.plan_make_agent.constant import PLAN_MAKE_AGENT
from agents.matmaster_agent.flow_agents.scene_agent.constant import SCENE_AGENT

# Agent Constants
MATMASTER_SUPERVISOR_AGENT = 'matmaster_supervisor_agent'
EXECUTION_SUMMARY_AGENT = 'execution_summary_agent'
REPORT_AGENT = 'report_agent'

# Function-Call Constants
MATMASTER_FLOW = 'matmaster_flow'
MATMASTER_FLOW_PLANS = 'matmaster_flow_plans'
MATMASTER_GENERATE_NPS = 'matmaster_generate_nps'
MATMASTER_INTENT_UI = 'matmaster_intent_ui'
MATMASTER_THINKING_UI = 'matmaster_thinking_ui'

# matmaster_flow 展示文案，直接传给前端（正常执行无标签则传空字符串）
EXECUTION_TYPE_LABEL_RETRY = '重试工具'
EXECUTION_TYPE_LABEL_CHANGE_TOOL = '已更换工具'

UNIVERSAL_CONTEXT_FILTER_KEYWORDS = [
    INTENT_AGENT,
    EXPAND_AGENT.replace('_agent', '_schema'),
    SCENE_AGENT,
]

THINKING_CONTEXT_FILTER_KEYWORDS = UNIVERSAL_CONTEXT_FILTER_KEYWORDS + [
    PLAN_MAKE_AGENT,
    MATMASTER_FLOW,
    MATMASTER_FLOW_PLANS,
    MATMASTER_GENERATE_NPS,
    EXECUTION_SUMMARY_AGENT,
    REPORT_AGENT,
]
