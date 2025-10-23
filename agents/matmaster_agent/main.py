import asyncio

from google.adk import Runner
from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from rich import print

from agents.matmaster_agent.agent import root_agent
from agents.matmaster_agent.constant import DBUrl
from agents.matmaster_agent.logger import logger

# litellm._turn_on_debug()


async def agent_main() -> None:
    """
    Main entry point for the material modeling agent application.

    This function:
    1. Initializes a new session for the user
    2. Sets up the agent runner
    3. Handles the interactive chat loop between user and agent
    4. Processes and displays agent responses in real-time

    The conversation continues until the user enters an exit command.
    """
    # Initialize session service and create new session
    session_service = DatabaseSessionService(db_url=DBUrl)
    session = await session_service.create_session(
        app_name='matmaster_agent',
        user_id='matmaster_agent_user',
    )
    logger.info(f"Current Session: {session.id}")

    # Set up the agent runner with root agent and session service
    runner = Runner(
        app_name='matmaster_agent', agent=root_agent, session_service=session_service
    )

    # Initial user prompt for material modeling
    # user_input = "使用 build_bulk_structure 创建体相铝晶体（Al），采用fcc结构，晶格常数设为4.05Å，并扩展为2×2×2超胞，输出文件命名为Al_bulk.cif"
    #   user_input = """
    #   run_molecular_dynamics 在优化后的Al体相结构(https://dp-storage-test2.oss-cn-zhangjiakou.aliyuncs.com/bohrium-test/110663/12791/store/0f23a0ea241566b00c8b401b2422457a2c2ef130/outputs/structure_file/Al_bulk.cif)上运行三阶段分子动力学模拟：
    # - 第一阶段：300K NVT系综平衡 0.2 ps
    # - 第二阶段：500K NPT系综退火 0.2 ps
    # - 第三阶段：300K NVT系综生产模拟 0.2 ps时间步长设为0.5 fs，每100步保存一次轨迹
    #   """
    # user_input = """
    # 使用 catalysis_agent 帮我计算吸附能，结构文件是：https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/11909/14844/store/upload/bac96a53-8eb2-41e0-8c71-413769df5844/ads_energy.tgz
    # """
    # user_input = ("帮我计算msd，traj=https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/48237/46562/store/upload/e8d55410-def9-47ab-bc32-d33dd3461f35/XDATCAR, "
    #               "INCAR=https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/48237/46562/store/upload/d3be80b8-b584-457d-921c-2c926878082d/INCAR")
    # user_input = "计算https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/12158/13844/store/upload/b8ec23aa-eb16-4114-bb06-b7722df7b1f2/SnSe.tgz的能带"
    # user_input = "使用NEB方法搜索H迁移的过渡态，初态结构文件： https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/11909/14844/store/upload/eab31774-4f1d-4e49-9d37-c6c8059ef704/H-trans-is-opt.poscar，末态结构文件：https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/11909/14844/store/upload/97045d53-fafc-462d-962f-2a1180df8b66/H-trans-fs-opt.poscar"
    # user_input = "请帮我查找3个包含 铝（Al）、氧（O） 和 镁（Mg） 的晶体结构。"
    # user_input = "切换到ABACUS_calculation_agent，并使用generata_bulk_structure 创建体相铝晶体（Al），采用fcc结构，晶格常数设为4.05Å"
    # user_input = "我想知道【元素组成，例：TiZrHfCoNiNb】在【计算器，例：dpa3】下的二元形成能？"
    # user_input = "高熵合金AlCoCr0.5FeNi2的可能结构是什么"
    # user_input = "调用 thermoelectric_agent 帮我生成10个具有Sn和Te元素的热电结构"
    # user_input = "plot perovstite 2021 to 2025"
    # user_input = '帮我创建一个 FCC Bulk Cu 的结构'
    # user_input = "帮我用DPA优化这个结构：https://dp-storage-test2.oss-cn-zhangjiakou.aliyuncs.com/bohrium-test/110663/12791/store/7ba41529-5af4-4e38-a6fb-c569cd769dd9/outputs/structure_paths/structure_bulk.cif"
    # user_input = "帮我检索TiO2"
    # user_input = "请你为我搭建一个氯化钠的结构"
    # user_input = '我想要一个bandgap 小于0.5ev的结构，空间群225，生成数量1'
    # user_input = '用openlam查找一个TiO2'
    user_input = '对 NbSe₂ 超导体进行声子谱计算并结合电子–声子耦合分析估算临界温度 Tc（从开源数据库获取初始结构并自行设定参数），并以 URL 导出声子谱与 e–ph 计算结果'
    print(f"🧑 用户：{user_input}")

    # Create the initial content with user input
    content = types.Content(role='user', parts=[types.Part(text=user_input)])

    # Main conversation loop
    while True:
        # Execute the agent with the current user input
        events = runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )

        # Process and display agent responses
        async for event in events:
            logger.debug(f"Event received: {event}")

            # Extract and display text content from event
            if not event.partial and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        role = event.content.role
                        if role == 'user':
                            print(f"🧑 用户：{part.text}")
                        elif role == 'model':
                            print(f"🤖 智能体：{part.text}")

        # Get next user input
        user_input = input('🧑 用户：')

        # Skip empty inputs
        if not user_input or not user_input.strip():
            continue

        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'q']:
            break

        # Prepare content for next iteration
        content = types.Content(role='user', parts=[types.Part(text=user_input)])

    # Clean up resources
    await runner.close()


if __name__ == '__main__':
    asyncio.run(agent_main())
