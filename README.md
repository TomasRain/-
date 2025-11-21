# 团队项目起步指南

这个仓库是团队项目的占位符，附带一份可扩展的起步说明，便于后续根据项目进展补充。

## 快速开始
1. 克隆仓库。
2. 为你的工作创建新分支：`git checkout -b feature/your-feature`。
3. 按需添加代码或文档。
4. 提交并推送后发起 Pull Request 以便团队评审。

## 项目灵感
- 构建一个追踪团队任务的小型 Web 应用。
- 原型化一份数据分析 Notebook。
- 试验一个新框架并分享经验。
- 打造一个“新闻热点聚合与总结”助手：输入热点关键词，自动抓取多源新闻、提取摘要并合成图文报告。

### 新闻热点聚合与总结助手（草案）
**目标**：给定热点事件或关键词，快速从公开新闻源抓取多条报道，生成去重整理的要点摘要，并可附带示意图片或封面。

**核心流程**
1. 关键词检索：使用新闻/搜索 API（如 NewsAPI、Serper、Bing）获取近期相关文章的链接和元数据。
2. 内容拉取：对检索到的链接进行正文提取与清洗（`newspaper3k`、`trafilatura` 或 `readability-lxml`）。
3. 去重聚合：基于标题与文本相似度去重，按来源/时间排序，保留若干代表性条目。
4. 摘要与对比：调用小型本地 LLM（如 Qwen2-7B-Instruct 量化版）或在线 API，对多篇报道进行多文档总结，输出中文要点和分歧点。
5. 图文合成：可选拉取首图或用生成式图片 API 生成封面（如 Stable Diffusion WebUI 或通用图像生成 API）。
6. 输出形式：CLI/网页展示，或生成 Markdown/HTML 报告。

**建议技术栈**
- 语言：Python 3.10+。
- 抓取：`requests` + `trafilatura`（正文提取稳定）或 `playwright` 用于少数动态页。
- 相似度/聚类：`sentence-transformers` 的中文小模型（如 `bge-small-zh`），`faiss` 做近似检索与去重。
- 总结：本地量化 LLM（`llama.cpp`/`Ollama` 部署 7B 量化）或在线 API；多文档总结可分段摘要后再汇总。
- Web：`FastAPI` + `Jinja2` 或前端微型框架（`htmx`/`Alpine.js`）；若仅 CLI，可用 `rich` 展示。

**起步任务（按优先级）**
1. 初始化项目目录：`src/`、`tests/`、`requirements.txt`，并创建 `.env.example` 存放 API Key 样例。
2. 实现关键词检索 + 内容提取的最小闭环（命令 `python -m src.collect "热点关键词"` 打印标题、来源、正文前 500 字）。
3. 引入相似度去重逻辑，输出去重后的前 N 条新闻摘要。
4. 封装摘要管线：多文档摘要 -> 汇总要点 -> 生成中文 Markdown 报告。
5. 可选：加一个 `/report?query=xxx` 的简易 Web 端点或静态报告生成。

### 当前实现（离线演示 + Serper 可选）
本仓库已提供一个最小可跑的命令行管线：

- **检索**：默认使用内置演示数据（无需网络），可切换为 Serper.dev API。
- **正文获取**：演示数据直接包含内容；真实抓取时会尝试 `requests` + `trafilatura`。
- **摘要**：基于分句的轻量摘要，便于快速验证流程；后续可接入 LLM。
- **输出**：终端展示汇总要点和每条新闻的简短摘要，支持 JSON 输出用于调试或集成。

#### 准备环境
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
```

#### 运行离线演示
```bash
PYTHONPATH=src python -m news_aggregator.cli "生成式 AI" --demo
```

#### 使用 Serper.dev 实时搜索
```bash
export SERPER_API_KEY=你的_serper_key
PYTHONPATH=src python -m news_aggregator.cli "新能源 投资" --serper --limit 5
```

#### JSON 输出（便于集成）
```bash
PYTHONPATH=src python -m news_aggregator.cli "多模态 模型" --demo --json
```

### 后续可迭代方向
- 将摘要步骤替换为本地 LLM 或云端 API，多文档合成时可分段汇总再二次总结。
- 增加标题、正文的相似度去重（`bge-small-zh` + `faiss`），减少重复报道。
- 提供 Web 端点或导出 Markdown/HTML 报告，方便分享。

## 协作规范
- 保持提交原子化且描述清晰。
- 每次变更都通过 Pull Request，方便队友审阅。
- 将环境配置或决策记录在 README 或对应文档中。

## 下一步
- 与团队确认项目范围与目标。
- 补充初始目录结构（例如 `src/`、`docs/`）。
- 约定编码规范、测试要求与发布流程。

## 语言偏好
- 文档默认使用中文，代码注释与提交信息可根据团队需要选择中英文，但建议保持一致性。
