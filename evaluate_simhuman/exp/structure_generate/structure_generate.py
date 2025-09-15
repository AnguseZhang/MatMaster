from dotenv import load_dotenv
from litellm import completion
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from bohrium import Bohrium
import httpx

load_dotenv(override=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """对话状态枚举"""
    INITIAL = "initial"
    IN_PROGRESS = "in_progress"
    SATISFIED = "satisfied"
    TIMEOUT = "timeout"

@dataclass
class ConversationGoal:
    """对话目标定义"""
    initial_question: str
    expected_outcomes: List[str]
    success_criteria: List[str]

class HumanSimulator:
    """
    简化的人类模拟器 - 用于多轮对话agent评估
    
    功能：
    1. 模拟真实用户行为
    2. 管理对话目标
    3. 生成上下文相关的响应
    4. 限制最多10轮对话
    """
    
    def __init__(self, model: str = "deepseek/deepseek-chat"):
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_state = ConversationState.INITIAL
        self.turn_count = 0
        self.start_time = None
        self.goal: Optional[ConversationGoal] = None
        
    def set_goal(self, goal: ConversationGoal):
        """设置对话目标"""
        self.goal = goal
        self.current_state = ConversationState.INITIAL
        self.turn_count = 0
        self.start_time = time.time()
        logger.info(f"设置对话目标: {goal.initial_question}")
        
    def get_initial_question(self) -> str:
        """获取初始问题"""
        if not self.goal:
            raise ValueError("未设置对话目标")
        return self.goal.initial_question
    
    def generate_response(self, agent_message: str) -> Tuple[str, bool]:
        """
        基于agent的回复生成模拟用户的响应
        
        Args:
            agent_message: agent的回复内容
            
        Returns:
            Tuple[str, bool]: (用户响应, 是否继续对话)
        """
        if not self.goal:
            raise ValueError("未设置对话目标")
            
        self.turn_count += 1
        self.conversation_history.append({
            "turn": self.turn_count,
            "agent": agent_message,
            "timestamp": time.time()
        })
        
        # 检查是否达到最大轮次（限制为10轮）
        if self.turn_count >= 10:
            self.current_state = ConversationState.TIMEOUT
            return "我们已经聊了10轮了，我想结束这个对话。", False
            
        # 生成用户响应
        user_response, should_continue = self._generate_user_response(agent_message)
        
        # 更新对话状态
        if not should_continue:
            self.current_state = ConversationState.SATISFIED
            
        self.conversation_history.append({
            "turn": self.turn_count,
            "user": user_response,
            "timestamp": time.time()
        })
        
        return user_response, should_continue
    
    def get_bohr_results(self, agent_message: str, job_id: List[str]) -> Tuple[str, bool]:
        """
        基于agent的回复生成模拟用户的响应
        
        Args:
            agent_message: agent的回复内容
            
        Returns:
            Tuple[str, bool]: (用户响应, 是否继续对话)
        """
        if not self.goal:
            raise ValueError("未设置对话目标")
            
        self.turn_count += 1
        self.conversation_history.append({
            "turn": self.turn_count,
            "agent": agent_message,
            "timestamp": time.time()
        })
        
            
        # 生成用户响应
        user_response = f'查看id为{job_id}的任务结果'
        should_continue = True
        
        # 更新对话状态
        if not should_continue:
            self.current_state = ConversationState.SATISFIED
            
        self.conversation_history.append({
            "turn": self.turn_count,
            "user": user_response,
            "timestamp": time.time()
        })
        
        return user_response, should_continue
    
    def _generate_user_response(self, agent_message: str) -> Tuple[str, bool]:
        """生成用户响应的核心逻辑"""
        
        prompt = self._build_response_prompt(agent_message)
        
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            user_response = result.get("response", "我理解了。")
            should_continue = result.get("continue", True)
            
            logger.info(f"用户响应生成 - 轮次: {self.turn_count}, 继续: {should_continue}")
            
            return user_response, should_continue
            
        except Exception as e:
            logger.error(f"生成用户响应失败: {e}")
            return "我理解了，请继续。", True
    
    def _build_response_prompt(self, agent_message: str) -> str:
        """构建生成用户响应的提示词"""
        
        conversation_context = self._format_conversation_history()
        
        return f"""
你是一个模拟用户，正在与一个材料计算AI agent进行多轮对话。请基于以下信息生成合适的响应：

对话目标：
- 初始问题: {self.goal.initial_question}
- 期望结果: {', '.join(self.goal.expected_outcomes)}
- 成功标准: {', '.join(self.goal.success_criteria)}

当前状态：
- 对话轮次: {self.turn_count}/10

Agent最新回复：
{agent_message}

请分析agent的回复是否满足任务需求，并生成合适的响应。

重要限制：
- 对话最多10轮，当前是第{self.turn_count}轮
- 除首轮对话外，其他轮次尽可能简短地回答agent的问题，回复内容紧扣初始问题，禁止发散
- 如果agent在询问具体参数或设置，提供简洁明确的回答
- 如果agent已经提供了初始任务所需的信息或完成了任务，请立刻结束对话
- 禁止回复可能导致agent产生误解或偏离目标的内容

请以JSON格式回复：
{{
    "response": "你的回复内容",
    "continue": true/false  // 是否继续对话
}}

"""
    
    def _format_conversation_history(self) -> str:
        """格式化对话历史"""
        if not self.conversation_history:
            return "无对话历史"
            
        formatted = []
        for i, entry in enumerate(self.conversation_history):
            if "agent" in entry:
                formatted.append(f"Agent: {entry['agent']}")
            elif "user" in entry:
                formatted.append(f"User: {entry['user']}")
                
        return "\n".join(formatted)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        return {
            "goal": self.goal.initial_question if self.goal else None,
            "total_turns": self.turn_count,
            "final_state": self.current_state.value,
            "duration_minutes": ((time.time() - self.start_time) / 60) if self.start_time else 0,
            "conversation_history": self.conversation_history
        }
    
    def get_last_user_response(self) -> str:
        """获取最后的用户响应"""
        if not self.conversation_history:
            return self.get_initial_question()
        
        # 查找最后一个用户响应
        for entry in reversed(self.conversation_history):
            if "user" in entry:
                return entry["user"]
        
        # 如果没有找到用户响应，返回初始问题
        return self.get_initial_question()

# 预定义的对话目标模板
class GoalTemplates:
    """对话目标模板"""
    
    @staticmethod
    def abacus_nacl_calculation() -> ConversationGoal:
        """ABACUS NaCl DFT计算目标"""
        return ConversationGoal(
            initial_question="我希望使用ABACUS对NaCl进行DFT计算，请帮我构建一个NaCl的晶胞，晶体类型为rocksalt型，晶格常数为5.5 Å，不使用立方体形式的原胞。",
            expected_outcomes=["成功构建NaCl晶胞", "获得ABACUS输入文件"],
            success_criteria=["晶胞构建完成", "获得可用的ABACUS输入文件"]
        )
    
    @staticmethod
    def fcc_copper_phonon() -> ConversationGoal:
        """FCC铜声子谱计算目标"""
        return ConversationGoal(
            initial_question="构建FCC铜并计算其声子谱",
            expected_outcomes=["构建FCC铜结构", "计算声子谱"],
            success_criteria=["FCC铜结构构建完成", "声子谱计算完成"]
        )
    
    @staticmethod
    def band_gap_structures() -> ConversationGoal:
        """寻找小带隙结构目标"""
        return ConversationGoal(
            initial_question="我想要4个band gap 小于0.5eV的结构",
            expected_outcomes=["找到4个小带隙结构", "获得结构信息"],
            success_criteria=["找到4个符合条件的结构", "获得完整的结构信息"]
        )

# 使用示例
if __name__ == "__main__":
    import asyncio
    import sys
    import os
    
    # 添加agents目录到Python路径
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
    
    # 尝试导入ADK相关模块
    try:
        from google.adk import Runner
        from google.adk.agents import RunConfig
        from google.adk.agents.run_config import StreamingMode
        from google.adk.sessions import DatabaseSessionService,InMemorySessionService
        from google.genai import types
        
        from agents.matmaster_agent.agent import root_agent,init_matmaster_agent
        from agents.matmaster_agent.constant import DBUrl
        from agents.matmaster_agent.logger import logger
        
        ADK_AVAILABLE = True
    except ImportError as e:
        print(f"警告: 无法导入ADK模块: {e}")
        print("将使用模拟的agent响应进行演示")
        ADK_AVAILABLE = False
    
    async def test_with_adk_agent():
        """与ADK agent进行多轮对话测试"""
        if not ADK_AVAILABLE:
            print("❌ ADK agent不可用，使用模拟响应")
            return await test_with_mock_agent()
        
        print("=" * 80)
        print("🤖 与ADK Agent多轮对话测试")
        print("=" * 80)
        
        # 初始化ADK agent
        # session_service = DatabaseSessionService(db_url=DBUrl)

        ### opik dataset
        from opik import Opik
        from opik.evaluation import evaluate

        os.environ["OPIK_URL_OVERRIDE"] = "https://bohrium-opik-latest.test.dp.tech/api" 
        os.environ["OPIK_WORKSPACE"] = "default"


        client = Opik()
        dataset = client.get_dataset(name="structure_generate")
        dataset_items = dataset.get_items()

        eval_results = {}
        ###
        
        
        for dataset_item in dataset_items:
            import time
            time.sleep(10)  # 避免请求过于频繁
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="matmaster_agent",
                user_id="human_simulator_test",
            )
            
            logger.info(f"Test Session: {session.id}")

            runner = Runner(
                app_name="matmaster_agent",
                agent=init_matmaster_agent(),
                session_service=session_service
            )

            # 创建人类模拟器
            simulator = HumanSimulator()

            # 数据预处理
            scenario = {
            "name":dataset_item["initial_question"],
            "goal":ConversationGoal(
                initial_question=dataset_item["initial_question"],
                expected_outcomes=dataset_item["expected_outcomes"],
                success_criteria=dataset_item["success_criteria"]
            )} 

            print(f"\n{'='*20} 测试场景: {scenario['name']} {'='*20}")
            
            # 设置对话目标
            simulator.set_goal(scenario['goal'])
            initial_question = simulator.get_initial_question()
            
            print(f"🎯 对话目标: {initial_question}")
            print(f"📋 期望结果: {', '.join(scenario['goal'].expected_outcomes)}")
            print(f"✅ 成功标准: {', '.join(scenario['goal'].success_criteria)}")

            # 初始化记录
            id = dataset_item['initial_question']
            eval_results[id] = {}
            eval_results[id]['initial_question'] = initial_question
            eval_results[id]['expected_outcomes'] = scenario['goal'].expected_outcomes
            eval_results[id]['success_criteria'] = scenario['goal'].success_criteria
            for i in range(1,6):
                eval_results[id][f'agent_response_{i}'] = ''
                eval_results[id][f'user_response_{i}'] = ''

            
            # 开始对话
            conversation_ended = False
            turn_count = 0
            
            while not conversation_ended and turn_count < 10:
                turn_count += 1
                print(f"\n🔄 第 {turn_count} 轮对话:")
                
                # 获取用户输入（从模拟器）
                if turn_count == 1:
                    user_input = initial_question
                else:
                    # 从模拟器获取响应
                    user_input = simulator.get_last_user_response()
                
                print(f"🧑 模拟用户: {user_input}")
                
                # 调用ADK agent
                try:
                    content = types.Content(role="user", parts=[types.Part(text=user_input)])
                    
                    agent_response = ""

                    events = runner.run_async(
                        user_id=session.user_id,
                        session_id=session.id,
                        new_message=content,
                        run_config=RunConfig(streaming_mode=StreamingMode.SSE)
                    )
                    
                    # 收集agent响应
                    async for event in events:
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    agent_response += part.text
                except asyncio.CancelledError:
                    logger.error("任务被取消，可能是超时或作用域取消导致")
                    agent_response = "任务被取消，无法完成请求。"
                    print(f"✅ 对话在第{turn_count}轮结束")
                    eval_results[id][f'agent_response_{turn_count}'] = "任务被取消，可能是超时或作用域取消导致"
                    break
                except Exception as e:
                    logger.error(f"获取agent响应失败: {e}")
                    agent_response = "抱歉，处理您的请求时出现问题。"
                    print(f"✅ 对话在第{turn_count}轮结束")
                    eval_results[id][f'agent_response_{turn_count}'] = str(e)
                    break
                
                eval_results[id][f'agent_response_{turn_count}'] = agent_response
                print(f"🤖 ADK Agent: {agent_response}")
                import re
                job_jsons = re.findall(r'<bohrium-chat-msg>(.*?)</bohrium-chat-msg>', agent_response)
                job_ids = []
                if job_jsons != []:
                    for job_json in job_jsons:
                        try:
                            job_json = json.loads(job_json)
                            if "eventData" in job_json and "content" in job_json["eventData"]:
                                content = job_json["eventData"]["content"]
                                if "job_list" in content and "job_id" in content["job_list"]:
                                    job_id = content["job_list"]["job_id"]
                                    job_ids.append(job_id)
                        except Exception as e:
                            logger.error(f"提取job_id失败: {e}")
                    
                # 查询job状态
                if job_ids != []:
                    job_ids = list(set(job_ids))
                    while True:
                        time.sleep(10)
                        all_finished = True
                        for job_id in job_ids:
                            bohrium_client = Bohrium()
                            job_info = bohrium_client.job.detail(job_id)
                            logger.info(f"查询到job状态: {job_id} - 状态: {job_info["status"]}")
                            if job_info["status"] not in [-1, 2]:
                                all_finished = False
                        if all_finished:
                            break

                     # 使用模拟器生成用户响应
                    user_response, should_continue = simulator.get_bohr_results(agent_response,job_ids)
                    eval_results[id][f'user_response_{turn_count}'] = user_response
                    print(f"🧑 模拟用户: {user_response}")
                else:
                    # 使用模拟器生成用户响应
                    user_response, should_continue = simulator.generate_response(agent_response)
                    eval_results[id][f'user_response_{turn_count}'] = user_response
                    print(f"🧑 模拟用户: {user_response}")
                
                if not should_continue:
                    conversation_ended = True
                    print(f"✅ 对话在第{turn_count}轮结束")
                    break
            
            # 获取对话摘要
            summary = simulator.get_conversation_summary()
            eval_results[id]['total_turns'] = summary['total_turns']
            eval_results[id]['final_state'] = summary['final_state']
            eval_results[id]['duration_minutes'] = summary['duration_minutes']
            print(f"\n📊 对话摘要:")
            print(f"   - 总轮次: {summary['total_turns']}")
            print(f"   - 最终状态: {summary['final_state']}")
            print(f"   - 耗时: {summary['duration_minutes']:.1f} 分钟")

            with open("evaluation_results.json", "w") as f:
                json.dump(eval_results, f, indent=4, ensure_ascii=False)
            
            # 简单的成功判断
            if summary['final_state'] == 'satisfied':
                print("✅ 测试通过: 对话成功完成")
            else:
                print("❌ 测试失败: 对话未成功完成")

            await runner.close()

        def task(dataset_item):
            return eval_results[dataset_item['initial_question']]
        

        evaluate(
                experiment_name="my_evaluation",
                dataset=dataset,
                task=task
                )
        
        
        print("\n" + "=" * 80)
        print("🎉 多轮对话测试完成！")
        print("=" * 80)
    
    async def test_with_mock_agent():
        """使用模拟agent进行测试"""
        print("=" * 80)
        print("🤖 与模拟Agent多轮对话测试")
        print("=" * 80)
        
        # 创建人类模拟器
        simulator = HumanSimulator()
        
        # 设置测试场景
        test_scenarios = [
            {
                "name": "ABACUS NaCl DFT计算",
                "goal": GoalTemplates.abacus_nacl_calculation(),
                "mock_responses": [
                    "您好！我可以帮助您使用ABACUS构建NaCl晶胞并进行DFT计算。请确认您需要的晶格常数是5.5 Å吗？",
                    "好的，我将为您构建rocksalt型NaCl晶胞。您希望使用什么DFT方法？比如PBE、HSE06等？",
                    "请告诉我您希望设置的截断能是多少？通常对于NaCl，建议使用50-60 Ry。",
                    "我将为您生成ABACUS输入文件。您希望保存为什么文件名？",
                    "完成！我已经为您构建了NaCl晶胞并生成了ABACUS输入文件。您可以开始计算了。"
                ]
            },
            {
                "name": "FCC铜声子谱计算", 
                "goal": GoalTemplates.fcc_copper_phonon(),
                "mock_responses": [
                    "您好！我可以帮助您构建FCC铜结构并计算声子谱。请确认您需要的是面心立方铜结构吗？",
                    "好的，我将为您构建FCC铜晶胞。您希望使用什么晶格常数？通常铜的晶格常数约为3.61 Å。",
                    "请告诉我您希望使用什么声子计算方法？比如有限位移法或密度泛函微扰理论？",
                    "我将为您设置声子计算参数。您希望计算多少个q点？",
                    "完成！我已经为您构建了FCC铜结构并设置了声子计算参数。"
                ]
            },
            {
                "name": "小带隙结构搜索",
                "goal": GoalTemplates.band_gap_structures(),
                "mock_responses": [
                    "您好！我可以帮助您寻找带隙小于0.5eV的结构。请告诉我您希望搜索什么类型的材料？",
                    "我将为您搜索候选结构。您希望使用什么计算方法？比如DFT、GW等？",
                    "请告诉我您希望搜索的化学空间范围？比如特定元素组合或结构类型？",
                    "我将为您筛选出符合条件的结构。您希望获得哪些具体信息？",
                    "完成！我已经为您找到了4个带隙小于0.5eV的结构。"
                ]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n{'='*20} 测试场景: {scenario['name']} {'='*20}")
            
            # 设置对话目标
            simulator.set_goal(scenario['goal'])
            initial_question = simulator.get_initial_question()
            
            print(f"🎯 对话目标: {initial_question}")
            print(f"📋 期望结果: {', '.join(scenario['goal'].expected_outcomes)}")
            print(f"✅ 成功标准: {', '.join(scenario['goal'].success_criteria)}")
            
            # 开始对话
            conversation_ended = False
            turn_count = 0
            
            while not conversation_ended and turn_count < len(scenario['mock_responses']):
                turn_count += 1
                print(f"\n🔄 第 {turn_count} 轮对话:")
                
                # 获取用户输入（从模拟器）
                if turn_count == 1:
                    user_input = initial_question
                else:
                    # 从模拟器获取响应
                    user_input = simulator.get_last_user_response()
                
                print(f"🧑 模拟用户: {user_input}")
                
                # 使用模拟的agent响应
                agent_response = scenario['mock_responses'][turn_count - 1]
                print(f"🤖 模拟Agent: {agent_response}")
                
                # 使用模拟器生成用户响应
                user_response, should_continue = simulator.generate_response(agent_response)
                print(f"🧑 模拟用户: {user_response}")
                
                if not should_continue:
                    conversation_ended = True
                    print(f"✅ 对话在第{turn_count}轮结束")
                    break
            
            # 获取对话摘要
            summary = simulator.get_conversation_summary()
            print(f"\n📊 对话摘要:")
            print(f"   - 总轮次: {summary['total_turns']}")
            print(f"   - 最终状态: {summary['final_state']}")
            print(f"   - 耗时: {summary['duration_minutes']:.1f} 分钟")
            
            # 简单的成功判断
            if summary['final_state'] == 'satisfied':
                print("✅ 测试通过: 对话成功完成")
            else:
                print("❌ 测试失败: 对话未成功完成")
        
        print("\n" + "=" * 80)
        print("🎉 模拟多轮对话测试完成！")
        print("=" * 80)
    
    # 运行测试
    print("🚀 人类模拟器启动")
    print("=" * 50)
    
    # 检查是否有ADK环境
    if ADK_AVAILABLE:
        print("✅ 检测到ADK环境，将使用真实ADK agent进行测试")
        asyncio.run(test_with_adk_agent())
    else:
        print("⚠️  未检测到ADK环境，将使用模拟agent进行测试")
        asyncio.run(test_with_mock_agent())