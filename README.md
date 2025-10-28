# GenAI Insight Agent

GenAI项目洞察分析代理，用于自动化分析GitHub项目。

## 功能特性

- 定时分析热门GenAI项目（vLLM、SGLang、Dify等）
- 自动获取HelloGitHub AI相关项目信息
- 支持流式和阻塞式API调用
- 完整的错误处理和重试机制
- 详细的日志记录

## 安装依赖

使用UV包管理器（推荐）：

```bash
# 安装UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

## 使用方法

### 启动定时任务

```bash
# 使用UV运行
uv run python run_tasks.py

# 或直接运行
python run_tasks.py
```

## Analyze API调用示例

### HelloGitHub日报触发

```bash
curl -X POST 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run' \
--header 'Authorization: Bearer app-lJpX4GANg9d6pud8ciHnh9EJ' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {"task": "获取https://hellogithub.com/ 中前5个AI相关的项目，把相关项目的信息以json形式输出。\n\n## 参考步骤：\n1. 勾选https://hellogithub.com/的AI 标签\n2. 顺序点击进入每个项目(前5个)\n3. 获取详细信息包括：Stars数量，新增stars in Past 6 days, 项目描述, url 和 tags\n\n## 参考输出格式\n[\n{\n  \"name\": \"..\",\n  \"stars\" : \"..\",\n  \"new_stars_past_7_days\" : \"..\",\n  \"description\": \"...\",\n  \"url\" : \"...\",\n  \"tags\" : [...]\n}\n..\n]"},
  "response_mode": "blocking",
  "user": "news_officer"
}'
```

### GitHub项目分析触发

```bash
curl -X POST 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run' \
--header 'Authorization: Bearer app-UWkAZ1R1rFKh5ppB5iONDzSx' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {"repo": "https://github.com/vllm-project/vllm", "start_date":"2024-10-27"},
  "response_mode": "blocking",
  "user": "github_analyzer"
}'
```