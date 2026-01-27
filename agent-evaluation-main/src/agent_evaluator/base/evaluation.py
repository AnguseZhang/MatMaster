import asyncio
import json
import logging
import os
import re
import time
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
from .human_simulator import ConversationGoal, HumanSimulator
from ..utils import load_dataset_json

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(), override=True)
print(os.getenv('BOHRIUM_API_URL'))


def _validate_l1_tool_calls(
    actual_tools: List[Dict[str, str]],
    expected_tools: List[str],
) -> Dict[str, Any]:
    """
    L1 验证：检查实际工具调用是否符合预期
    
    :param actual_tools: 实际调用的工具列表 [{'tool_name': ..., 'description': ...}]
    :param expected_tools: 预期的工具名称列表 ['tool1', 'tool2']
    :return: 验证结果 {'passed': bool, 'reason': str, 'details': dict}
    """
    actual_tool_names = [t['tool_name'] for t in actual_tools]
    
    # 如果没有指定预期工具，只检查是否有工具调用
    if not expected_tools:
        if actual_tool_names:
            return {
                'passed': True,
                'reason': '未指定预期工具，但有工具调用生成',
                'details': {
                    'actual_tools': actual_tool_names,
                    'expected_tools': [],
                }
            }
        else:
            return {
                'passed': False,
                'reason': '未生成任何工具调用',
                'details': {
                    'actual_tools': [],
                    'expected_tools': [],
                }
            }
    
    # 检查预期工具是否都被调用
    missing_tools = [t for t in expected_tools if t not in actual_tool_names]
    extra_tools = [t for t in actual_tool_names if t not in expected_tools]
    
    if missing_tools:
        return {
            'passed': False,
            'reason': f'缺少预期工具调用: {missing_tools}',
            'details': {
                'actual_tools': actual_tool_names,
                'expected_tools': expected_tools,
                'missing_tools': missing_tools,
                'extra_tools': extra_tools,
            }
        }
    
    return {
        'passed': True,
        'reason': '所有预期工具均已调用',
        'details': {
            'actual_tools': actual_tool_names,
            'expected_tools': expected_tools,
            'extra_tools': extra_tools,
        }
    }


def _validate_l1b_tool_calls(
    actual_tools: List[Dict[str, Any]],
    expected_tools: List[str],
    expected_args: Dict[str, Any],
) -> Dict[str, Any]:
    """
    L1b 验证：检查实际工具调用和参数是否符合预期
    
    :param actual_tools: 实际调用的工具列表 [{'tool_name': ..., 'tool_args': {...}}]
    :param expected_tools: 预期的工具名称列表 ['tool1', 'tool2']
    :param expected_args: 预期的参数验证规则 {
        'tool_name': {
            'required_keys': ['key1', 'key2'],  # 必须包含的参数键
            'key_values': {'key1': 'expected_value'},  # 参数值验证（可选）
            'key_contains': {'key1': 'substring'},  # 参数值包含验证（可选）
            'key_list_contains': {'key1': 'item'},  # 数组参数包含验证（可选）
        }
    }
    :return: 验证结果 {'passed': bool, 'reason': str, 'details': dict}
    """
    actual_tool_names = [t['tool_name'] for t in actual_tools]
    
    # 首先检查工具名称
    if expected_tools:
        missing_tools = [t for t in expected_tools if t not in actual_tool_names]
        if missing_tools:
            return {
                'passed': False,
                'reason': f'缺少预期工具调用: {missing_tools}',
                'details': {
                    'actual_tools': actual_tool_names,
                    'expected_tools': expected_tools,
                    'missing_tools': missing_tools,
                }
            }
    
    # 如果没有指定参数验证规则，只验证工具名称
    if not expected_args:
        return {
            'passed': True,
            'reason': '工具名称验证通过，未指定参数验证规则',
            'details': {
                'actual_tools': actual_tool_names,
                'expected_tools': expected_tools,
            }
        }
    
    # 验证参数
    args_validation_errors = []
    for tool in actual_tools:
        tool_name = tool.get('tool_name', '')
        tool_args = tool.get('tool_args', {})
        
        if tool_name not in expected_args:
            continue  # 该工具没有参数验证规则
        
        rules = expected_args[tool_name]
        
        # 检查必须包含的参数键
        required_keys = rules.get('required_keys', [])
        for key in required_keys:
            if key not in tool_args:
                args_validation_errors.append(
                    f"工具 {tool_name} 缺少必需参数: {key}"
                )
        
        # 检查参数值
        key_values = rules.get('key_values', {})
        for key, expected_value in key_values.items():
            actual_value = tool_args.get(key)
            if actual_value != expected_value:
                args_validation_errors.append(
                    f"工具 {tool_name} 参数 {key} 值不匹配: "
                    f"期望={expected_value}, 实际={actual_value}"
                )
        
        # 检查参数值包含（字符串）
        key_contains = rules.get('key_contains', {})
        for key, substring in key_contains.items():
            actual_value = str(tool_args.get(key, ''))
            if substring not in actual_value:
                args_validation_errors.append(
                    f"工具 {tool_name} 参数 {key} 不包含预期内容: "
                    f"期望包含={substring}, 实际={actual_value}"
                )
        
        # 检查数组参数包含
        key_list_contains = rules.get('key_list_contains', {})
        for key, expected_item in key_list_contains.items():
            actual_list = tool_args.get(key, [])
            if not isinstance(actual_list, list):
                actual_list = [actual_list]
            if expected_item not in actual_list:
                args_validation_errors.append(
                    f"工具 {tool_name} 参数 {key} 不包含预期元素: "
                    f"期望包含={expected_item}, 实际={actual_list}"
                )
    
    if args_validation_errors:
        return {
            'passed': False,
            'reason': f'参数验证失败: {args_validation_errors[0]}',
            'details': {
                'actual_tools': actual_tool_names,
                'expected_tools': expected_tools,
                'validation_errors': args_validation_errors,
            }
        }
    
    return {
        'passed': True,
        'reason': '工具名称和参数验证通过',
        'details': {
            'actual_tools': actual_tool_names,
            'expected_tools': expected_tools,
        }
    }


async def _run_conversation(
    dataset_item: Dict[str, Any],
    max_turn_count: int,
    item_id: int,
    save_mode: str = 'w',
    label_key: str = '',
    truncation_mode: str = '',
) -> Dict[str, Any]:
    """
    执行一次对话测试，并返回结果
    :param dataset_item: 单条测试数据
    :param max_turn_count: 最大对话轮次
    :param save_mode: 写文件模式 ("w" 覆盖 / "a" 追加)
    :param truncation_mode: 截断模式
        - '': 不截断，完整执行
        - 'L1': 在计划确认后截断，只验证工具名称
        - 'L1b': 在 function_call 生成后截断，验证工具名称和参数
    """
    if item_id is None:
        item_id = 0
    if not os.path.exists(f'logs/job_{item_id}'):
        os.makedirs(f'logs/job_{item_id}')

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    
    # 创建 session，注入 truncation_mode
    # L1 模式：truncation_mode = True 或 'L1'
    # L1b 模式：truncation_mode = 'L1b'
    if truncation_mode == 'L1':
        initial_state = {'truncation_mode': True}
    elif truncation_mode == 'L1b':
        initial_state = {'truncation_mode': 'L1b'}
    else:
        initial_state = {}
    
    session = await session_service.create_session(
        app_name='matmaster_agent',
        user_id='human_simulator_test',
        state=initial_state,
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
        if not os.path.exists(f"{label_key}/logs/job_{item_id}"):
            os.makedirs(f"{label_key}/logs/job_{item_id}")
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
            
            # ========================== #
            # 收集所有事件以供查看和后续处理  #
            # ========================== #
            events_list = []
            l1_truncation_data = None  # L1 截断模式下的计划数据
            l1b_truncation_data = None  # L1b 截断模式下的 function_call 数据
            
            async for event in events:
                # 打印每个事件的内容，方便调试查看
                # print(f"DEBUG: Received event: {event}") 
                
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            agent_response += part.text
                        # 如果你想看 function_call 内容：
                        if part.function_call:
                            print(f"DEBUG: Function Call: {part.function_call}")
                            # 截断模式：捕获截断事件（来自 function_call）
                            if truncation_mode:
                                try:
                                    func_name = getattr(part.function_call, 'name', '')
                                    func_args = part.function_call.args
                                    
                                    # L1 截断事件
                                    if func_name == 'matmaster_l1_truncation':
                                        if isinstance(func_args, dict):
                                            l1_truncation_data = {
                                                'status': func_args.get('status'),
                                                'multi_plans': json.loads(func_args.get('multi_plans', '{}')),
                                                'plan_info': json.loads(func_args.get('plan_info', '{}')),
                                            }
                                            logger.info(f"L1 截断数据已捕获: {l1_truncation_data.get('status')}")
                                    
                                    # L1b 截断事件
                                    elif func_name == 'matmaster_l1b_truncation':
                                        if isinstance(func_args, dict):
                                            l1b_truncation_data = {
                                                'status': func_args.get('status'),
                                                'step_index': func_args.get('step_index'),
                                                'tool_name': func_args.get('tool_name'),
                                                'function_calls': json.loads(func_args.get('function_calls', '[]')),
                                                'plan': json.loads(func_args.get('plan', '{}')),
                                            }
                                            logger.info(f"L1b 截断数据已捕获: tool={l1b_truncation_data.get('tool_name')}")
                                            
                                except Exception as e:
                                    logger.warning(f"解析截断数据失败: {e}")
                            
                # 将事件转换为字典并保存
                events_list.append(dict(event))

            # 将事件保存到txt文件
            with open(
                f"{label_key}/logs/job_{item_id}/turn_{turn_count}.txt",
                'w',
                encoding='utf-8',
            ) as f:
                f.write(str(events_list))

        except asyncio.CancelledError:
            msg = '任务被取消，可能是超时或作用域取消导致'
            logger.error(msg)
            eval_results[f'agent_response_{turn_count}'] = msg
            raise
        except Exception as e:
            logger.error(f"获取agent响应失败: {e}")
            eval_results[f'agent_response_{turn_count}'] = str(e)
            raise e

        eval_results[f'agent_response_{turn_count}'] = agent_response
        print(f"🤖 ADK Agent: {agent_response}")

        # ===== L1 截断模式：提前退出并验证 =====
        if truncation_mode == 'L1' and l1_truncation_data:
            print('\n📋 L1 截断模式 - 计划生成完成，跳过执行阶段')
            
            # 提取实际调用的工具列表
            actual_tools = []
            multi_plans = l1_truncation_data.get('multi_plans', {})
            if multi_plans and 'plans' in multi_plans:
                for plan in multi_plans['plans']:
                    for step in plan.get('steps', []):
                        if step.get('tool_name'):
                            actual_tools.append({
                                'tool_name': step['tool_name'],
                                'description': step.get('description', ''),
                            })
            
            # L1 验证：检查工具调用是否符合预期
            expected_tools = dataset_item.get('expected_tools', [])
            l1_validation_result = _validate_l1_tool_calls(actual_tools, expected_tools)
            
            eval_results.update({
                'truncation_mode': 'L1',
                'l1_truncation_data': l1_truncation_data,
                'actual_tools': actual_tools,
                'expected_tools': expected_tools,
                'l1_validation': l1_validation_result,
                'total_turns': turn_count,
                'final_state': 'l1_truncated',
            })
            
            print(f"   - 实际工具调用: {[t['tool_name'] for t in actual_tools]}")
            print(f"   - 预期工具调用: {expected_tools}")
            print(f"   - L1 验证结果: {'通过' if l1_validation_result['passed'] else '失败'}")
            if not l1_validation_result['passed']:
                print(f"   - 失败原因: {l1_validation_result.get('reason', 'N/A')}")
            
            # 保存结果并退出
            with open('evaluation_results.json', save_mode, encoding='utf-8') as f:
                json.dump(eval_results, f, indent=4, ensure_ascii=False)
            
            await runner.close()
            return eval_results
        # ===== L1 截断模式结束 =====

        # ===== L1b 截断模式：验证工具名称和参数 =====
        if truncation_mode == 'L1b' and l1b_truncation_data:
            print('\n📋 L1b 截断模式 - function_call 已捕获，验证工具参数')
            
            # 提取实际调用的工具和参数
            function_calls = l1b_truncation_data.get('function_calls', [])
            actual_tools = []
            actual_args = []
            for fc in function_calls:
                actual_tools.append({
                    'tool_name': fc.get('tool_name', ''),
                    'tool_args': fc.get('tool_args', {}),
                })
                actual_args.append(fc.get('tool_args', {}))
            
            # L1b 验证：检查工具名称和参数
            expected_tools = dataset_item.get('expected_tools', [])
            expected_args = dataset_item.get('expected_args', {})
            l1b_validation_result = _validate_l1b_tool_calls(
                actual_tools, expected_tools, expected_args
            )
            
            eval_results.update({
                'truncation_mode': 'L1b',
                'l1b_truncation_data': l1b_truncation_data,
                'actual_tools': actual_tools,
                'actual_args': actual_args,
                'expected_tools': expected_tools,
                'expected_args': expected_args,
                'l1b_validation': l1b_validation_result,
                'total_turns': turn_count,
                'final_state': 'l1b_truncated',
            })
            
            print(f"   - 实际工具调用: {[t['tool_name'] for t in actual_tools]}")
            print(f"   - 实际参数: {actual_args}")
            print(f"   - 预期工具调用: {expected_tools}")
            print(f"   - 预期参数: {expected_args}")
            print(f"   - L1b 验证结果: {'通过' if l1b_validation_result['passed'] else '失败'}")
            if not l1b_validation_result['passed']:
                print(f"   - 失败原因: {l1b_validation_result.get('reason', 'N/A')}")
            
            # 保存结果并退出
            with open('evaluation_results.json', save_mode, encoding='utf-8') as f:
                json.dump(eval_results, f, indent=4, ensure_ascii=False)
            
            await runner.close()
            return eval_results
        # ===== L1b 截断模式结束 =====

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
                        bohrium_client = Bohrium(
                            base_url=os.getenv(
                                'BOHRIUM_API_URL',
                                'https://test.openapi.bohrium.dp.tech',
                            ),
                            access_key=os.getenv('MATERIALS_ACCESS_KEY'),
                            project_id=os.getenv('MATERIALS_PROJECT_ID'),
                        )
                        job_info = bohrium_client.job.detail(job_id)
                    except Exception as e:
                        import traceback

                        print(f"tracebackkkkkkkkkk, {traceback.print_exc()}")
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
    with open('evaluation_results.json', save_mode, encoding='utf-8') as f:
        json.dump(eval_results, f, indent=4, ensure_ascii=False)

    if summary['final_state'] == 'satisfied':
        print('✅ 测试通过: 对话成功完成')
    else:
        print('❌ 测试失败: 对话未成功完成')

    await runner.close()
    return eval_results


async def evaluation_threads_single_task(
    file_path: str,
    item_id: int,
    max_turn_count: int = 10,
    label_key: str = '',
    max_retries: int = 1,
    base_backoff: float = 5.0,
    truncation_mode: str = '',
):
    """
    测试单个数据（带重试）
    
    :param truncation_mode: 截断模式
        - '': 不截断，完整执行
        - 'L1': 在计划确认后截断，只验证工具名称
        - 'L1b': 在 function_call 生成后截断，验证工具名称和参数
    """
    print('=' * 80)
    if truncation_mode == 'L1':
        print('🔬 L1 截断模式 - 仅验证工具名称')
    elif truncation_mode == 'L1b':
        print('🔬 L1b 截断模式 - 验证工具名称和参数')
    else:
        print('🤖 与ADK Agent多轮对话测试')
    print('=' * 80)

    dataset_json = json.loads(load_dataset_json(file_path))
    dataset_item = dataset_json[item_id]
    
    # 截断模式下减少等待时间
    if not truncation_mode:
        time.sleep(10)  # 避免请求过于频繁

    attempt = 0
    while attempt < max_retries:
        try:
            result = await _run_conversation(
                dataset_item,
                max_turn_count,
                save_mode='a',
                item_id=item_id,
                label_key=label_key,
                truncation_mode=truncation_mode,
            )
            # 成功则跳出重试循环
            break
        except asyncio.CancelledError:
            # 取消应直接传播
            logger.error('任务被取消，停止重试')
            raise
        except Exception as e:
            attempt += 1
            logger.error(f"第 {attempt} 次执行失败: {e}")
            if attempt >= max_retries:
                logger.error('已达到最大重试次数，抛出异常')
                raise
            backoff = base_backoff * (2 ** (attempt - 1))
            print(f"⚠️ 第 {attempt} 次执行失败，{backoff} 秒后重试...")
            await asyncio.sleep(backoff)

    print('\n' + '=' * 80)
    if truncation_mode:
        print(f'🎉 {truncation_mode} 截断测试完成！')
    else:
        print('🎉 单条多轮对话测试完成！')
    print('=' * 80)

    return result