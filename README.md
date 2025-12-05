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
    - tldr.tech（暂无）
      - https://tldr.tech/ai/
    - reddit信息（暂无）
    - youtube信息（暂无）
      - https://www.youtube.com/@githubtrendfeed
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

- 列举知名开源Repo的重要更新
  - 重要Feature更新
  - 和云厂商的集成更新(与Azure，Google Cloud, Ali Cloud等的集成)
- 开源Repo的社区活跃度指标
  - 分析任务启动当天开始近15天的PR总量和Merged PR新增数量变化趋势
  - 分析任务启动当天开始近15天的Open Issue新增数量变化趋势
- 开放性Insight(标准较高，给出的时候添加confidence tag[高，中，低])
  - 自动根据 https://tldr.tech/ai/{date} 前一周的内容，来提取一些关键的AI信息
  - 结合前一步的AI信息，尝试找到当前这些repo中有关联的变更，提取有价值Insight

## 分析要求

- 【分析数据范围】
  - DynamoDB中包含了所需数据，仅仅考虑priority='Human-P0'的repos, 其他的不纳入分析。
  - 统计数据部分，考虑近15天的全部数据，不一定有15天内的全部数据，需要能适应数据部分缺失的情况。
  - 列举知名开源Repo的重要更新这部分，仅仅考虑最近一天的数据，假设当日为2025-12-05，那么考虑最近一天(2025-12-05或者2025-12-04)的数据的更新。
- 【关注点】
  - 需要利用raw data中的一些标签，比如某Pull request的属性中{"type":"Feat"，"importance":"High"}一般认为重要，其他比如type为FixBug, Doc, importance不是High的一般认为不重要，不作为Repo的重要更新纳入报告。
- 【展现形式】
  - 客观数据最好用图表展示，图不要太大，多个子图水平排列，可使用matplotlib生成图表，采用学术论文风格和配色。
  - 新增Merged PR/新增PR的占比需要有比较直观的体现，由于分析周期为近15天，建议每三天的一个数据采样点，从时间维度进行纵向对比。
  - 需要从“新增PR数量”，“新增Merged PR数量”， “新增Open Issue数量”三个维度展现，不同repo在同一个维度子图上进行横向对比，注意指标是每日增量，你需要自己计算日间差值。
  - 由于面对的不一定是相关领域的技术人员，对每个更新的描述，应该尽可能简单化。不涉及太深技术原理，重点放在解释清楚其意义。
- 【篇幅长度】
  - 尽可能短，只需要最有信息量的内容，降低读者的阅读负担。
  - 重要Feature更新部分，总体上不要超过5条，每个repo不要超过3条，你需要从报告根本目的出发来挑选最有价值的Feature更新。
  - 与云厂商的集成部分，总体条数不做限制，但仅仅关注与GenAI相关的服务，以AWS举例，主要关注Bedrock/SageMaker等AI相关服务。
- 【输出位置】
  - 报告输出到report_output/目录，文件命名格式为 GenAI_Insight_Report_{date}.md。
  - 报告引用的图片存在到report_output/images/。

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
  "https://github.com/vllm-project/vllm"
  "https://github.com/sgl-project/sglang"
  "https://github.com/langgenius/dify"
  "https://github.com/cline/cline"
  "https://github.com/BerriAI/litellm"
  "https://github.com/hiyouga/LLaMA-Factory"
)

for repo in "${repos[@]}"; do
  python3 .claude/skills/genai-rawdata-retriever/scripts/dynamodb_manager.py \
    --table genai-repo-watchlist \
    --region us-east-1 \
    put "$repo" \
    --data '{"priority": "Human-P0"}'
done
```

