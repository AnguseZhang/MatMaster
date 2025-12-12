from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.job_agents.agent import BaseAsyncJobAgent
from agents.matmaster_agent.llm_config import LLMConfig
from agents.matmaster_agent.logger import matmodeler_logging_handler

from .constant import (
    ApexAgentName,
    ApexServerUrl,
)
from .finance import apex_cost_func
from .prompt import ApexAgentDescription, ApexAgentInstruction
from .toolset import ApexBohriumExecutor, ApexBohriumStorage

# 配置SSE参数
sse_params = SseServerParams(url=ApexServerUrl)
apex_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=ApexBohriumStorage,
    executor=ApexBohriumExecutor,
    async_mode=True,
    wait=False,
    logging_callback=matmodeler_logging_handler,
)


class ApexAgent(BaseAsyncJobAgent):
    """
    APEX材料性质计算智能体

    支持功能：
    - 材料性质计算（空位、间隙、弹性、表面、EOS、声子、γ表面）
    - 异步Bohrium任务提交和状态监控
    - 智能用户意图识别和参数转换
    - 结构文件管理和下载
    - 存储空间管理
    - Bohrium认证信息动态配置
    - 自动图片渲染为Markdown格式
    - 异步任务处理（继承BaseAsyncJobAgent）
    """

    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=ApexAgentName,
            description=ApexAgentDescription,
            instruction=ApexAgentInstruction,
            tools=[apex_toolset],
            dflow_flag=False,
            supervisor_agent=MATMASTER_AGENT_NAME,
            cost_func=apex_cost_func,
            enable_tgz_unpack=False,
        )


def init_apex_agent(llm_config) -> BaseAgent:
    """初始化APEX材料性质计算智能体"""
    return ApexAgent(llm_config)
