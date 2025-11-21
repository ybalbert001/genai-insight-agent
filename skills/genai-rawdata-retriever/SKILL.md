---
name: genai-rawdata-retriever
description: "Retrieve and query GenAI project raw data from DynamoDB tables (github-insight-raw-data and github-trend-repo-candidates). With the data, 1) you can get the analysis of repository on the specified date. 2) you can get the repository in the github trending page on the specified date."
---

# GenAI Raw Data Retriever

## Overview

Retrieve raw data from DynamoDB tables for GenAI project insights. Returns JSON-formatted data from `github-insight-raw-data` (repo analysis) and `github-trend-repo-candidates` (trending repos).

## Prerequisites

- AWS credentials configured (via `~/.aws/credentials` or environment variables)
- Access to DynamoDB tables in `us-east-1` region:
  - `github-insight-raw-data`
  - `github-trend-repo-candidates`
- Python 3.x with boto3 installed

## Available Operations

The skill uses `scripts/dynamodb_manager.py` which supports the following operations:

### 1. Get Single Item
Retrieve data for a specific repository on a specific date.

```bash
python scripts/dynamodb_manager.py [--table TABLE] get <project_url> <collect_date> [--json]
```

### 2. Query by Date Range
Query historical data for a repository within a date range.

```bash
python scripts/dynamodb_manager.py [--table TABLE] query <project_url> [--start START_DATE] [--end END_DATE] [--json]
```

### 3. Scan Table
Scan all items in the table (use with caution on large tables).

```bash
python scripts/dynamodb_manager.py [--table TABLE] scan [--limit LIMIT] [--json]
```

### 4. Put Item
Add or update repository data.

```bash
python scripts/dynamodb_manager.py [--table TABLE] put <project_url> <collect_date> --data '{"key": "value"}'
```

### 5. Delete Item
Remove repository data for a specific date.

```bash
python scripts/dynamodb_manager.py [--table TABLE] delete <project_url> <collect_date> [--confirm]
```

## Data Schema

Both tables use the same schema:

- **Partition Key**: `project_url` (String) - GitHub repository URL
- **Sort Key**: `collect_date` (String) - Collection date in YYYY-MM-DD format
- **Additional Attributes**: Varies by table (JSON data)

### Table Descriptions

- **github-insight-raw-data**: Contains detailed repository analysis data (stars, forks, commits, contributors, etc.)
- **github-trend-repo-candidates**: Contains repositories that appeared on GitHub trending page on specific dates

For detailed data schema documentation including field types, PR categories, and importance levels, see [references/data_schema.md](references/data_schema.md) or [references/example_trend_repo_response.json](references/example_trend_repo_response.json).

For a sample response structure, see [references/example_response.json](references/example_response.json) or [references/example_trend_repo_response.json](references/example_trend_repo_response.json).

## Usage Examples

**Note**: All commands below assume you are in the skill's root directory (`skills/genai-rawdata-retriever`).

### Example 1: Get Repository Analysis for a Specific Date

```bash
python scripts/dynamodb_manager.py --table github-insight-raw-data get \
  https://github.com/vllm-project/vllm \
  2025-01-15 \
  --json
```

**Use case**: Analyze how a specific repository performed on a particular date.

### Example 2: Query Historical Trending Data

```bash
python scripts/dynamodb_manager.py --table github-trend-repo-candidates query \
  https://github.com/vllm-project/vllm \
  --start 2025-01-01 \
  --end 2025-01-07 \
  --json
```

**Use case**: Track when a repository appeared on GitHub trending page during a week.

### Example 3: Get Recent Repository Data

```bash
python scripts/dynamodb_manager.py --table github-insight-raw-data query \
  https://github.com/vllm-project/vllm \
  --start 2025-01-01 \
  --json
```

**Use case**: Retrieve all repository analysis data from January 2025 onwards.

### Example 4: Scan Recent Trending Repositories

```bash
python scripts/dynamodb_manager.py --table github-trend-repo-candidates scan \
  --limit 20 \
  --json
```

**Use case**: Get a sample of recent trending repositories for analysis.

## Common Use Cases

### 1. Repository Growth Analysis
Query historical data from `github-insight-raw-data` to track metrics over time (stars, forks, commits).

### 2. Trending Pattern Detection
Query `github-trend-repo-candidates` to identify when repositories gained popularity.

### 3. Cross-Repository Comparison
Use scan or multiple queries to compare different repositories on the same date.

### 4. Time-Series Data Export
Query date ranges and export to JSON for visualization or further analysis.

## Integration with Claude Code

When using this skill with Claude Code:

1. Claude can directly execute the Python script to retrieve data
2. All operations return JSON format when `--json` flag is used
3. Results can be analyzed, compared, or visualized programmatically
4. Date formats must be YYYY-MM-DD (e.g., "2025-01-15")

## Parameters Reference

### Global Parameters
- `--table`: Choose table (`github-insight-raw-data` or `github-trend-repo-candidates`). Default: `github-insight-raw-data`
- `--region`: AWS region. Default: `us-east-1`

### Output Parameters
- `--json`: Output in JSON format (recommended for programmatic use)
- `--limit`: Maximum number of items to return (scan operation only)

### Date Parameters
- `collect_date`: Single date in YYYY-MM-DD format
- `--start`: Start date for range queries (inclusive)
- `--end`: End date for range queries (inclusive)

## Troubleshooting

### Authentication Errors
Ensure AWS credentials are properly configured:
```bash
aws configure
# or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Table Not Found
Verify you're using the correct table name and have access:
```bash
aws dynamodb list-tables --region us-east-1
```

### No Data Returned
- Check date format is YYYY-MM-DD
- Verify the repository URL matches exactly (including protocol)
- Try scanning the table to see available data

### Permission Errors
Ensure your AWS credentials have DynamoDB read permissions:
- `dynamodb:GetItem`
- `dynamodb:Query`
- `dynamodb:Scan`

## Notes

- **Performance**: Use `query` instead of `scan` when possible for better performance
- **Cost**: Scan operations can be expensive on large tables; use `--limit` to control costs
- **Dates**: All dates are in YYYY-MM-DD format and stored as strings
- **URLs**: Repository URLs must include the full GitHub URL (e.g., `https://github.com/owner/repo`)
