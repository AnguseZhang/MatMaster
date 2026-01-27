import json
import argparse
import asyncio
import os
import sys
from dotenv import load_dotenv

def load_dataset_json(json_file):
    with open(json_file, encoding='utf-8') as f:
        dataset_json = json.dumps(json.load(f))

    return dataset_json

def run_single_evaluation():
    """通用单任务评估入口"""
    load_dotenv()
    
    # 延迟导入以避免循环依赖或不必要的加载
    from .base.evaluation import evaluation_threads_single_task
    
    sys.stdout.reconfigure(encoding='utf-8')
    print('🚀 人类模拟器启动')
    print('=' * 50)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_turn_count', type=int, default=5, help='最大对话轮数')
    parser.add_argument('--item_id', type=int, default=0, help='样本索引')
    parser.add_argument('--json_path', type=str, help='数据集JSON路径')
    parser.add_argument('--label_key', type=str, help='标签（用于日志目录）')
    parser.add_argument('--truncation_mode', type=str, default='',
                        help='截断模式: L1（只验证工具名称）或 L1b（验证工具名称和参数）')
    args = parser.parse_args()

    # 如果没有提供 label_key，尝试从脚本路径或环境变量推断
    label_key = args.label_key
    if not label_key:
        label_key = os.getenv("AGENT_LABEL_KEY", "default")

    asyncio.run(
        evaluation_threads_single_task(
            args.json_path,
            item_id=args.item_id,
            max_turn_count=args.max_turn_count,
            max_retries=3,
            label_key=label_key,
            truncation_mode=args.truncation_mode,
        )
    )
