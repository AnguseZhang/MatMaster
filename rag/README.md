# RAG make_plan 独立运行包

本文件夹包含运行 **RAG make_plan** 所需的全部代码、配置与索引，可单独拷贝到任意位置，仅依赖本目录即可执行任务。

## 运行环境

### 要求

- **Python 3.10+**
- 以下包需已安装（见 `requirements-rag.txt`）：
  - **pyyaml**：读 `settings.yaml`
  - **litellm** 或 **openai**：调大模型（优先 litellm，无则退化为 openai）
  - **graphrag**：本地检索、实体/边、embedding（[GraphRAG](https://github.com/microsoft/graphrag)）
  - **pydantic**：DashScope 补丁用

### 安装示例

```bash
# 建议用 conda 建独立环境
conda create -n rag python=3.12
conda activate rag

# 按顺序安装
pip install pyyaml litellm openai pydantic
# graphrag 需单独安装（见官方文档，或 pip install graphrag）
pip install graphrag
```

或使用本目录提供的依赖列表（不含 graphrag 安装方式）：

```bash
pip install -r requirements-rag.txt
```

- 无需环境变量即可运行；若使用代理可在系统或 litellm 中配置。

## 目录结构

```
rag/
├── README.md
├── requirements-rag.txt   # 运行依赖列表
├── settings.yaml          # LLM 与 GraphRAG 配置
├── run_make_plan.py       # 主入口脚本
├── make_plan_rag.py       # 统一入口逻辑
├── plan_llm.py            # LLM 调用与 plan 校验
├── context_builder.py     # RAG 上下文构建
├── patch_local_context_entity_cap.py
├── run_index_with_dashscope_fix.py
├── prompts/
│   └── plan_make_rag.txt
├── output/                # GraphRAG 索引（lancedb、parquet 等）
├── run_plan_16_to_30_append_bianpai.py   # 批量跑题（可选）
└── 1.json                 # 批量用题集（可选）
```

## 用法

在 **本目录** 下执行（`--root .` 表示以当前目录为项目根）：

```bash
cd /path/to/rag
python run_make_plan.py --query "你的问题" --root .
```

指定输出文件：

```bash
python run_make_plan.py --query "你的问题" --root . \
  --out output/plan.txt --out-context output/context.txt
```

批量对 1.json 第 16～30 题跑计划并追加到 bianpai.md：

```bash
python run_plan_16_to_30_append_bianpai.py
```

## 配置

- **LLM**：在 `settings.yaml` 的 `models.default_chat_model` 中配置 `api_key`、`api_base`、`model`（如 DashScope、OpenAI 等兼容接口）。
- **索引**：`output/` 内为已有 GraphRAG 索引；若需重建，在本目录执行 `python run_index_with_dashscope_fix.py index --root .`（需先准备 `input/` 下的文档）。

## 仅依赖本目录

所有路径均相对本目录（`--root .`）：配置读 `./settings.yaml`，prompt 读 `./prompts/`，索引读 `./output/`。将整个 `rag` 文件夹拷贝到任意位置后，在该目录下按上述命令执行即可。
