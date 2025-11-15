# GenAI Insight Agent

GenAI项目洞察分析代理，用于自动化分析GitHub项目。分析的主要目标是为了GenAI领域的从业者获取第一手，细粒度的技术洞察，帮助他们快速了解最新发展情况(技术趋势，最新热点，技术热点切换方向），从而调整他们的工作方向。

## 组件模块

- 信息获取系统（定向抓取整理GenAI相关的数据源上的信息)
  - github信息
    - Dify工作流
      - github_repo_analyze (用于定时运行获取某个repo某日的变更情况)
      - github_trend_analyze (用于分析github trend页面的热门项目，用于发现值得关注的新项目)
      - repo_analyze_daily_trigger (用于定时触发github_repo_analyze)
  - reddit信息（暂无）
  - youtube信息（暂无）
- 监控系统
  - Langfuse 系统（直接配置在Dify的workflow上，用于问题排查)
- 存贮组件
  - Dynamodb (用于存贮github_repo_analyze和github_trend_analyze得到的数据，Dify工作流会通过dynamodb插件对其进行读写)
- 分析系统（自动根据获取+整理的信息推断insight)
  - Claude Code (用于得到具备深度insight的分析报告)
  - Claude Skills (用于配置)

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
nohup uv run python run_tasks.py > output.log 2>&1 &

# 或直接运行
python run_tasks.py
```

### 手动运行项目分析

```bash
# 使用默认日期 (2025-10-22)
uv run python manual_run.py

# 指定分析开始日期
uv run python manual_run.py --date 2025-10-28

# 使用短参数
uv run python manual_run.py -d 2025-10-28
```

## Dify Analyze API调用示例

### HelloGitHub日报触发

```bash
curl -X POST 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run' \
--header 'Authorization: Bearer <token>' \
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
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {"repo": "https://github.com/vllm-project/vllm", "start_date":"2024-10-27"},
  "response_mode": "blocking",
  "user": "github_analyzer"
}'
```