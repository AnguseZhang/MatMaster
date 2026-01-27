# L1b 截断模式技术文档

## 1. 概述

L1b 截断模式是 MatMaster Agent 测评体系的一种优化策略，用于在 **工具参数生成后、实际执行前** 截断测试流程，以快速验证 Agent 是否正确选择了工具并传入了正确的参数。

### 1.1 设计目标

| 目标 | 说明 |
|------|------|
| 快速验证 | 跳过实际工具执行（API 调用），大幅缩短测试时间 |
| 参数校验 | 验证 LLM 生成的工具参数是否符合预期 |
| 成本控制 | 避免消耗真实 API 配额和计算资源 |

### 1.2 与其他模式对比

| 模式 | 截断位置 | 可验证内容 | 耗时 |
|------|----------|-----------|------|
| **完整模式** | 不截断 | 工具执行结果 | 长 |
| **L1 模式** | plan_confirm 后 | 工具名称 | 短 |
| **L1b 模式** | function_call 生成后 | 工具名称 + 参数 | 中 |

---

## 2. 架构背景

### 2.1 MatMaster Agent 工具调用架构

MatMaster Agent 基于 Google ADK 框架，工具调用采用 **两层嵌套** 架构：

```
用户请求
    ↓
IntentAgent → ExpandAgent → SceneAgent → PlanMakeAgent
    ↓
PlanInfoAgent（生成 multi_plans，包含 tool_name）
    ↓
[L1 截断点] ← plan_confirm.flag = True
    ↓
ExecutionAgent
    ↓
    ├─→ LLM 生成 function_call（MCP 工具，如 fetch_structures_with_filter）
    │       ↓
    │   private_callback 拦截并移除 function_call  ← [关键点]
    │       ↓
    │   转换为内部 Agent 调用（如 optimade_tool_connect）
    │       ↓
    │   [L1b 截断点] ← 在此捕获原始工具信息
    │       ↓
    └─→ 实际执行工具（API 调用）
```

### 2.2 为什么需要特殊处理

由于 `private_callback.py` 会在 LLM 响应后 **移除** 原始的 function_call，如果直接在事件流中捕获，只能获取到转换后的内部 Agent 名称（如 `optimade_tool_connect`），而不是原始的 MCP 工具名称和参数。

---

## 3. 核心实现

### 3.1 涉及的文件

| 文件 | 职责 |
|------|------|
| `flow_agents/agent.py` | 主流程编排，L1 截断检查 |
| `execution_agent/agent.py` | 执行层，L1b 截断检查 |
| `base_callbacks/private_callback.py` | 记录被移除的 function_call |
| `evaluation.py` | 测评框架，验证逻辑 |
| `launcher.py` | 命令行参数解析 |

### 3.2 实现步骤

#### 步骤 1：Session State 注入

在 `evaluation.py` 中，创建 session 时注入截断模式标志：

```python
# evaluation.py
if truncation_mode == 'L1b':
    initial_state = {'truncation_mode': 'L1b'}

session = await session_service.create_session(
    app_name='matmaster_agent',
    user_id='human_simulator_test',
    state=initial_state,
)
```

**为什么这样做**：通过 session state 传递截断模式，使 Agent 内部各组件都能感知到当前处于截断模式。

#### 步骤 2：记录原始 function_call

在 `private_callback.py` 中，移除 function_call 前将其记录到 state：

```python
# private_callback.py:346-365
if callback_context.state.get('truncation_mode') == 'L1b':
    if 'l1b_captured_function_calls' not in callback_context.state:
        callback_context.state['l1b_captured_function_calls'] = []
    callback_context.state['l1b_captured_function_calls'].append({
        'tool_name': function_name,
        'tool_args': function_args,
    })
```

**为什么这样做**：
- `private_callback` 是第一个接触到原始 function_call 的位置
- 在移除前记录，确保保留完整的工具名称和参数
- 存储到 state 中，供后续截断逻辑读取

#### 步骤 3：L1b 截断检查

在 `execution_agent/agent.py` 中，执行工具前检查 state 并截断：

```python
# execution_agent/agent.py:168-230
truncation_mode = ctx.session.state.get('truncation_mode', False)

async for event in target_agent.run_async(ctx):
    if truncation_mode == 'L1b':
        # 优先使用 private_callback 记录的原始工具信息
        state_captured = ctx.session.state.get('l1b_captured_function_calls', [])
        if state_captured and not l1b_truncated:
            captured_function_calls = state_captured
            l1b_truncated = True
    
    yield event
    
    if l1b_truncated:
        # 输出截断事件
        for truncation_event in context_function_event(...):
            yield truncation_event
        return  # 截断退出
```

**为什么这样做**：
- 在 `target_agent.run_async()` 启动后立即检查
- 优先使用 state 中记录的原始工具信息（来自 private_callback）
- 捕获到工具信息后立即 `return`，跳过后续执行

#### 步骤 4：输出截断事件

截断时输出 `matmaster_l1b_truncation` 事件，包含工具信息：

```python
context_function_event(
    ctx,
    self.name,
    'matmaster_l1b_truncation',
    None,
    ModelRole,
    {
        'status': 'truncated_with_args',
        'step_index': index,
        'tool_name': current_tool_name,
        'function_calls': json.dumps(captured_function_calls, ensure_ascii=False),
        'plan': json.dumps(ctx.session.state.get('plan', {}), ensure_ascii=False),
    },
)
```

**为什么这样做**：
- 通过事件流传递截断数据，保持与 ADK 框架的兼容性
- 包含完整的工具名称、参数和计划信息
- 测评框架可以从事件中提取验证所需的数据

---

## 4. 验证逻辑

### 4.1 验证流程

```
截断事件捕获
    ↓
提取实际工具调用和参数
    ↓
与测试集中的预期值对比
    ↓
输出验证结果
```

### 4.2 验证规则

在 `evaluation.py` 的 `_validate_l1b_tool_calls()` 函数中实现：

```python
def _validate_l1b_tool_calls(
    actual_tools: List[Dict[str, Any]],
    expected_tools: List[str],
    expected_args: Dict[str, Any],
) -> Dict[str, Any]:
```

#### 规则 1：工具名称验证

```python
missing_tools = [t for t in expected_tools if t not in actual_tool_names]
if missing_tools:
    return {'passed': False, 'reason': f'缺少预期工具调用: {missing_tools}'}
```

#### 规则 2：必需参数键验证 (`required_keys`)

```python
required_keys = rules.get('required_keys', [])
for key in required_keys:
    if key not in tool_args:
        args_validation_errors.append(f"工具 {tool_name} 缺少必需参数: {key}")
```

#### 规则 3：参数值精确匹配 (`key_values`)

```python
key_values = rules.get('key_values', {})
for key, expected_value in key_values.items():
    if tool_args.get(key) != expected_value:
        args_validation_errors.append(f"参数 {key} 值不匹配")
```

#### 规则 4：字符串参数包含验证 (`key_contains`)

```python
key_contains = rules.get('key_contains', {})
for key, substring in key_contains.items():
    if substring not in str(tool_args.get(key, '')):
        args_validation_errors.append(f"参数 {key} 不包含预期内容: {substring}")
```

#### 规则 5：数组参数包含验证 (`key_list_contains`)

```python
key_list_contains = rules.get('key_list_contains', {})
for key, expected_item in key_list_contains.items():
    actual_list = tool_args.get(key, [])
    if expected_item not in actual_list:
        args_validation_errors.append(f"参数 {key} 不包含预期元素: {expected_item}")
```

### 4.3 验证通过与不通过

| 场景 | 结果 | 原因 |
|------|------|------|
| 工具名称匹配 + 参数验证通过 | **通过** | 所有规则都满足 |
| 工具名称不匹配 | **不通过** | `missing_tools` 不为空 |
| 缺少必需参数 | **不通过** | `required_keys` 中有未出现的键 |
| 参数值不匹配 | **不通过** | `key_values` 验证失败 |
| 字符串不包含 | **不通过** | `key_contains` 验证失败 |
| 数组不包含元素 | **不通过** | `key_list_contains` 验证失败 |

---

## 5. 测试集格式

### 5.1 JSON 结构

```json
{
  "initial_question": "用户问题",
  "expected_tools": ["工具名称"],
  "expected_args": {
    "工具名称": {
      "required_keys": ["必需参数键1", "必需参数键2"],
      "key_values": {"参数键": "精确值"},
      "key_contains": {"参数键": "包含子串"},
      "key_list_contains": {"数组参数": "包含元素"}
    }
  },
  "expected_outcomes": ["预期结果描述"],
  "success_criteria": ["成功标准"]
}
```

### 5.2 示例

```json
{
  "initial_question": "在 Alexandria 中查找并返回 5 个含 Li、Mn、O 的材料",
  "expected_tools": ["fetch_structures_with_filter"],
  "expected_args": {
    "fetch_structures_with_filter": {
      "required_keys": ["filter", "n_results", "providers"],
      "key_contains": {
        "filter": "Li"
      },
      "key_list_contains": {
        "providers": "alexandria"
      }
    }
  }
}
```

---

## 6. 使用方法

### 6.1 命令行

```bash
# L1b 截断模式
python main.py agent database_search --l1b

# L1 截断模式（仅验证工具名称）
python main.py agent database_search --l1

# 完整模式
python main.py agent database_search
```

### 6.2 日志输出位置

| 模式 | 日志目录 |
|------|----------|
| L1b | `cases/logs/database_search_l1b/` |
| L1 | `cases/logs/database_search_l1/` |
| 完整 | `cases/logs/database_search/` |

---

## 7. 注意事项

### 7.1 异步生成器警告

截断时可能出现以下警告：

```
RuntimeError: async generator ignored GeneratorExit
```

**说明**：这是 Google ADK 框架在异步生成器被提前终止时的正常行为，**不影响截断功能的正确性**。

### 7.2 截断位置限制

L1b 截断发生在 `ExecutionAgent` 内部，需要经过以下流程：
1. 用户提问 → Agent 生成方案
2. 用户确认方案 → 进入执行阶段
3. LLM 生成 function_call → **L1b 截断**

因此 L1b 测试需要 **2 轮对话** 才能完成截断。

### 7.3 工具映射

不同的 MCP 工具对应不同的内部 Agent，截断逻辑需要在 `private_callback` 中记录原始工具信息，而不是依赖内部 Agent 名称。

---

## 8. 总结

L1b 截断模式通过以下机制实现快速参数验证：

1. **State 注入**：通过 session state 传递截断模式标志
2. **原始信息记录**：在 `private_callback` 中记录被移除的 function_call
3. **截断检查**：在 `execution_agent` 中检查 state 并提前退出
4. **事件输出**：通过 ADK 事件流传递截断数据
5. **验证逻辑**：在测评框架中对比实际参数与预期参数

这种设计既保持了与 ADK 框架的兼容性，又能在不执行实际工具的情况下完成参数验证，实现了测试效率与验证完整性的平衡。
