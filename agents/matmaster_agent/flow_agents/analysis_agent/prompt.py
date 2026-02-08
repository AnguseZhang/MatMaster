from agents.matmaster_agent.utils.sanitize_braces import sanitize_braces


def get_analysis_instruction(plan):
    plan_str = plan if isinstance(plan, str) else str(plan)
    plan_str = sanitize_braces(plan_str)
    return f"""
分析 plan 变量的结果和之前的对话历史，来对本次计划的执行进行总结后展示给用户：

<Plan Content>
{plan_str}

<Plan Structure>
{{
  steps: # 根据用户意图拆解出来需要执行的步骤，列表中的一个元素代表一步；如果对应步骤没有可用工具，也有对应元素
    [
      {{
        tool_name: <string>, # 返回的工具名称，如果没有可以调用的工具，返回值为 null
        description: <string>, # 调用该工具的说明
        "status": "plan" // 计划中为 plan，成功为success，失败为failed，进行中为process
      }}
    ]
  feasibility: <string> # 如果计划涉及的所有细分步骤都有对应工具，会返回 "full"; 部分有工具，会返回 "part"；一个工具也没有，会返回 “null”
}}

The summary must be entirely self-contained and must not include any suggestions for 'Optional next steps'
or similar subsequent actions.
"""
