# Data Schema Reference

## Table: github-insight-raw-data

Repository analysis data collected daily.

### Keys
- **project_url** (String, Partition Key): Full GitHub repository URL
  - Example: `https://github.com/vllm-project/vllm`
- **collect_date** (String, Sort Key): Date in YYYY-MM-DD format
  - Example: `2025-11-20`

### Attributes

#### metric_info (Map)
Basic repository metrics:
- **stars** (String): Total star count
- **forks** (String): Total fork count
- **merged_pr_count** (String): Total merged PRs
- **open_pr_count** (String): Currently open PRs
- **closed_issue_count** (String): Total closed issues
- **open_issue_count** (String): Currently open issues

#### pr_insight_list (List)
List of PR analysis objects:
- **type** (String): PR type
  - Values: `FixBug`, `Feat`, `Perf`, `Test`, `Refactor`, `Chore`, `Docs`
- **importance** (String): PR importance level
  - Values: `High`, `Medium`, `Minor`, `Low`
- **meaning** (String): Detailed analysis in Chinese

### Example Item

```json
{
  "project_url": "https://github.com/vllm-project/vllm",
  "collect_date": "2025-11-20",
  "metric_info": {
    "stars": "63600",
    "forks": "11400",
    "merged_pr_count": "15169",
    "open_pr_count": "1244",
    "closed_issue_count": "10138",
    "open_issue_count": "1906"
  },
  "pr_insight_list": [
    {
      "type": "FixBug",
      "importance": "High",
      "meaning": "修复了关键的内存泄漏问题"
    }
  ]
}
```

## Table: github-trend-repo-candidates

Repositories that appeared on GitHub trending page.

### Keys
- **project_url** (String, Partition Key): Full GitHub repository URL
- **collect_date** (String, Sort Key): Date when repo appeared on trending

### Attributes

Varies by collection method. Typically includes:
- Repository metadata
- Trending rank/position
- Language/category information
- Basic metrics at time of trending

### Example Query Patterns

#### Get single day analysis
```bash
python scripts/dynamodb_manager.py --table github-insight-raw-data get \
  https://github.com/owner/repo \
  2025-11-20 \
  --json
```

#### Query date range
```bash
python scripts/dynamodb_manager.py --table github-insight-raw-data query \
  https://github.com/owner/repo \
  --start 2025-11-01 \
  --end 2025-11-30 \
  --json
```

#### Check if repo was trending
```bash
python scripts/dynamodb_manager.py --table github-trend-repo-candidates query \
  https://github.com/owner/repo \
  --start 2025-11-01 \
  --json
```

## Data Types Note

All numeric values are stored as **strings** in DynamoDB. Convert to integers/floats when performing calculations:

```python
stars_count = int(item['metric_info']['stars'])
forks_count = int(item['metric_info']['forks'])
```

## PR Type Categories

| Type | Description |
|------|-------------|
| FixBug | Bug fixes and error corrections |
| Feat | New features and capabilities |
| Perf | Performance optimizations |
| Test | Test improvements and additions |
| Refactor | Code restructuring without behavior change |
| Chore | Maintenance tasks, dependency updates |
| Docs | Documentation updates |

## Importance Levels

| Level | Description |
|-------|-------------|
| High | Critical changes, major features, security fixes |
| Medium | Significant improvements, notable bug fixes |
| Minor | Small improvements, minor fixes |
| Low | Trivial changes, typo fixes |
