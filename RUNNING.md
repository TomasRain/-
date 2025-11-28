# 运行指南

本项目提供命令行与 FastAPI 网页界面两种入口，以下步骤可帮助你在本地快速体验新闻热点聚合与摘要功能。

## 环境准备
1. 安装 Python 3.10+。
2. 创建并激活虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 设置模块路径（每次打开新终端后执行）：
   ```bash
   export PYTHONPATH=src
   ```

> 如果无法联网安装依赖，命令行演示模式仍可运行，但 FastAPI/Web 入口需要安装 `fastapi` 与 `uvicorn`。

## 命令行运行
- **离线演示（无需网络）**：
  ```bash
  PYTHONPATH=src python -m news_aggregator.cli "生成式 AI" --demo
  ```
- **JSON 输出（便于集成调试）**：
  ```bash
  PYTHONPATH=src python -m news_aggregator.cli "多模态 模型" --demo --json
  ```
- **使用 Serper.dev 实时搜索**（需要 API Key）：
  ```bash
  export SERPER_API_KEY=你的_serper_key
  PYTHONPATH=src python -m news_aggregator.cli "新能源 投资" --serper --limit 5
  ```

## 启动浏览器界面（FastAPI）
1. 确认已安装 Web 依赖（`fastapi`、`uvicorn`）。
2. 启动服务：
   ```bash
   export PYTHONPATH=src
   uvicorn news_aggregator.web:app --reload --port 8000
   ```
3. 打开浏览器访问 http://localhost:8000 ，输入关键词即可体验：
   - **离线示例模式**：勾选“使用演示数据”，无需网络。
   - **实时 Serper 搜索**：设置 `SERPER_API_KEY` 后取消勾选即可实时拉取。
   - 页面会展示缓存命中状态、耗时与各阶段计数，便于观察性能。

## 常见问题
- **缺少依赖**：按上方命令重新执行 `pip install -r requirements.txt`。FastAPI 相关报错通常是未安装 Web 依赖。
- **无法访问外网**：使用 `--demo` 模式或勾选“使用演示数据”即可离线体验。
- **缓存与性能**：相同关键词+模式在 10 分钟内重复请求会命中内存缓存，明显缩短耗时。
