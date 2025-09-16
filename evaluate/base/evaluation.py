import asyncio
import json
import logging
import re
import time
import uuid

from bohrium import Bohrium
from dotenv import load_dotenv, find_dotenv
from google.adk import Runner
from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.matmaster_agent.agent import root_agent
from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME
from agents.matmaster_agent.utils.event_utils import is_function_call
from evaluate.base.human_simulator import ConversationGoal, HumanSimulator
from evaluate.utils import load_dataset_json

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())


def evaluation_task(dataset_item):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=MATMASTER_AGENT_NAME, session_service=session_service)
    session = asyncio.run(session_service.create_session(
        app_name=MATMASTER_AGENT_NAME,
        user_id='evaluator',
        session_id=uuid.uuid4().hex
    ))

    expected_function_call = {}
    if dataset_item['input'].get('contents', None):
        user_query = dataset_item['input']['contents'][0]['parts'][0]['text']
    else:
        user_query = dataset_item['input']['parts'][0]['text']

    for part in dataset_item['expected_output']['content']['parts']:
        if part.get('function_call'):
            expected_function_call = {
                'function_name': part['function_call']['name'],
                'function_args': part['function_call']['args']
            }

    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_call = {}
    for event in runner.run(user_id=session.user_id, session_id=session.id, new_message=content):
        events.append(event)
        if is_function_call(event):
            function_call = {
                'function_name': event.content.parts[0].function_call.name,
                'function_args': event.content.parts[0].function_call.args
            }
            break

    output = events[-1].content.parts[0].text
    result = {
        'input': user_query,
        'output': output,
        'function_call': function_call,
        'expected_function_call': expected_function_call,
        'context': []
    }
    return result


def multi_turn_evaluation_task(dataset_item):
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=MATMASTER_AGENT_NAME, session_service=session_service)
    session = asyncio.run(session_service.create_session(
        app_name=MATMASTER_AGENT_NAME,
        user_id='evaluator',
        session_id=uuid.uuid4().hex
    ))

    expected_function_call = {}
    turn_index = 2
    if dataset_item['input'].get('contents', None):
        user_query = ''
        for input_part in dataset_item['input']['contents'][:turn_index]:
            input_part_text = input_part['parts'][0]['text']
            input_part_role = input_part['role']
            user_query += f"For context: [{input_part_role}]\n{input_part_text}\n"
            user_query += '---------------------\n'
        user_query += dataset_item['input']['contents'][turn_index]['parts'][0]['text']
    else:
        user_query = dataset_item['input']['parts'][0]['text']
        if dataset_item['expected_output']['content']['parts'][0].get('function_call'):
            expected_function_call = {
                'function_name': dataset_item['expected_output']['content']['parts'][0]['function_call']['name'],
                'function_args': dataset_item['expected_output']['content']['parts'][0]['function_call']['args']
            }

    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_call = {}
    for event in runner.run(user_id=session.user_id, session_id=session.id, new_message=content):
        events.append(event)

    output = events[-1].content.parts[0].text
    result = {
        'input': user_query,
        'output': output,
        'function_call': function_call,
        'expected_function_call': expected_function_call,
        'context': []
    }
    return result


async def evaluation_threads_task(file_path, max_turn_count=10):
    """与ADK agent进行多轮对话测试"""
    print('=' * 80)
    print('🤖 与ADK Agent多轮对话测试')
    print('=' * 80)

    dataset_json = json.loads(load_dataset_json(file_path))
    eval_results = []
    for index, dataset_item in enumerate(dataset_json):
        time.sleep(10)  # 避免请求过于频繁
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name='matmaster_agent',
            user_id='human_simulator_test',
        )

        logger.info(f"Test Session: {session.id}")

        runner = Runner(
            app_name='matmaster_agent',
            agent=root_agent,
            session_service=session_service
        )

        # 创建人类模拟器
        simulator = HumanSimulator(max_turn_count=max_turn_count)

        # 数据预处理
        scenario = {
            'name': dataset_item['initial_question'],
            'goal': ConversationGoal(
                initial_question=dataset_item['initial_question'],
                expected_outcomes=dataset_item['expected_outcomes'],
                success_criteria=dataset_item['success_criteria']
            )}

        print(f"\n{'=' * 20} 测试场景: {scenario['name']} {'=' * 20}")

        # 设置对话目标
        simulator.set_goal(scenario['goal'])
        initial_question = simulator.get_initial_question()

        print(f"🎯 对话目标: {initial_question}")
        print(f"📋 期望结果: {', '.join(scenario['goal'].expected_outcomes)}")
        print(f"✅ 成功标准: {', '.join(scenario['goal'].success_criteria)}")

        # 初始化记录
        eval_results.append({})
        eval_results[index]['initial_question'] = initial_question
        eval_results[index]['expected_outcomes'] = scenario['goal'].expected_outcomes
        eval_results[index]['success_criteria'] = scenario['goal'].success_criteria
        for i in range(1, 6):
            eval_results[index][f'agent_response_{i}'] = ''
            eval_results[index][f'user_response_{i}'] = ''

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
                content = types.Content(role='user', parts=[types.Part(text=user_input)])

                agent_response = ''

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
                logger.error('任务被取消，可能是超时或作用域取消导致')
                print(f"✅ 对话在第{turn_count}轮结束")
                eval_results[index][f'agent_response_{turn_count}'] = '任务被取消，可能是超时或作用域取消导致'
                break
            except Exception as e:
                logger.error(f"获取agent响应失败: {e}")
                print(f"✅ 对话在第{turn_count}轮结束")
                eval_results[index][f'agent_response_{turn_count}'] = str(e)
                break

            eval_results[index][f'agent_response_{turn_count}'] = agent_response
            print(f"🤖 ADK Agent: {agent_response}")

            job_jsons = re.findall(r'<bohrium-chat-msg>(.*?)</bohrium-chat-msg>', agent_response)
            job_ids = []
            if job_jsons:
                for job_json in job_jsons:
                    try:
                        job_json = json.loads(job_json)
                        if 'eventData' in job_json and 'content' in job_json['eventData']:
                            content = job_json['eventData']['content']
                            if 'job_list' in content and 'job_id' in content['job_list']:
                                job_id = content['job_list']['job_id']
                                job_ids.append(job_id)
                    except Exception as e:
                        logger.error(f"提取job_id失败: {e}")

            # 查询job状态
            if job_ids:
                job_ids = list(set(job_ids))
                while True:
                    time.sleep(10)
                    all_finished = True
                    for job_id in job_ids:
                        bohrium_client = Bohrium()
                        job_info = bohrium_client.job.detail(job_id)
                        logger.info(f"查询到job状态: {job_id} - 状态: {job_info["status"]}")
                        if job_info['status'] not in [-1, 2]:
                            all_finished = False
                    if all_finished:
                        break

                # 使用模拟器生成用户响应
                user_response, should_continue = simulator.get_bohr_results(agent_response, job_ids)
                eval_results[index][f'user_response_{turn_count}'] = user_response
                print(f"🧑 模拟用户: {user_response}")
            else:
                # 使用模拟器生成用户响应
                user_response, should_continue = simulator.generate_response(agent_response)
                eval_results[index][f'user_response_{turn_count}'] = user_response
                print(f"🧑 模拟用户: {user_response}")

            if not should_continue:
                print(f"✅ 对话在第{turn_count}轮结束")
                break

        # 获取对话摘要
        summary = simulator.get_conversation_summary()
        eval_results[index]['total_turns'] = summary['total_turns']
        eval_results[index]['final_state'] = summary['final_state']
        eval_results[index]['duration_minutes'] = summary['duration_minutes']
        print(f"\n📊 对话摘要:")
        print(f"   - 总轮次: {summary['total_turns']}")
        print(f"   - 最终状态: {summary['final_state']}")
        print(f"   - 耗时: {summary['duration_minutes']:.1f} 分钟")

        with open('evaluation_results.json', 'w') as f:
            json.dump(eval_results, f, indent=4, ensure_ascii=False)

        # 简单的成功判断
        if summary['final_state'] == 'satisfied':
            print('✅ 测试通过: 对话成功完成')
        else:
            print('❌ 测试失败: 对话未成功完成')

        await runner.close()

    print('\n' + '=' * 80)
    print('🎉 多轮对话测试完成！')
    print('=' * 80)


async def evaluation_threads_single_task(file_path, item_id, max_turn_count=10):
    """与ADK agent进行多轮对话测试"""
    print('=' * 80)
    print('🤖 与ADK Agent多轮对话测试')
    print('=' * 80)

    dataset_json = json.loads(load_dataset_json(file_path))
    eval_results = {}
    dataset_item = dataset_json[item_id]

    time.sleep(10)  # 避免请求过于频繁
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name='matmaster_agent',
        user_id='human_simulator_test',
    )

    logger.info(f"Test Session: {session.id}")

    runner = Runner(
        app_name='matmaster_agent',
        agent=root_agent,
        session_service=session_service
    )

    # 创建人类模拟器
    simulator = HumanSimulator(max_turn_count=max_turn_count)

    # 数据预处理
    scenario = {
        'name': dataset_item['initial_question'],
        'goal': ConversationGoal(
            initial_question=dataset_item['initial_question'],
            expected_outcomes=dataset_item['expected_outcomes'],
            success_criteria=dataset_item['success_criteria']
        )}

    print(f"\n{'=' * 20} 测试场景: {scenario['name']} {'=' * 20}")

    # 设置对话目标
    simulator.set_goal(scenario['goal'])
    initial_question = simulator.get_initial_question()

    print(f"🎯 对话目标: {initial_question}")
    print(f"📋 期望结果: {', '.join(scenario['goal'].expected_outcomes)}")
    print(f"✅ 成功标准: {', '.join(scenario['goal'].success_criteria)}")

    # 初始化记录
    eval_results['initial_question'] = initial_question
    eval_results['expected_outcomes'] = scenario['goal'].expected_outcomes
    eval_results['success_criteria'] = scenario['goal'].success_criteria
    for i in range(1, max_turn_count+1):
        eval_results[f'agent_response_{i}'] = ''
        eval_results[f'user_response_{i}'] = ''

    # 开始对话
    conversation_ended = False
    turn_count = 0

    while not conversation_ended and turn_count < max_turn_count:
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
            content = types.Content(role='user', parts=[types.Part(text=user_input)])

            agent_response = ''

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
            logger.error('任务被取消，可能是超时或作用域取消导致')
            print(f"✅ 对话在第{turn_count}轮结束")
            eval_results[f'agent_response_{turn_count}'] = '任务被取消，可能是超时或作用域取消导致'
            break
        except Exception as e:
            logger.error(f"获取agent响应失败: {e}")
            print(f"✅ 对话在第{turn_count}轮结束")
            eval_results[f'agent_response_{turn_count}'] = str(e)
            break

        eval_results[f'agent_response_{turn_count}'] = agent_response
        print(f"🤖 ADK Agent: {agent_response}")

        job_jsons = re.findall(r'<bohrium-chat-msg>(.*?)</bohrium-chat-msg>', agent_response)
        job_ids = []
        if job_jsons:
            for job_json in job_jsons:
                try:
                    job_json = json.loads(job_json)
                    if 'eventData' in job_json and 'content' in job_json['eventData']:
                        content = job_json['eventData']['content']
                        if 'job_list' in content and 'job_id' in content['job_list']:
                            job_id = content['job_list']['job_id']
                            job_ids.append(job_id)
                except Exception as e:
                    logger.error(f"提取job_id失败: {e}")

        # 查询job状态
        if job_ids:
            job_ids = list(set(job_ids))
            while True:
                time.sleep(10)
                all_finished = True
                for job_id in job_ids:
                    bohrium_client = Bohrium()
                    job_info = bohrium_client.job.detail(job_id)
                    logger.info(f"查询到job状态: {job_id} - 状态: {job_info["status"]}")
                    if job_info['status'] not in [-1, 2]:
                        all_finished = False
                if all_finished:
                    break

            # 使用模拟器生成用户响应
            user_response, should_continue = simulator.get_bohr_results(agent_response, job_ids)
            eval_results[f'user_response_{turn_count}'] = user_response
            print(f"🧑 模拟用户: {user_response}")
        else:
            # 使用模拟器生成用户响应
            user_response, should_continue = simulator.generate_response(agent_response)
            eval_results[f'user_response_{turn_count}'] = user_response
            print(f"🧑 模拟用户: {user_response}")

        if not should_continue:
            print(f"✅ 对话在第{turn_count}轮结束")
            break

    # 获取对话摘要
    summary = simulator.get_conversation_summary()
    eval_results['total_turns'] = summary['total_turns']
    eval_results['final_state'] = summary['final_state']
    eval_results['duration_minutes'] = summary['duration_minutes']
    print(f"\n📊 对话摘要:")
    print(f"   - 总轮次: {summary['total_turns']}")
    print(f"   - 最终状态: {summary['final_state']}")
    print(f"   - 耗时: {summary['duration_minutes']:.1f} 分钟")

    with open('evaluation_results.json', 'a') as f:
        json.dump(eval_results, f, indent=4, ensure_ascii=False)

    # 简单的成功判断
    if summary['final_state'] == 'satisfied':
        print('✅ 测试通过: 对话成功完成')
    else:
        print('❌ 测试失败: 对话未成功完成')

    await runner.close()

    print('\n' + '=' * 80)
    print('🎉 多轮对话测试完成！')
    print('=' * 80)
