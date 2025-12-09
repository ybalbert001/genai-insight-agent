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
    - genai-rawdata-retriever (Dynamodb表读取)
    - genai-insight-reporter (报告生成)

## 报告生成

本项目使用 `genai-insight-reporter` skill 来生成分析报告。报告特点：

- **中文报告**: 报告使用中文，方便国内用户阅读
- **模板化**: 使用Jinja2模板系统，易于定制和扩展
- **标准格式**: 遵循项目定义的report_template.md格式
- **完整信息**: 包含PR编号、标题等详细信息
- **可视化**: 包含matplotlib生成的社区活跃度图表

### 快速生成报告

执行下面命令，或者`sh ./generate_report.sh`
```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
report_date=$(date -d "2 day ago" +%Y-%m-%d)
claude -p "生成${report_date}日的genai insight report, 并发送email" --dangerously-skip-permissions > report.log
```

## 分析目标

### 1. 重要更新追踪
#### 1.1 Feature更新
- 筛选条件：`type="Feat"` 且 `importance="High"`
- 时间范围：最近1天数据
- 输出限制：总计不超过5条，单个repo不超过3条

#### 1.2 云厂商集成更新
- 关注服务：AWS Bedrock/SageMaker、Azure AI、Google Cloud AI、Ali Cloud AI等GenAI相关服务
- 时间范围：最近1天数据
- 排除内容：重构类、文档类更新

### 2. 社区活跃度分析
#### 2.1 统计指标（近15天趋势）
- **新增PR总量** = (open_pr + merged_pr)的日增量
- **新增Merged PR数量** = merged_pr的日增量
- **新增Open Issue数量** = (open_issue + closed_issue)的日增量
- **新增Star数量** = star的日增量

#### 2.2 社区项目趋势解读
- **项目维护水平** = Merged PRs / New PRs（接近1为佳）
- **社区参与度** = Issues vs PRs（反映用户/贡献者比例）
- **项目关注度** = Star增长趋势
- **领域热度** = 跨项目横向对比（LLM推理引擎、LLM开发平台、垂直Agent、模型微调、LLM网关等）

### 3. 开放性Insight（需标注置信度）
- 提取 https://tldr.tech/ai/{前7天日期} 的AI行业关键信息
- 关联repos中的相关变更
- 输出格式：**[置信度：高/中/低]** Insight内容

---

## 分析要求

### 1. 数据范围
| 维度 | 筛选条件 | 时间窗口 |
|------|---------|---------|
| 仓库范围 | `priority='Human-P0'` | - |
| 统计趋势 | 近15天全量数据 | 15天 |
| Feature更新 | 最新数据 | 1天（当日或前1日）|
| 云厂商集成 | 最新数据 | 1天（当日或前1日）|

### 2. 数据处理规则
#### 2.1 异常值处理
- 若某天数据 > 15天均值的3倍 → 丢弃该数据点
- 若日增量 ≤ 0 → 丢弃该数据点（视为缺失）

#### 2.2 重要性判定
```
✅ 纳入报告：type="Feat" AND importance="High"
❌ 不纳入：type in ["FixBug", "Doc"] OR importance != "High"
```

#### 2.3 增量计算逻辑
```python
# 日增量 = 当日累计值 - 前日累计值
daily_new_prs = (open_pr_today + merged_pr_today) - (open_pr_yesterday + merged_pr_yesterday)
daily_merged = merged_pr_today - merged_pr_yesterday
daily_issues = (open_issue_today + closed_issue_today) - (open_issue_yesterday + closed_issue_yesterday)
```

### 3. 展现形式
#### 3.1 图表要求
- **工具**：matplotlib
- **风格**：学术论文风格配色
- **布局**：多子图网格排列，尺寸适中
- **结构**：4个维度子图（新增PR / 新增Merged PR / 新增Issue / 新增Star），每个子图包含所有repos的对比

#### 3.2 可视化重点
```
子图1: 新增PR数量趋势（15个采样点，多repo横向对比）
子图2: 新增Merged PR数量趋势（同上）
子图3: 新增Open Issue数量趋势（同上）
子图4: 新增star数量趋势（同上）
```

#### 3.3 文字描述规范
- ✅ 保留技术术语原文（如Transformer、inference、fine-tuning）
- ❌ 避免过度翻译专业词汇
- ✅ 简化冗余表述，聚焦核心价值, 尽可能短，只需要最有信息量的内容，降低读者的阅读负担.
  - 重要Feature更新部分，总体上不要超过5条，每个repo不要超过3条，你需要从报告根本目的出发来挑选最有价值的Feature更新。
  - 与云厂商的集成部分，总体条数不做限制，但仅仅关注与GenAI相关的服务，以AWS举例，主要关注Bedrock/SageMaker等AI相关服务。

### 4. 输出规范
#### 4.1 文件结构
```
report_output/
├── GenAI_Insight_Report_{YYYY-MM-DD}.md
└── images/
    ├── activity_trends.png
    └── ...
```

#### 4.2 语言要求
- 报告正文：中文
- 技术术语：英文原文
- 示例："该PR实现了vLLM的prefix caching优化"


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

