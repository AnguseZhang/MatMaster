from agents.matmaster_agent.flow_agents.expand_agent.constant import EXPAND_AGENT
from agents.matmaster_agent.flow_agents.intent_agent.constant import INTENT_AGENT
from agents.matmaster_agent.flow_agents.scene_agent.constant import SCENE_AGENT

# Agent Constants
MATMASTER_SUPERVISOR_AGENT = 'matmaster_supervisor_agent'

# Function-Call Constants
MATMASTER_FLOW = 'matmaster_flow'
MATMASTER_FLOW_PLANS = 'matmaster_flow_plans'
MATMASTER_GENERATE_NPS = 'matmaster_generate_nps'
# 前端 demo 工具名；ADK 只下发 function_call，等前端执行后回传 function_response 再继续
DEMO_FRONTEND_TOOL = 'demo_frontend_tool'
# 前端 tool 返回值写入 session.state 的 key，后续逻辑可用 ctx.session.state[DEMO_FRONTEND_TOOL_RESULT_STATE_KEY] 读取
DEMO_FRONTEND_TOOL_RESULT_STATE_KEY = 'demo_frontend_tool_result'

# matmaster_flow 展示文案，直接传给前端（正常执行无标签则传空字符串）
EXECUTION_TYPE_LABEL_RETRY = '重试工具'
EXECUTION_TYPE_LABEL_CHANGE_TOOL = '已更换工具'

UNIVERSAL_CONTEXT_FILTER_KEYWORDS = [
    INTENT_AGENT,
    EXPAND_AGENT.replace('_agent', '_schema'),
    SCENE_AGENT,
]
