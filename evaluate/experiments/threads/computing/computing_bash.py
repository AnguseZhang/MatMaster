import argparse
import asyncio

from evaluate.base.evaluation import evaluation_threads_single_task

if __name__ == '__main__':
    # 运行测试
    print('🚀 人类模拟器启动')
    print('=' * 50)
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_turn_count', type=int, default=20, help='最大对话轮数')
    parser.add_argument('--item_id', type=int, default=0, help='样本索引')
    args = parser.parse_args()

    asyncio.run(
        evaluation_threads_single_task(
            'computing.json', item_id=args.item_id, max_turn_count=args.max_turn_count
        )
    )
