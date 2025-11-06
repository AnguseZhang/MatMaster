import asyncio

from evaluate.base.evaluation import evaluation_threads_task

# 使用示例
if __name__ == '__main__':
    # 运行测试
    print('🚀 人类模拟器启动')
    print('=' * 50)

    asyncio.run(evaluation_threads_task('structure_generate/structure_generate.json'))
