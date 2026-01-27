
# 第一阶段（L1）实现计划：Agent 工具调用评估体系

> 本文聚焦第一阶段：允许真实联网调用 Bohrium MCP（SSE），优先评估“调用策略稳定性”，其次评估“工具质量”。

## Step 1 – Clarify（本阶段需要你确认的关键问题）
为避免“做着做着目标漂移”，下面问题会直接影响实现形态与验收口径：

1) 评估入口是什么？
- B. 给定固定 tool call 序列/日志 → 只评估策略执行与恢复（推荐作为 L1 主入口）

2) L1 的“策略正确性”基准（ground truth）从哪里来？
- B. 规则生成：你提供少量规则，自动生成一批合规/不合规样本（更快起步）

3) L1 是否要求可在 CI 稳定跑？
- B. 否：先 live-only，本地先跑通（后续再补 replay）

4) 第一阶段的范围边界（必须明确）
- 只覆盖 1 个工具（fetch_bohrium_crystals）还是覆盖 3~5 个核心工具？
    - 覆盖这个MCP server的全部的核心工具
- 只做单步调用，还是必须覆盖“多步调用序列”（例如 submit → query_status → get_results）？
    - 当前做单步调用
5) 失败恢复策略的“期望动作”是什么？
- 参数不合法：是否允许自动修复（补默认值/截断上限）？

---

## Step 2 – Structure（第一阶段的骨架与模块）

### 2.1 产出物（Deliverables）
- 一个可运行的 L1 评估 runner（本地命令行）
- 一套用例格式（case schema），新增 case 不需要改代码
- 一套评分与报告格式（json 报告 + 人类可读摘要）
- 一套最小策略规则（policy spec）：允许工具、参数预算、恢复策略
- 可选但强烈建议：record/replay（为后续 CI 做铺垫）

### 2.2 评估对象（SUT）拆分
- Tool Adapter（底座）：统一调用 MCP 工具、处理连接、超时、重试、结果解析
- Policy Checker（核心）：对 tool call（单步/序列）进行合规性与策略质量评分
- Runner（编排）：加载 cases → 执行 → 评分 → 汇总报告

### 2.3 L1 评分拆分（策略优先）
建议默认：S_total = 0.7 * S_policy + 0.3 * S_tool

- S_policy（策略与合规）：
  - 工具选择正确性
  - 参数合规与预算约束
  - 调用序列结构（顺序/重复/循环）
  - 失败恢复（重试/降级/停止）
- S_tool（工具执行质量）：
  - 成功率
  - 契约一致性（结果可解析/关键字段存在）
  - 延迟（P50/P95）

---

## Step 3 – Generate（第一阶段里程碑与实现步骤）

### Milestone 0：工程可运行底座（半天）
**目标**：本地一条命令可以跑评估 runner（即使先只有 1 个 case）。

**任务**
1) 固化环境
- uv 已就绪（pyproject.toml + uv.lock）
- runner 使用项目内 .venv

2) 统一工具调用
- 封装 MCP SSE 连接、initialize、list_tools、call_tool
    - 涉及后面更多的MCP工具，所以需要有地方进行MCP sse的设置
- 加入超时控制、重试策略（先最小：超时 20s、重试 0~1 次）

**验收（DoD）**
- 运行一次可以连通 Bohrium MCP 并调用 fetch_bohrium_crystals 成功

### Milestone 1：最小评估闭环（1~2 天）
**目标**：用“固定 tool call 序列/单步调用”跑出第一版评分与报告。

**任务**
1) 定义 case 格式（建议 JSON/YAML 均可，先选一种）
- case_id、scenario、tool_calls（序列）、oracle、budget、tags

2) 定义 policy spec（最小可用版本）
- 允许工具集合（allowlist）
- 参数预算（如 n_results 上限、output_formats 允许值）
- 失败恢复（超时/5xx/空结果/参数错误的处理）

3) 实现 Policy Checker（第一版只做“硬规则”）
- 参数 schema 校验：必填/类型/枚举/范围
- 预算校验：截断或直接判失败（取决于你对“自动修复”态度）
- 序列校验：禁止重复调用/循环（先简单：相邻重复扣分）

4) 实现 Oracle（第一版只做“关键字段”）
- 能从 CallToolResult 里提取 text，并 parse JSON
- 关键字段：code、message、n_found、cleaned_structures（存在且类型正确）

5) 实现报告
- 单次运行输出 report.json：每个 case 的通过/失败、得分、失败原因、延迟
- 控制台输出摘要：通过率、均分、Top 失败原因

**建议最小用例集合（起步 6 个）**
- 正例：SrTiO3 / n_results=3 / output_formats=["json"]
- 边界：n_results=1
- 边界：n_results=10（默认值）
- 反例：缺少 formula（应判参数不合规）
- 反例：n_results=10000（应判超预算/或被截断并扣分）
- 反例：output_formats=["xxx"]（应判枚举不合规）

**验收（DoD）**
- 本地运行：能稳定跑完 ≥6 个 case，生成 report.json
- report.json 中能看到每条 case 的：score、latency_ms、fail_reason（若失败）

### Milestone 2：引入 record/replay（1~2 天，可并行）
**目标**：为未来 CI 准备“可重复”的评估运行模式。

**任务**
1) Record
- live 运行时保存：tool_name、args、normalized_result、timestamp、latency

2) Normalize
- 去掉易漂移字段：trace_id、job_id、output_dir 等
- 可配置：不同工具不同的 normalize 规则

3) Replay
- CI 默认走 replay，禁止外网依赖
- replay 模式下仍走同一套 Policy Checker + Oracle

**验收（DoD）**
- 同一组 cases：replay 多次输出一致（除耗时统计外）

---

## Step 4 – Refine（迭代策略：如何让评分从“能用”变“可信”）

### 4.1 先别追求“完美分数”，先追求“可解释”
第一阶段评分的核心价值是：
- 能把失败归因到具体维度（参数/预算/顺序/恢复/工具失败）
- 能稳定比较两个策略版本（回归）

### 4.2 推荐默认权重（可改）
- S_policy = 70
  - 工具选择：25
  - 参数合规：25
  - 序列结构：10
  - 失败恢复：10
- S_tool = 30
  - 成功率：15
  - 契约一致性：10
  - 延迟：5

### 4.3 校准方法（等有数据再做）
- 采集 1~2 周 report.json（或至少 50 次运行）
- 观察：哪些失败最影响用户体验、最常见、最难修
- 据此调整：权重、阈值、与“硬失败/软扣分”的边界

---

## 附：第一阶段建议的目录形态（不强制）
> 当前仓库还很轻，第一阶段可以先不追求“完美架构”，但建议至少把 case/policy/report/s_policy 分开。

- docs/
  - thoughts.md（已整理对话与总体思路）
  - plan.md（本文）
- cases/（可选）
- src/policies/（可选）
- src/reports/（可选）
...
