# GenAI Insight Agent

GenAI项目洞察分析代理，用于自动化分析GitHub项目。分析的主要目标是为了GenAI领域的从业者获取第一手，细粒度的技术洞察，帮助他们快速了解最新发展情况(技术趋势，最新热点，技术热点切换方向），从而调整他们的工作方向。

## 组件模块

- 采集模块（定向抓取整理GenAI相关的数据源上的信息)
  - 采集引擎
      - Dify工作流
        - github_repo_analyze (用于定时运行获取某个repo某日的变更情况)
        - github_trend_analyze (用于分析github trend页面的热门项目，用于发现值得关注的新项目)
        - repo_analyze_daily_trigger (用于定时触发github_repo_analyze)
  - 采集来源
    - github信息 (目前为指定的N个知名repo)
    - reddit信息（暂无）
    - youtube信息（暂无）
- 监控模块
  - Langfuse系统（直接配置在Dify的workflow上，用于问题排查)
- 存贮模块
  - Dynamodb表 (Dify工作流会通过dynamodb插件对其进行读写)
    - github-insight-raw-data (存贮github_repo_analyze)
    - github-trend-repo-candidates (存贮github_trend_analyze得到的数据)
  - Dynamodb Manager
    - 创建分析源数据表
    - 读写测试功能
- 分析系统（自动根据获取+整理的信息推断insight)
  - Claude Code (分析Agent)
  - Claude Skills 
    - Dynamodb表读取

## 分析目标

- 知名开源Repo的重要更新
- 开源Repo的社区活跃度指标
  - 近7日Open PR数量，近7日Close PR数量, 同比变化
  - Contributor的Diversity
- 开源Repo和云厂商的集成更新
  - 与Azure，Google Cloud, Ali Cloud等的集成
- 开放性Insight
  - 自动根据AI圈的热词来分析当前这些repo中比较前瞻的信号
- 自动发现新兴的repo
  - 根据一定客观的准入规则纳入重点分析的开源项目池
  - 对照本项目的根本目标来定性的判断是否值得持续关注


## Dynamodb表定义

### [表] github-insight-raw-data

| 键类型 | 属性名 | 数据类型 | 说明 |
|--------|--------|----------|------|
| HASH (分区键) | project_url | String (S) | 项目URL |
| RANGE (排序键) | collect_date | String (S) | 收集日期 |

### [表] github-trend-repo-candidates

| 键类型 | 属性名 | 数据类型 | 说明 |
|--------|--------|----------|------|
| HASH (分区键) | project_url | String (S) | 项目URL |
| RANGE (排序键) | collect_date | String (S) | 收集日期 |


## 安装依赖

使用UV包管理器（推荐）：

```bash
# 安装UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

## 手动维护观察池中的genai repos

- 创建对应dynamodb 表
```bash
python3 .claude/skills/genai-rawdata-retriever/scripts/dynamodb_manager.py --table genai-repo-watchlist --region us-east-1 create-table
```

- 添加人工指定的repos
```bash
#!/bin/bash

repos=(
  "github.com/vllm-project/vllm"
  "github.com/sgl-project/sglang"
  "github.com/langgenius/dify"
  "github.com/cline/cline"
  "github.com/BerriAI/litellm"
  "github.com/hiyouga/LLaMA-Factory"
)

for repo in "${repos[@]}"; do
  python3 .claude/skills/genai-rawdata-retriever/scripts/dynamodb_manager.py \
    --table genai-repo-watchlist \
    --region us-east-1 \
    put "$repo" 2025-11-23 \
    --data '{"priority": "human-P0"}'
done
```

