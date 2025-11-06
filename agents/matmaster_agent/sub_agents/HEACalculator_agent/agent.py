import copy

from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import BaseAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from agents.matmaster_agent.base_agents.public_agent import BaseSyncAgent
from agents.matmaster_agent.constant import (  # BohriumExecutor,
    LOCAL_EXECUTOR,
    BohriumStorge,
)
from agents.matmaster_agent.llm_config import LLMConfig

from .constant import HEACALCULATOR_AGENT_NAME, HEACALCULATOR_SERVER_URL
from .prompt import HEACALC_AGENT_DESCRIPTION, HEACALC_AGENT_INSTRUCTION

HEACalc_BohriumStorge = copy.deepcopy(BohriumStorge)
# HEACalc_BohriumExecutor = copy.deepcopy(BohriumExecutor)
# HEACalc_BohriumExecutor["machine"]["remote_profile"][
#    "image_address"] = "registry.dp.tech/dptech/dp/native/prod-22028/hea-calculator:demo"

sse_params = SseServerParams(url=HEACALCULATOR_SERVER_URL)

hea_calculator_toolset = CalculationMCPToolset(
    connection_params=sse_params,
    storage=HEACalc_BohriumStorge,
    executor=LOCAL_EXECUTOR,  # HEACalc_BohriumExecutor
)


class HEACalculatorAgentBase(BaseSyncAgent):
    def __init__(self, llm_config: LLMConfig):
        super().__init__(
            model=llm_config.default_litellm_model,
            name=HEACALCULATOR_AGENT_NAME,
            description=HEACALC_AGENT_DESCRIPTION,
            instruction=HEACALC_AGENT_INSTRUCTION,
            tools=[hea_calculator_toolset],
        )


def init_hea_calculator_agent(llm_config=None, use_deepseek=False) -> BaseAgent:
    if llm_config is None:
        # 如果没有提供llm_config，使用默认配置
        from agents.matmaster_agent.llm_config import MatMasterLlmConfig

        llm_config = MatMasterLlmConfig

    if use_deepseek:
        # 创建使用DeepSeek的配置
        from agents.matmaster_agent.llm_config import create_default_config

        deepseek_config = create_default_config()
        # 确保DeepSeek模型已初始化
        if hasattr(deepseek_config, 'deepseek_chat'):
            print('使用DeepSeek模型配置')
            llm_config = deepseek_config

    return HEACalculatorAgentBase(llm_config)


# 创建独立的root_agent实例供ADK使用
# try:
#    from agents.matmaster_agent.llm_config import MatMasterLlmConfig
#    root_agent = init_apex_agent(MatMasterLlmConfig, use_deepseek=True)
# except ImportError:
# 如果导入失败，设置为None
#    root_agent = None
# def init_HEACalculator_agent(llm_config, use_deepseek=False) -> BaseAgent:
#    return HEACalculatorAgent(llm_config)
