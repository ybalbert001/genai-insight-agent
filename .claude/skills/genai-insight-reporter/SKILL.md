---
name: genai-insight-reporter
description: "Generate comprehensive GenAI project insight reports with community activity analysis (including project health metrics, community engagement patterns, and star growth), important feature updates, and cloud provider integrations. Use when asked to create, generate, or produce GenAI insight reports, analysis reports for GenAI projects, or reports analyzing GitHub repository trends for AI/ML projects. Automatically fetches data from DynamoDB, analyzes trends with domain-specific context, generates matplotlib charts, and outputs formatted markdown reports with interpreted insights."
---

# GenAI Insight Reporter

## Overview

Generates comprehensive insight reports for GenAI open-source projects by analyzing GitHub data stored in DynamoDB. The skill:

1. Fetches data from DynamoDB tables (github-insight-raw-data, genai-repo-watchlist)
2. Analyzes community activity metrics over 15-day windows with interpretation:
   - Project health indicators (Merged PR / New PR ratios)
   - Community engagement patterns (Issue vs PR balance)
   - Star growth trends
   - Domain-specific insights for different project types
3. Identifies important feature updates and cloud provider integrations
4. Generates academic-style matplotlib visualizations
5. Produces formatted markdown reports with embedded charts and interpreted insights

## Quick Start

**Note**: This skill uses a two-stage workflow - scripts extract and filter data, then Claude curates and generates the final report.

### Stage 1: Extract Initial Data

```bash
python scripts/report_generator.py \
  --dynamodb-script /path/to/genai-rawdata-retriever/scripts/dynamodb_manager.py \
  --output-dir report_output_draft \
  --max-features 15  # Get more candidates for review
```

This will:
- Analyze Human-P0 priority repos from the last 15 days
- Generate activity trend charts (Daily PRs, Merged PRs, Issues)
- Extract feature updates (type=Feat, importance=High)
- Identify potential cloud provider integrations (keyword-based)
- Output draft report to `report_output_draft/GenAI_Insight_Report_YYYYMMDD.md`

### Stage 2: Claude Review and Curation (Required)

Claude must then:
1. **Read the draft report** to see filtered candidates
2. **Access raw DynamoDB data** via genai-rawdata-retriever skill for full PR context
3. **Evaluate significance**: Determine which features are truly important
4. **Rewrite descriptions**: Condense verbose meanings, preserve technical terms
5. **Validate cloud integrations**: Verify keyword matches are genuine integrations
6. **Generate final report**: Create polished markdown with curated content and charts

## When to Use This Skill

Use this skill when the user requests:
- "Generate a GenAI insight report"
- "Create the latest GenAI project analysis"
- "Produce a report on GenAI repo activity"
- "Analyze recent GenAI project updates"
- "Give me insights on GenAI open-source projects"

## Report Structure

The generated report includes:

### 1. Community Activity Analysis
- Matplotlib charts showing 15-day trends
- Three metrics: Daily New PRs, Daily Merged PRs, Daily New Open Issues
- Multi-line charts for cross-repo comparison
- Summary table with:
  - 日均新增PR (Average Daily New PRs)
  - 日均Merged PR (Average Daily Merged PRs)
  - 日均新增Issue (Average Daily New Issues)
  - Star总量 (Total Stars) - current total star count
- **Interpretation** (CRITICAL: Maximum 5 sentences):
  - Must focus on **domain insights (领域洞察)** as the primary element
  - Structure: 1-2 sentences on patterns, 2-3 sentences on domain insights, 0-1 on trends
  - Domain categories monitored:
    - LLM inference engines (vLLM, SGLang)
    - Low-code LLM platforms (Dify)
    - Vertical AI agents (Cline)
    - LLM fine-tuning platforms (LLaMA-Factory)
    - LLM gateways/proxies (LiteLLM)

### 2. Important Feature Updates
- Filters for `type=Feat` AND `importance=High`
- Extracts from most recent 1-2 days of data
- Maximum 5 total features, 3 per repo
- Focuses on technically significant updates

### 3. Cloud Provider Integrations
- Identifies GenAI cloud service integrations:
  - AWS: Bedrock, SageMaker
  - Azure: OpenAI Service
  - GCP: Vertex AI
  - Alibaba Cloud
- Excludes refactor and documentation PRs

### 4. Emerging Insights (Optional, High-quality only)
- Analyzes AI industry trends from tldr.tech/ai
- Correlates trending topics with repo changes
- Generates forward-looking insights
- **Requirements**: High standard, must include confidence tags [High, Medium, Low]
- **Source**: Past 7 days of tldr.tech/ai newsletters
- **Process**: Claude analyzes trends → finds correlations → generates insights

## Usage

### Two Workflow Options

#### Option A: Draft + Review Workflow (Recommended)

**Step 1**: Generate draft report with initial filtering:
```bash
python scripts/report_generator.py \
  --dynamodb-script <path-to-dynamodb-manager.py> \
  --output-dir report_output_draft \
  --max-features 15
```

**Step 2**: Claude reads draft, accesses DynamoDB for full context, curates content, and generates final report

#### Option B: JSON Extraction for Detailed Review

**Step 1**: Extract raw data as JSON for Claude to review:
```bash
python scripts/data_extractor.py \
  --dynamodb-script <path-to-dynamodb-manager.py> \
  --output candidates.json
```

**Step 2**: Claude reads JSON, evaluates each candidate, rewrites descriptions, and builds report from scratch

### Basic Report Generation (Automated Only)

For quick automated reports without manual curation:

```bash
python scripts/report_generator.py \
  --dynamodb-script <path-to-dynamodb-manager.py> \
  --output-dir <output-directory>
```

Note: This produces a report based solely on automated filtering and may include low-quality or verbose descriptions.

### Advanced Options

```bash
python scripts/report_generator.py \
  --dynamodb-script /path/to/dynamodb_manager.py \
  --output-dir custom_reports \
  --region us-west-2 \
  --days 20 \
  --max-features 8 \
  --max-features-per-repo 4
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dynamodb-script` | (required) | Path to genai-rawdata-retriever's dynamodb_manager.py |
| `--output-dir` | `report_output` | Directory for generated reports and charts |
| `--region` | `us-east-1` | AWS region for DynamoDB access |
| `--days` | `15` | Number of days to analyze for trends |
| `--max-features` | `5` | Maximum total feature updates to include |
| `--max-features-per-repo` | `3` | Maximum features per individual repo |

## Analysis Criteria

### Data Scope
- **Repos**: Only `priority=Human-P0` from genai-repo-watchlist
- **Time Window**: Last 15 days for trends, last 1-2 days for feature updates
- **Data Quality**: Filters out anomalies (increments > 3σ from mean)

### Feature Selection
Important features must meet ALL criteria:
- `type = "Feat"` (not FixBug, Doc, Refactor, etc.)
- `importance = "High"` (not Medium or Low)
- From most recent available day (today or yesterday)

### Cloud Integration Detection
Identifies PRs mentioning GenAI cloud services:
- Keywords: bedrock, sagemaker, azure, openai, vertex, gcp, alibaba, aliyun
- Excludes: Refactor, Doc, Chore type PRs
- Focus: Integration with AI/ML specific services

### Community Metrics Interpretation

**IMPORTANT: Keep interpretation concise - maximum 5 sentences total. Focus on domain insights.**

When analyzing and interpreting community activity data, the report includes:

#### Metrics Provided
- **日均新增PR** (Average Daily New PRs): Total PR volume (open + merged)
- **日均Merged PR** (Average Daily Merged PRs): PRs successfully merged
- **日均新增Issue** (Average Daily New Issues): New issues opened
- **Star总量** (Total Stars): Current total star count

#### Interpretation Guidelines

**Critical**: Your interpretation must be:
1. **Concise**: Maximum 5 sentences total
2. **Domain-focused**: Emphasize domain insights (领域洞察) as the most important element
3. **Actionable**: Provide insights that matter to GenAI practitioners

**Structure your interpretation as**:
- 1-2 sentences on overall patterns across projects
- 2-3 sentences on domain insights (THIS IS THE MOST IMPORTANT PART)
- 0-1 sentence on notable trends

**For domain insights, consider**:
- **Inference Engines** (vLLM, SGLang): Performance optimization trends, hardware support
- **Platforms** (Dify): Feature breadth, integration ecosystem
- **Agents** (Cline): User experience, workflow automation
- **Fine-tuning** (LLaMA-Factory): Model support, training efficiency
- **Gateways** (LiteLLM): Provider compatibility, API standardization

**Example of good interpretation** (concise, domain-focused):
```
vLLM和SGLang保持高PR活跃度，反映推理引擎竞争激烈。Dify的Star总量领先显示低代码平台市场需求旺盛。领域洞察：推理引擎重点转向多模态支持，应用平台注重集成广度，微调工具进入成熟期开发放缓。LiteLLM快速迭代体现多云多模型适配压力。整体上，GenAI基础设施层技术驱动，应用层用户需求驱动。
```

**Avoid**:
- Verbose explanations of what metrics mean
- Repetitive project-by-project descriptions
- Obvious observations without insight
- Exceeding 5 sentences

## Output Files

```
report_output/
├── GenAI_Insight_Report_20251206.md
└── images/
    └── community_activity_20251206.png
```

### Report Format

Markdown file with:
- GitHub-flavored markdown
- Embedded chart references (`![](images/chart.png)`)
- Technical terminology preserved
- Concise descriptions (avoiding verbosity)
- Metadata section with generation timestamp

### Chart Format

- PNG images at 300 DPI
- Academic paper styling (9pt Arial, thin lines)
- Horizontal layout (3 subplots)
- Date formatting: MM-DD
- Legend positioned automatically

## Module Architecture

The skill uses a modular design with both automated and AI-assisted workflows:

### Core Modules

#### `data_analyzer.py`
- Interfaces with DynamoDB via dynamodb_manager.py
- Calculates daily increment metrics
- Extracts features and cloud integrations (including PR numbers and titles)
- Filters data anomalies
- Used by both report_generator and data_extractor

#### `chart_generator.py`
- Matplotlib chart generation
- Academic paper styling configuration
- Supports multiple chart layouts (3-panel, 2x2 grid)
- Handles date formatting and legends

### Templates

#### `templates/report_template.md.j2`
- Jinja2 template for report generation
- Uses Chinese language for all sections
- Follows the standard format with:
  - 数据来源 (Data Sources)
  - 重点项目更新 (Priority Repo Updates)
  - 云厂商集成进展 (Cloud Provider Integrations)
  - 开源项目社区生态指标 (Community Activity Metrics)
  - 前瞻性信号 (Emerging Signals) - optional
- Supports PR numbers and titles when available
- Customizable template variables

### Workflow Scripts

#### `report_generator.py` (Automated Draft)
- Main orchestration script for automated workflow
- Generates draft reports with initial filtering
- Command-line interface with parameters
- Coordinates data analysis, chart generation, and markdown output
- **Output**: Draft report with charts (requires Claude review)

#### `data_extractor.py` (JSON Export for AI Review)
- Extracts raw candidate data in JSON format
- Outputs all High-importance PRs and potential cloud integrations
- Includes full PR context (_raw_pr field) for Claude to analyze
- **Output**: JSON file with candidates for Claude to curate
- **Usage**: When Claude needs detailed context for each candidate

#### `tldr_fetcher.py` (AI Trend Analysis Helper)
- Generates URLs for tldr.tech/ai newsletters (past 7 days)
- Creates fetch instructions for Claude to use with WebFetch tool
- **Output**: JSON file with URLs and extraction prompts
- **Usage**: For Section 4 (Emerging Insights) - optional, high-effort section
- **Note**: Actual fetching and analysis done by Claude using WebFetch

**Workflow Comparison**:
- `report_generator.py`: Creates draft markdown → Claude reviews/rewrites → Final report
- `data_extractor.py`: Exports JSON → Claude analyzes/selects/writes → Final report from scratch
- `tldr_fetcher.py`: Provides URLs → Claude fetches/analyzes/correlates → Adds Emerging Insights section

## Requirements

### AWS Configuration
- AWS credentials configured (`~/.aws/credentials` or environment variables)
- Access to DynamoDB tables:
  - `github-insight-raw-data`
  - `genai-repo-watchlist`
- Permissions: `dynamodb:Query`, `dynamodb:Scan`

### Python Dependencies
- Python 3.7+
- matplotlib>=3.8.0 (for chart generation)
- jinja2>=3.1.0 (for template rendering, optional but recommended)

To install dependencies:
```bash
pip install matplotlib jinja2
# or with uv:
uv pip install matplotlib jinja2
```

**Note**: If jinja2 is not installed, the skill will fall back to basic string formatting.

### Related Skills
- **genai-rawdata-retriever**: Required for accessing DynamoDB data
  - Must be installed and configured
  - Path to `scripts/dynamodb_manager.py` must be provided

## Workflow

This skill uses a **two-stage workflow** combining deterministic data processing (scripts) with AI judgment (Claude):

### Stage 1: Data Extraction and Initial Filtering (Automated)
The scripts perform deterministic operations:
- Query DynamoDB for Human-P0 repos
- Calculate daily increment metrics
- Filter PRs by type=Feat and importance=High
- Detect cloud integration keywords
- Generate matplotlib charts

### Stage 2: AI Review and Curation (Claude's Role)
**IMPORTANT**: Claude must perform these subjective tasks:

1. **Review significance**: Not all High-importance PRs are equally significant. Evaluate each feature update for:
   - Real technical impact vs incremental improvements
   - Relevance to GenAI practitioners
   - Strategic importance (new capabilities vs optimizations)

2. **Prioritize updates**: Re-rank features by actual significance, not just the importance tag:
   - Consider context: Is this a breakthrough or routine update?
   - Assess scope: Does it enable new use cases or just improve existing ones?
   - Filter out: Routine additions, minor tweaks labeled as High importance

3. **Rewrite descriptions**: Feature meanings from DynamoDB may be verbose or unclear:
   - Condense long descriptions while preserving technical terms
   - Clarify technical significance in 1-2 concise sentences
   - Ensure descriptions answer "why does this matter?"
   - Keep technical terminology intact (don't oversimplify)

4. **Validate cloud integrations**: Keyword matching may produce false positives:
   - Verify the PR actually adds/updates cloud integration
   - Confirm it's GenAI-service related (not general infrastructure)
   - Rewrite to clearly state what was integrated

5. **Generate final report**: After curation, create the markdown report with:
   - Curated and rewritten feature descriptions
   - Validated cloud integrations
   - Charts generated by scripts
   - **Community trends interpretation** (CRITICAL: Maximum 5 sentences):
     - Focus primarily on domain insights (领域洞察) - this is the most important element
     - 1-2 sentences on overall patterns
     - 2-3 sentences on domain-specific insights (inference engines, platforms, agents, etc.)
     - Use metrics as supporting evidence, not the focus
     - Be concise and actionable

### Stage 3: Emerging Insights Analysis (Optional, AI-intensive)

**This is a high-standard, optional section that requires extensive AI analysis.**

#### Step 1: Fetch AI Industry Trends
```bash
python scripts/tldr_fetcher.py --days 7 --output tldr_urls.json
```

This generates a JSON file with URLs to fetch from tldr.tech/ai.

#### Step 2: Claude Fetches and Analyzes Content
For each URL in the JSON:
1. Use **WebFetch** tool to retrieve the newsletter content
2. Extract key AI developments:
   - New model releases
   - Infrastructure developments
   - Tooling/framework updates
   - Research breakthroughs
3. Identify recurring themes and trending topics

#### Step 3: Correlate Trends with Repo Changes
Claude analyzes the connection between:
- Industry trends from tldr.tech
- Feature updates in monitored repos
- Cloud integration patterns
- Community activity shifts

#### Step 4: Generate Insights with Confidence Tags

**Insight Quality Standards** (very high bar):
- Must be **forward-looking** (not just descriptive)
- Must provide **actionable intelligence** for GenAI practitioners
- Must have **clear evidence** connecting trend to repo changes
- Must be **non-obvious** (not something easily inferred)

**Confidence Levels**:
- **High**: Multiple repos showing same pattern, clear industry trend, strong evidence
- **Medium**: Single repo but significant change, emerging trend, moderate evidence
- **Low**: Tentative connection, early signals, speculative

**Example Insights**:

```markdown
### 🔮 Emerging Insights

**Insight 1: Multi-modal inference becoming infrastructure priority** [Confidence: High]
- **Trend**: tldr.tech featured 3 major multi-modal model releases this week (GPT-4V update, Gemini 1.5 Pro, Claude 3.5 Sonnet vision)
- **Repo correlation**: Both vLLM and SGLang added multi-modal input processing in last 2 days
- **Implication**: Inference infrastructure shifting from text-only to multi-modal as default. Practitioners should prepare for multi-modal workloads.

**Insight 2: Cloud providers accelerating GenAI-specific hardware** [Confidence: Medium]
- **Trend**: AWS announced new Trainium2 chips optimized for transformer models
- **Repo correlation**: Increased AWS integration PRs in multiple repos (vLLM, LiteLLM)
- **Implication**: Possible shift toward cloud-specific optimizations vs hardware-agnostic approaches.
```

#### When to Skip This Section
- If no meaningful correlations found (don't force insights)
- If confidence level would be consistently "Low"
- If insights are obvious or already well-known
- Time constraints (this section is very time-intensive)

### Complete Workflow Steps

**Basic Workflow (Sections 1-3)**:
1. **Determine paths**: Locate dynamodb_manager.py from genai-rawdata-retriever skill
2. **Execute script**: Run report_generator.py to get raw report with charts
3. **Read generated report**: Load the report markdown and review all sections
4. **Review feature updates**:
   - Read each feature's original meaning from DynamoDB
   - Evaluate true significance
   - Rewrite descriptions to be concise yet technically accurate
   - Remove features that don't meet significance threshold
5. **Review cloud integrations**:
   - Verify each is a genuine GenAI cloud service integration
   - Remove false positives
   - Clarify integration descriptions
6. **Regenerate report**: Create final curated report with improved content (Sections 1-3)

**Extended Workflow (Add Section 4: Emerging Insights)**:
7. **Generate tldr URLs**: Run `tldr_fetcher.py` to get URLs for past 7 days
8. **Fetch AI news**: Use WebFetch tool to retrieve content from each URL
9. **Extract trends**: Analyze each newsletter for key developments and themes
10. **Correlate with repos**: Find connections between industry trends and repo changes
11. **Generate insights**: Create 2-3 high-quality insights with confidence tags
12. **Add to report**: Append Emerging Insights section if quality threshold met
13. **Present to user**: Show report path and summarize key insights

## Example Invocation by Claude

```python
# Step 1: Locate the dynamodb manager script
dynamodb_script = ".claude/skills/genai-rawdata-retriever/scripts/dynamodb_manager.py"

# Step 2: Run the report generator to get initial report
import subprocess
result = subprocess.run([
    "python3",
    ".claude/skills/genai-insight-reporter/scripts/report_generator.py",
    "--dynamodb-script", dynamodb_script,
    "--output-dir", "report_output_draft",
    "--days", "15",
    "--max-features", "15"  # Get more candidates for review
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error generating draft report:", result.stderr)
    exit(1)

# Step 3: Read the generated draft report
draft_report_path = "report_output_draft/GenAI_Insight_Report_20251206.md"
with open(draft_report_path) as f:
    draft_content = f.read()

# Step 4: Claude reviews and curates content
# Example: Read feature descriptions from DynamoDB to understand full context
# (In practice, Claude would analyze each feature here)

# Step 5: Claude rewrites feature descriptions
curated_features = [
    {
        "repo": "vllm-project/vllm",
        "description": "Added FP8 quantization support, reducing memory by 50% and doubling inference speed for large models. Significant for deployment cost reduction.",
        "significance": "high"
    },
    # ... more curated features
]

# Step 6: Generate final report with curated content
# Claude uses Write tool to create the final polished report
final_report = f"""# GenAI Insight Report - 2025-12-06

## 1. Community Activity Analysis
![Chart](images/community_activity_20251206.png)

## 2. Important Feature Updates

### vllm-project/vllm
**Feat** (High)
- Added FP8 quantization support, reducing memory by 50% and doubling inference speed for large models. Significant for deployment cost reduction.

[... more curated sections ...]
"""

# Write final report
with open("report_output/GenAI_Insight_Report_20251206.md", "w") as f:
    f.write(final_report)

print("✅ Curated report generated successfully")
```

## Troubleshooting

### No repos found
**Problem**: "No Human-P0 repos found"
**Solution**: Check genai-repo-watchlist table has entries with `priority=Human-P0`

### Missing data
**Problem**: "No data found" for specific repos
**Solution**: Verify github-insight-raw-data has recent entries for those repos

### AWS credentials error
**Problem**: Authentication failed
**Solution**: Configure AWS credentials:
```bash
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Import errors
**Problem**: "ModuleNotFoundError: No module named 'matplotlib'"
**Solution**: Install dependencies:
```bash
pip install matplotlib
# or with uv:
uv pip install matplotlib
```

### Empty charts
**Problem**: Charts generated but have no data lines
**Solution**:
- Verify data exists for the time period
- Check that increments are positive (negative increments are filtered)
- Ensure at least 2 days of data for calculating increments

## Best Practices

1. **Run regularly**: Generate reports weekly to track trends
2. **Check data quality**: Review charts for anomalies before sharing
3. **Customize parameters**: Adjust `--days` and `--max-features` based on needs
4. **Archive reports**: Keep historical reports for longitudinal analysis
5. **Verify priority**: Ensure genai-repo-watchlist is up-to-date with Human-P0 repos

## Notes

- Charts use incremental metrics (day-over-day changes), not cumulative counts
- Feature extraction prioritizes recent updates over historical significance
- Cloud integration detection is keyword-based and may require refinement
- Report length is intentionally concise to reduce reader burden
- Academic paper styling ensures charts are publication-ready
