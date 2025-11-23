---
name: repo-admission-filter
description: "根据客观准入规则评估GitHub趋势仓库，判断是否应纳入GenAI监控池。支持批量评估和优先级分级。"
---

# Repository Admission Filter

## 概述

根据预定义的客观准入规则自动评估GitHub趋势仓库，判断其是否应该被纳入GenAI项目监控池。所有客观标准都实现为稳定执行的代码，确保筛选过程的一致性和可重复性。

## 核心功能

1. **客观规则评估**：基于量化指标自动判断仓库是否符合准入标准
2. **优先级分级**：将符合条件的仓库分为P0-P3四个优先级
3. **批量处理**：支持对多个仓库进行批量评估

## 准入规则概览

该skill实现了完整的准入规则体系：

- **过滤条件**：AI相关、非教程、有编程语言
- **规则1**：爆发式增长（日增≥500 或 增长率≥5%）→ P0
- **规则2**：成熟项目（≥20K stars + ≥2K forks）→ P1
- **规则3**：稳定增长（5K-20K stars + 日增≥150 + ≥500 forks）→ P2
- **规则4**：官方/基础设施（关键词或知名组织）→ P2

详细规则定义、理由和示例见：**[references/admission_rules.md](references/admission_rules.md)**

## 前置条件

- Python 3.7+
- 无额外依赖（仅使用Python标准库）

## 使用方法

### 基本用法

```bash
# 评估单个仓库（从stdin）
echo '{"project_url": "...", "cumulative_stars": "15000", ...}' | python scripts/admission_filter.py

# 评估批量仓库（从文件）
python scripts/admission_filter.py input.json

# 筛选特定优先级
python scripts/admission_filter.py input.json -p P0 -p P1

# 输出到文件
python scripts/admission_filter.py input.json -o output.json

# 详细输出模式
python scripts/admission_filter.py input.json -v
```

### 示例数据

使用提供的示例数据测试：

```bash
python scripts/admission_filter.py references/example_input.json
```

## 命令行参数

### 位置参数
- `input`: 输入JSON文件路径（默认：stdin，使用"-"表示）

### 可选参数
- `-o, --output FILE`: 输出JSON文件路径（默认：stdout）
- `-p, --priority {P0,P1,P2,P3}`: 按优先级过滤，可多次指定
- `-v, --verbose`: 详细输出模式（stderr输出评估过程）

## 数据格式

### 输入格式

必需字段：

```json
{
  "project_url": "https://github.com/owner/repo",
  "collect_date": "2025-11-21",
  "cumulative_stars": "15822",
  "incremental_stars": "176",
  "forks": "1147",
  "programming_language": "Python",
  "description": "项目描述",
  "is_AI_related_project": true,
  "is_tutorial_collection": false
}
```

支持单个对象或数组格式。参考：[references/example_input.json](references/example_input.json)

### 输出格式

```json
[
  {
    "project_url": "https://github.com/sansan0/TrendRadar",
    "collect_date": "2025-11-21",
    "priority": "P0",
    "matched_rules": [
      "Rule1: Explosive Growth",
      "Rule2: Mature Project"
    ],
    "reasons": [
      "爆发式增长: +11411 stars/日",
      "成熟项目: 22,085 stars, 12,065 forks"
    ]
  },
  {
    "project_url": "https://github.com/kvcache-ai/ktransformers",
    "collect_date": "2025-11-21",
    "priority": "P2",
    "matched_rules": [
      "Rule3: Stable Growth"
    ],
    "reasons": [
      "稳定增长: 15,822 stars, +176/日, 1147 forks"
    ]
  }
]
```

## 优先级说明

| 优先级 | 含义 | 处理策略 |
|--------|------|----------|
| **P0** | 爆发式增长，需立即分析 | 24小时内深度分析 |
| **P1** | 成熟项目或重点关注 | 每日监控，每周报告 |
| **P2** | 稳定增长或基础设施 | 每周检查，每月评估 |
| **P3** | 监控池观察期 | 7天观察窗口 |
| **REJECTED** | 未通过过滤条件 | 不纳入监控 |

## 使用场景

### 场景1：快速筛选P0项目

```bash
# 只显示需要立即分析的P0项目
python scripts/admission_filter.py daily_data.json -p P0
```

### 场景2：批量评估并保存结果

```bash
# 评估所有仓库并保存到文件
python scripts/admission_filter.py trending_repos.json -o evaluation_result.json
```

### 场景3：详细评估过程

```bash
# 使用verbose模式查看详细评估过程
python scripts/admission_filter.py trending_repos.json -v
```

### 场景4：在Python中使用

```python
import json
from scripts.admission_filter import RepoAdmissionFilter

# 加载数据
with open('data.json') as f:
    repos = json.load(f)

# 评估
filter_obj = RepoAdmissionFilter()
results = filter_obj.evaluate_batch(repos)

# 处理P0项目
p0_projects = [r for r in results if r.priority.value == "P0"]
for project in p0_projects:
    print(f"🔥 {project.project_url}")
    print(f"   原因: {'; '.join(project.reasons)}")
```

## 规则阈值调整

所有阈值都定义在 `scripts/admission_filter.py` 的类常量中：

```python
class RepoAdmissionFilter:
    # 规则1：爆发式增长
    EXPLOSIVE_STARS_THRESHOLD = 500      # 单日增量stars
    EXPLOSIVE_GROWTH_RATE = 0.05         # 增长率（5%）

    # 规则2：成熟项目
    MATURE_STARS_THRESHOLD = 20000       # 累计stars
    MATURE_FORKS_THRESHOLD = 2000        # Forks数

    # 规则3：稳定增长
    STABLE_STARS_MIN = 5000              # Stars下限
    STABLE_STARS_MAX = 20000             # Stars上限
    STABLE_INCREMENTAL_MIN = 150         # 最小日增
    STABLE_FORKS_MIN = 500               # 最小forks

    # 规则4：官方/基础设施
    OFFICIAL_KEYWORDS = ["official", "sdk", "protocol", ...]
    KNOWN_ORGS = ["openai", "anthropic", ...]
```

根据GenAI领域发展情况，可以调整这些阈值。建议每季度复盘一次。

## 故障排查

### 问题：所有项目被拒绝

**排查**：
```bash
python scripts/admission_filter.py input.json -v
```

**常见原因**：
- `is_AI_related_project` 不为 true
- `is_tutorial_collection` 为 true
- `programming_language` 为空

### 问题：JSON解析错误

**排查**：
```bash
# 验证JSON格式
cat input.json | python -m json.tool
```

### 问题：输出为空

**原因**：可能使用了优先级过滤（-p）但没有该优先级的项目

**解决**：不加 `-p` 参数查看所有结果

## 最佳实践

1. **定期评估**：建议每天运行筛选，及时捕捉新趋势
2. **优先级聚焦**：
   - P0项目：立即深度分析
   - P1项目：每日监控
   - P2项目：每周检查
3. **结合定性评估**：客观规则筛选后，仍需评估技术创新性和前瞻性
4. **定期调整阈值**：每季度根据GenAI发展情况审查阈值

## 与Claude Code集成

此skill专为Claude Code设计：
- ✅ 纯Python标准库实现，无外部依赖
- ✅ JSON输入输出，便于程序化处理
- ✅ 支持stdin/stdout，便于管道操作
- ✅ 详细模式（-v）输出评估日志

## 注意事项

- ⚠️ 该skill仅实现**客观标准判断**，定性评估（技术创新性、前瞻性等）仍需人工或AI辅助
- 📊 所有数值字段支持字符串或数字格式，代码会自动转换
- 🔄 阈值应根据GenAI领域发展情况定期调整
- 📝 被拒绝的项目会标注具体拒绝原因

## 参考文档

- **[准入规则详细说明](references/admission_rules.md)** - 规则定义、理由、示例
- **[示例输入数据](references/example_input.json)** - 测试数据参考
