# agent-evaluation
evaluate agent

## 执行

python main.py
python main.py --suite-dir cases/mofdb_agent


## 评估

### agent 评估
1. 提供prompt
2. 提供问题
3. 评估agent的响应是否符合预期
4. 输出报告
    - 包含用例ID、问题、agent响应、是否符合预期、耗时，token
    - 日志中记录过程
    - 总结评估结果，包括通过率、平均策略分、平均耗时
5. 额外需求：
    - 支持高通量设置，提高评估速度
    - 
uv run python main.py agent database_search

### mcp工具评估

