# Agent 评估系统设计与实现

这份文档用于指导后端工程师在本仓库内落地一套可扩展、可复现、可追溯的 Agent 评估系统。它覆盖：模块职责、关键注意点、整体架构、数据模型、执行流程、以及如何结合当前 `evaluate/base/` 内的实现与迭代。

## 目标与非目标

目标：
- 用统一的方式描述评估任务（单轮/多轮/带工具/带文件）
- 支持多次试验（Trial），并行执行，输出可汇总的指标
- 记录结构化 Transcript，区分 Transcript 与 Outcome，支持回放与诊断
- 支持多类 Grader：规则/代码、模型裁判、人类标注
- 结果可落盘/可查询/可视化（自建存储或对接现有观测平台）

非目标：
- 不在评估框架里实现具体 Agent 能力
- 不依赖特定 UI；报表以结构化数据为主，展示为辅

## 术语

| 术语 | 定义 |
| :--- | :--- |
| 评估 (Eval) | 为 AI 提供输入，然后使用评分逻辑对其输出进行评判，以衡量其成功程度。 |
| 任务 (Task) | 一个具有明确输入和成功标准的单个测试，也被称为问题或测试用例。 |
| 试验 (Trial) | 对一个任务的单次尝试。由于模型输出具有非确定性，通常需要运行多次试验以获得更一致的结果。 |
| 评分器 (Grader) | 对 Agent 在某个方面的表现进行打分的逻辑。一个任务可以有多个评分器，每个评分器包含多个断言。 |
| 记录 (Transcript) | 一次试验的完整记录，包括模型输出、工具调用、工具结果、中间状态、错误与元信息。 |
| 结果 (Outcome) | 试验结束时环境的最终状态（数据库查询结果、生成文件、结构化 JSON、外部作业状态等）。 |
| 评估框架 (Evaluation Harness) | 端到端运行评估的基础设施：加载任务、并发跑 Trial、记录、评分、汇总。 |
| Agent 框架 (Agent Harness) | 使模型以 Agent 方式行动的系统：处理输入、编排工具调用并返回事件流/结果。 |
| 评估套件 (Evaluation Suite) | 为测量特定能力或行为而设计的一系列任务集合。 |

## 总体架构

评估系统建议拆分为 6 层，便于替换实现与逐步演进：

1) Task 层：任务/数据集定义（输入、期望、约束、附件）
2) Runner 层：驱动 Agent 执行 Trial（单轮/多轮/带工具/带文件）
3) Logging 层：采集结构化 Transcript + Outcome 快照
4) Grader 层：对 Trial 做多维评分（pass/fail、0-1、原因、证据）
5) Aggregation 层：跨 Trial/Task 汇总统计（均值、通过率、置信区间、分桶）
6) Storage/Reporting 层：结果落盘、可回放、可检索、可视化

建议的数据流（单个 Task，多次 Trial）：

1. 读取 TaskSpec → 生成 N 个 TrialSpec
2. Runner 执行 Trial → 产出 Transcript + Outcome
3. 分层 Grader（代码→LLM→人工）逐级评估 Trial → 产出分层 GradeResult
4. 聚合器汇总 → 产出 TaskSummary / SuiteSummary
5. 结果写入存储并可回放

## 关键注意点（务必落实）

- 可复现性：记录模型名、温度、top_p、系统提示词版本、工具版本、数据集版本、代码版本（commit hash）
- 非确定性：同一 Task 必须跑多次 Trial；汇总使用均值/分位数/置信区间
- 隔离性：带工具的评估要么使用沙箱环境，要么在 Outcome 层提供可回滚/可比对的快照
- 超时与重试：对 Agent 调用、外部作业（例如 Bohrium job）要有统一超时与重试策略
- 脱敏与安全：Transcript 禁止写入密钥、Cookie、Token、内部 URL；落盘前做红线字段清洗
- 结构化记录：不要只保存拼接文本；工具调用/结果必须结构化，便于做自动评分与检索
- 输出落盘格式：追加写 JSON 时不要用单个 `.json` 直接 `append` 多对象，推荐 JSONL 或按 Task/Trial 分文件

## 数据模型（建议标准）

系统要稳定扩展，核心是统一数据契约。下面是建议的最小可用结构（JSON 表示，实际可用 Pydantic/Dataclass 实现）。

### TaskSpec（任务定义）

```json
{
  "input": {
    "initial_question": "我想系统性调研氧化物类固态电解质的最新进展，先给出一个可行的多步计划。",
    "file_urls": ["https://.../a.pdf"]
  },
  "success_criteria": [
    "返回明确的分步计划并停止，等待用户指示",
    "未在未确认时调用任何工具"
  ],
  "execution": {
    "max_turns": 3,
    "trials": 5,
    "timeout_sec": 120
  },
  "grading": {
    "code": [{ "name": "no_tool_before_confirm" }],
    "llm": { "name": "plan_quality", "model": "azure/gpt-4o", "threshold": 0.8 },
    "human": { "sample_rate": 0.05 }
  }
}
```

说明：
- `execution.trials` 可以被 suite/命令行覆盖
- `grading` 表示分层评分配置：先跑代码层（硬约束），再跑 LLM 层（质量/语义），人工层用于抽检或升级复核

### TrialResult（单次试验产物）

```json
{
  "trial_id": "uuid",
  "task_id": "sse.plan_then_confirm.v1",
  "started_at": 1730000000,
  "ended_at": 1730000123,
  "status": "completed",
  "agent": { "name": "matmaster_agent", "model": "..." },
  "input": { "initial_question": "..." },
  "transcript": { "ref": "trial_logs/.../transcript.jsonl" },
  "outcome": { "ref": "trial_logs/.../outcome.json" },
  "error": null,
  "grades": [
    { "stage": "code", "name": "no_tool_before_confirm", "score": 1, "passed": true, "reason": [] },
    { "stage": "llm", "name": "plan_quality", "score": 0.8, "passed": true, "reason": ["..."] }
  ],
  "meta": { "seed": null, "temperature": 1.0 }
}
```

### TranscriptEvent（结构化事件）

```json
{
  "ts": 1730000001,
  "turn": 1,
  "kind": "assistant_message",
  "payload": {
    "text": "..."
  },
  "usage": { "input_tokens": 0, "output_tokens": 0 },
  "trace": { "session_id": "...", "run_id": "..." }
}
```

`kind` 建议枚举：
- `user_message` / `assistant_message`
- `tool_call` / `tool_result`
- `system`（超时、取消、重试、限流）
- `artifact`（文件、图片、表格、外部链接等）

### Outcome（环境最终状态）

Outcome 必须可被后续评分与回放使用，建议以“可比对快照”为主：

```json
{
  "type": "external_job",
  "jobs": [
    { "provider": "bohrium", "job_id": "xxx", "final_status": 2, "result_uri": "..." }
  ],
  "files": [
    { "name": "export.csv", "uri": "..." }
  ],
  "db_snapshot": null,
  "notes": ""
}
```

## Task 系统（任务与数据集）

### Task 的定位（重要）

这里的 Task 指“评估用例/评估脚本”，它的职责是：在一个可控环境里复现输入、拿到可验证的 Outcome，并产出可评分的证据。对于需要环境真值/落地结果校验的任务，Task 应该直接调用 MCP 工具来：
- 构造/初始化环境（例如写入测试数据、准备文件、创建作业）
- 获取真值或可比对快照（例如 DB 查询、文件哈希、作业最终状态）
- 在必要时完成清理/回滚（保证多 Trial 的隔离性）

`HumanSimulator` 不应作为 Task 的必需组成部分。它更适合作为“可选的对话压测/探索性测试驱动器”，用于模拟不确定的人类反馈，而不是作为任务执行的主路径。

### base 层的输入契约

本仓库当前 `evaluate/base/` 已有两类 Runner 输入契约（都是“传入一个 `dataset_item` 字典”）。文档后续所有实现建议，都以这两类契约为基准。

#### 单轮/轻量多轮（`evaluation_task` / `multi_turn_evaluation_task`）

实现入口在 `evaluate/base/evaluation.py`：
- `evaluation_task(dataset_item)`
- `multi_turn_evaluation_task(dataset_item)`

它们对 `dataset_item` 的最低要求是：
- `dataset_item["input"]`：包含用户文本（两种格式之一：`contents` 或 `parts`）
- `dataset_item["expected_output"]["content"]["parts"]`：可选包含期望的 `function_call`，用于工具调用匹配

最低示例（仅展示必需字段）：

```json
{
  "input": {
    "parts": [
      { "text": "用户问题..." }
    ]
  },
  "expected_output": {
    "content": {
      "parts": [
        { "function_call": { "name": "tool_name", "args": { "k": "v" } } }
      ]
    }
  }
}
```

当 `input.contents` 存在时，base 逻辑会从 `contents[0].parts[0].text` 取首轮文本；`multi_turn_evaluation_task` 会把前若干轮拼成上下文再发给 Agent。

#### 多轮对话（人类模拟，`evaluation_threads_single_task` / `_run_conversation`）

实现入口在 `evaluate/base/evaluation.py`：
- `evaluation_threads_single_task(...)` → `_run_conversation(dataset_item, ...)`

它对 `dataset_item` 的最低要求是：
- `initial_question`: 首轮用户问题
- `expected_outcomes`: 期望结果点列表（用于评分与结果汇总）
- `success_criteria`: 成功标准列表（用于评分与结果汇总）
- `file_urls`（可选）: 附件 URI 列表（当前按 PDF 处理）

最低示例（仅展示必需字段）：

```json
{
  "initial_question": "用户问题...",
  "expected_outcomes": ["期望点1", "期望点2"],
  "success_criteria": ["标准1", "标准2"],
  "file_urls": ["https://.../a.pdf"]
}
```

### 任务设计原则

- 可测性：成功标准必须可判定（可由规则或 LLM judge 判定），避免纯主观描述
- 可分解：多轮任务要显式写清楚每轮输入与期望行为边界（例如“必须先征得确认”）
- 可控副作用：涉及数据库写入、外部作业等必须声明隔离策略或回滚策略
- 覆盖面：评估套件按能力维度组织（规划、工具调用、信息检索、长文总结、稳健性等）
- 可复现执行：优先用脚本化回合与 MCP 真值校验；避免把“对话推进”依赖在 HumanSimulator 这类非确定组件上

## Trial 执行系统（Runner）

Runner 的职责是“给 Agent 输入 → 获取事件流 → 组织 turn → 最终落盘”。

### 单轮 Runner（对应当前 `evaluation_task`）

当前实现位于 `evaluate/base/evaluation.py` 的 `evaluation_task(dataset_item)`：
- 创建 ADK Session
- 发送 user query
- 收集事件（遇到 function_call 可能提前 break）
- 产出 `{"input","output","function_call","expected_function_call"}` 供评分器（Grader）使用

落地建议：
- 不要提前 `break` 导致丢失后续事件；保留完整事件流，评分时再选择关键信号
- 将 `events` 结构化写入 Transcript（JSONL），并记录模型配置/会话 ID

### 多轮 Runner（当前实现：人类模拟；推荐：脚本化 Task 驱动）

当前实现位于 `evaluate/base/evaluation.py` 的 `_run_conversation(...)`：
- `HumanSimulator` 按规则生成用户反馈，驱动多轮对话
- 通过 ADK `runner.run_async` 拉取事件并拼接 `agent_response`
- 从 `agent_response` 中解析 `<bohrium-chat-msg>...</bohrium-chat-msg>` 提取 job_id 并轮询状态
- 将每轮事件保存为 `turn_{n}.txt`，汇总写入 `evaluation_results.json`

落地建议（后端实现优先级从高到低）：
- 把“对话推进”从 HumanSimulator 迁移为脚本化 Task 驱动：每轮用户输入来自 Task 定义或 MCP 查询结果
- 将每轮保存从 txt 改为结构化 JSONL（每条 event 一行），保持可检索、可回放
- 把 job_id 提取与 job 轮询抽成 OutcomeAdapter（避免 Runner 越写越重）
- 统一超时：对每轮 Agent 调用、对外部 job 轮询分别配置超时
- `evaluation_results.json` 追加写多个对象会破坏 JSON 格式，建议改为 `evaluation_results.jsonl` 或按 trial 分目录写

## Transcript 系统（记录与回放）

### 功能

- 全量记录：用户输入、Agent 输出、工具调用、工具结果、异常、耗时、token 统计、外部依赖状态
- 可回放：能把 Transcript 再喂给 Grader 或调试工具复现问题
- 可查询：按 task_id、grader 失败原因、工具名、错误码检索

### 建议落盘结构

建议目录结构（每次评估运行一个 run_id）：

```text
evaluate/runs/{run_id}/
  suite.json
  tasks/{task_id}/
    trials/{trial_id}/
      transcript.jsonl
      outcome.json
      grades.json
      meta.json
  summary.json
```

### 脱敏策略（必须）

写盘前做：
- 移除/掩码：`access_key`、`api_key`、`token`、`cookie`、`Authorization` 等字段
- 对外部 URL 做白名单或 hash
- 对工具返回的大块数据（例如全文）只保留摘要 + artifact 引用

## Outcome 系统（环境结果与可比对性）

Outcome 用来解决“只看文本不够”的问题：很多任务的成功与否取决于外部环境状态（DB、文件、作业系统）。

实现方式建议：
- 为每类外部系统定义 `OutcomeAdapter`：
  - 输入：Transcript（或关键事件）
  - 输出：Outcome JSON（结构化快照）
- 常见 Outcome 类型：
  - `external_job`：作业系统 job 状态、结果位置
  - `db_query`：查询语句、结果行数、关键字段摘要（避免落敏感原始数据）
  - `file_export`：文件路径/uri、schema、行数、hash
  - `artifact`：图、表、结构化结果 JSON

## Grader 系统（评分器）

Grader 的职责是：基于 TrialResult（尤其是 Transcript + Outcome）产出结构化评分。这里的“分层 Grader”指的是评估流水线分层：先用代码/规则做硬约束与快速筛查，再用 LLM 做语义与质量评估，最后在需要时才进入人工评估（抽检或高价值样本）。

### 分层设计

1) 基于代码/规则的 Grader（确定性强、成本低、优先使用）
- 用于：工具调用是否正确、是否遵循流程约束、是否包含必填字段、格式是否满足 schema
- 例：判断“未确认前不得调用工具”

2) 基于模型的 Grader（覆盖面广、成本高）
- 用于：答案相关性、计划质量、解释是否清晰、信息完整性
- 需要：严格输出 JSON schema（score/reason/evidence），并做解析与失败兜底
- 建议：为 judge prompt 版本化，并记录在 Trial meta 中

3) 基于人工的 Grader（最高质量、最慢）
- 用于：高价值任务集的抽检与标注
- 流程：从失败样本/高不确定样本抽样 → 标注 → 回写标签作为 golden

### 分层执行策略

常用策略：
- 逐级停止：代码层失败则直接失败；只有代码层通过才进入 LLM 层
- 逐级升级：LLM 层得分接近阈值、或任务高价值时，升级到人工层复核
- 分层产物：每一层输出自己的 GradeResult，聚合时以 `pass_policy` 指定层为准

## 汇总与报表（Aggregation）

最低需要输出：
- 每个 Task：试验次数、通过率、平均分、失败原因 TopN、耗时分布
- 每个 Suite：按 tag/能力维度分组的通过率与趋势

建议统计口径：
- 通过率：`passed_trials / total_trials`
- 分数：均值 + 分位数（p50/p90）
- 波动：同 Task 多 Trial 的方差，用于衡量稳定性

## 如何结合当前仓库实现

### 现状映射

- Runner：
  - 单轮：`evaluate/base/evaluation.py` → `evaluation_task(...)`
  - 轻量多轮：`evaluate/base/evaluation.py` → `multi_turn_evaluation_task(...)`
  - 多轮对话：`evaluate/base/evaluation.py` → `evaluation_threads_single_task(...)` / `_run_conversation(...)`
- 人类模拟器：
  - `evaluate/base/human_simulator.py` → `HumanSimulator`

### 推荐实现步骤（从可用到可扩展）

1) 统一结构化 Transcript
- 在单轮与多轮 Runner 中，把 ADK event 流统一写到 `transcript.jsonl`
- 记录 session_id、run_id、turn、event.kind、payload

2) 明确 Outcome 与 Transcript 的边界
- 将外部 job 轮询与结果归档输出为 `outcome.json`
- Transcript 只记录“发生了什么”，Outcome 记录“最终环境状态是什么”

3) 建立 Grader 插件化接口
- 分层 grader：按 code→llm→human 的流水线组织执行与停止/升级策略
- 规则 grader：读取 transcript/outcome 做断言
- LLM judge：统一 prompt/schema/解析器，失败时给出 reason 并降级
- 将分层评分结果写入 `grades.json`

4) 建立 suite/run 聚合输出
- 输出 `summary.json`，包含按 task_id 与 tag 的聚合
- 同时把关键指标写入数据库/日志系统/观测平台
