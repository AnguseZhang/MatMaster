import asyncio
import json
import logging
import re
import time
import os
import uuid
from typing import Any, Dict, List

from bohrium import Bohrium
from dotenv import find_dotenv, load_dotenv
from google.adk import Runner
from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.artifacts import InMemoryArtifactService
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
    runner = Runner(
        agent=root_agent, app_name=MATMASTER_AGENT_NAME, session_service=session_service
    )
    session = asyncio.run(
        session_service.create_session(
            app_name=MATMASTER_AGENT_NAME,
            user_id='evaluator',
            session_id=uuid.uuid4().hex,
        )
    )

    expected_function_call = {}
    if dataset_item['input'].get('contents', None):
        user_query = dataset_item['input']['contents'][0]['parts'][0]['text']
    else:
        user_query = dataset_item['input']['parts'][0]['text']

    for part in dataset_item['expected_output']['content']['parts']:
        if part.get('function_call'):
            expected_function_call = {
                'function_name': part['function_call']['name'],
                'function_args': part['function_call']['args'],
            }

    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_call = {}
    for event in runner.run(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        events.append(event)
        if is_function_call(event):
            function_call = {
                'function_name': event.content.parts[0].function_call.name,
                'function_args': event.content.parts[0].function_call.args,
            }
            break

    output = events[-1].content.parts[0].text
    result = {
        'input': user_query,
        'output': output,
        'function_call': function_call,
        'expected_function_call': expected_function_call,
        'context': [],
    }
    return result


def multi_turn_evaluation_task(dataset_item):
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent, app_name=MATMASTER_AGENT_NAME, session_service=session_service
    )
    session = asyncio.run(
        session_service.create_session(
            app_name=MATMASTER_AGENT_NAME,
            user_id='evaluator',
            session_id=uuid.uuid4().hex,
        )
    )

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
                'function_name': dataset_item['expected_output']['content']['parts'][0][
                    'function_call'
                ]['name'],
                'function_args': dataset_item['expected_output']['content']['parts'][0][
                    'function_call'
                ]['args'],
            }

    content = types.Content(role='user', parts=[types.Part(text=user_query)])

    events = []
    function_call = {}
    for event in runner.run(
        user_id=session.user_id, session_id=session.id, new_message=content
    ):
        events.append(event)

    output = events[-1].content.parts[0].text
    result = {
        'input': user_query,
        'output': output,
        'function_call': function_call,
        'expected_function_call': expected_function_call,
        'context': [],
    }
    return result


async def _run_conversation(
    dataset_item: Dict[str, Any], max_turn_count: int, item_id: int, save_mode: str = 'w'
) -> Dict[str, Any]:
    """
    执行一次对话测试，并返回结果
    :param dataset_item: 单条测试数据
    :param max_turn_count: 最大对话轮次
    :param save_mode: 写文件模式 ("w" 覆盖 / "a" 追加)
    """

    if item_id is None:
        item_id = 0
    if not os.path.exists(f'logs/job_{item_id}'):
        os.makedirs(f'logs/job_{item_id}')
        
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    session = await session_service.create_session(
        app_name='matmaster_agent',
        user_id='human_simulator_test',
    )

    logger.info(f"Test Session: {session.id}")

    runner = Runner(
        app_name='matmaster_agent',
        agent=root_agent,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    simulator = HumanSimulator(max_turn_count=max_turn_count)

    # 场景初始化
    scenario = {
        'name': dataset_item['initial_question'],
        'goal': ConversationGoal(
            initial_question=dataset_item['initial_question'],
            expected_outcomes=dataset_item['expected_outcomes'],
            success_criteria=dataset_item['success_criteria'],
        ),
    }

    file_parts = []
    if 'file_urls' in dataset_item:
        for file_url in dataset_item['file_urls']:
            # with open(file_url, "rb") as f:
            #     file_bytes = f.read()
            file_part = types.Part.from_uri(
                file_uri=file_url, mime_type='application/pdf'
            )
            file_parts.append(file_part)

    print(f"\n{'=' * 20} 测试场景: {scenario['name']} {'=' * 20}")

    simulator.set_goal(scenario['goal'])
    initial_question = simulator.get_initial_question()

    print(f"🎯 对话目标: {initial_question}")
    print(f"📋 期望结果: {', '.join(scenario['goal'].expected_outcomes)}")
    print(f"✅ 成功标准: {', '.join(scenario['goal'].success_criteria)}")

    # 初始化结果
    eval_results = {
        'initial_question': initial_question,
        'expected_outcomes': scenario['goal'].expected_outcomes,
        'success_criteria': scenario['goal'].success_criteria,
    }
    for i in range(1, max_turn_count + 1):
        eval_results[f'agent_response_{i}'] = ''
        eval_results[f'user_response_{i}'] = ''

    # 对话循环
    turn_count = 0
    while turn_count < max_turn_count:
        turn_count += 1
        print(f"\n🔄 第 {turn_count} 轮对话:")

        # 获取用户输入
        user_input = (
            initial_question if turn_count == 1 else simulator.get_last_user_response()
        )
        print(f"🧑 模拟用户: {user_input}")

        # 调用 agent
        try:
            if turn_count == 1 and file_parts != []:
                content = types.Content(
                    role='user', parts=file_parts + [types.Part(text=user_input)]
                )
            else:
                content = types.Content(
                    role='user', parts=[types.Part(text=user_input)]
                )
            agent_response = ''

            events = runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )

            # 保存事件到本地 JSON 文件
            events_list = []
            async for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            agent_response += part.text
                # 将事件转换为字典并添加到列表
                events_list.append(dict(event))

            # 将事件保存到txt文件
            with open(f"logs/job_{item_id}/turn_{turn_count}.txt", "w", encoding="utf-8") as f:
                f.write(str(events_list))

                
        except asyncio.CancelledError:
            msg = '任务被取消，可能是超时或作用域取消导致'
            logger.error(msg)
            eval_results[f'agent_response_{turn_count}'] = msg
            break
        except Exception as e:
            logger.error(f"获取agent响应失败: {e}")
            eval_results[f'agent_response_{turn_count}'] = str(e)
            break

        eval_results[f'agent_response_{turn_count}'] = agent_response
        print(f"🤖 ADK Agent: {agent_response}")

        # 提取 job_id
        job_jsons = re.findall(
            r'<bohrium-chat-msg>(.*?)</bohrium-chat-msg>', agent_response
        )
        job_ids: List[str] = []
        for job_json in job_jsons:
            try:
                job_json = json.loads(job_json)
                if 'eventData' in job_json and 'content' in job_json['eventData']:
                    content = job_json['eventData']['content']
                    if 'job_list' in content and 'job_id' in content['job_list']:
                        job_ids.append(content['job_list']['job_id'])
            except Exception as e:
                logger.error(f"提取job_id失败: {e}")

        # 查询 job 状态
        if job_ids:
            job_ids = list(set(job_ids))
            while True:
                time.sleep(10)
                all_finished = True
                for job_id in job_ids:
                    try:
                        bohrium_client = Bohrium(access_key=os.getenv("MATERIALS_ACCESS_KEY"),
                                                project_id=os.getenv("MATERIALS_PROJECT_ID"))
                        job_info = bohrium_client.job.detail(job_id)
                    except Exception as e:
                        logger.error(f"查询job状态失败: {e}")
                        all_finished = False
                        continue

                    logger.info(f"查询到job状态: {job_id} - 状态: {job_info['status']}")
                    if job_info['status'] not in [-1, 2]:
                        all_finished = False
                if all_finished:
                    break

            user_response, should_continue = simulator.get_bohr_results(
                agent_response, job_ids
            )
        else:
            user_response, should_continue = simulator.generate_response(agent_response)

        eval_results[f'user_response_{turn_count}'] = user_response
        print(f"🧑 模拟用户: {user_response}")

        if not should_continue:
            print(f"✅ 对话在第{turn_count}轮结束")
            break

    # 对话总结
    summary = simulator.get_conversation_summary()
    eval_results.update(
        {
            'total_turns': summary['total_turns'],
            'final_state': summary['final_state'],
            'duration_minutes': summary['duration_minutes'],
        }
    )

    print('\n📊 对话摘要:')
    print(f"   - 总轮次: {summary['total_turns']}")
    print(f"   - 最终状态: {summary['final_state']}")
    print(f"   - 耗时: {summary['duration_minutes']:.1f} 分钟")

    # 保存结果
    with open('evaluation_results.json', save_mode) as f:
        json.dump(eval_results, f, indent=4, ensure_ascii=False)

    if summary['final_state'] == 'satisfied':
        print('✅ 测试通过: 对话成功完成')
    else:
        print('❌ 测试失败: 对话未成功完成')

    await runner.close()
    return eval_results


async def evaluation_threads_task(file_path: str, max_turn_count: int = 10):
    """批量测试所有数据"""
    print('=' * 80)
    print('🤖 与ADK Agent多轮对话测试')
    print('=' * 80)

    dataset_json = json.loads(load_dataset_json(file_path))
    results = []
    for i, dataset_item in enumerate(dataset_json):
        time.sleep(10)  # 避免请求过于频繁
        result = await _run_conversation(
            dataset_item, max_turn_count, save_mode='w' if i == 0 else 'a'
        )
        results.append(result)

    print('\n' + '=' * 80)
    print('🎉 多轮对话测试完成！')
    print('=' * 80)
    return results


async def evaluation_threads_single_task(
    file_path: str, item_id: int, max_turn_count: int = 10
):
    """测试单个数据"""
    print('=' * 80)
    print('🤖 与ADK Agent多轮对话测试')
    print('=' * 80)

    dataset_json = json.loads(load_dataset_json(file_path))
    dataset_item = dataset_json[item_id]
    time.sleep(10)  # 避免请求过于频繁

    result = await _run_conversation(dataset_item, max_turn_count, save_mode='a',item_id=item_id)

    print('\n' + '=' * 80)
    print('🎉 单条多轮对话测试完成！')
    print('=' * 80)

    return result
