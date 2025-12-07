# Report Templates

This directory contains Jinja2 templates for generating GenAI insight reports.

## Template Files

### `report_template.md.j2`

The main Chinese language template for generating GenAI insight reports. This template follows the standard report structure defined in the project requirements.

## Template Variables

The template receives the following variables:

### Basic Information
- `date` (str): Report date in YYYY-MM-DD format
- `repo_links` (str): Comma-separated list of repository links in markdown format
- `generation_time` (str): Timestamp when report was generated

### Analysis Period
- `analysis_days` (int): Number of days analyzed (default: 15)
- `analysis_start_date` (str): Start date of analysis period
- `analysis_end_date` (str): End date of analysis period

### Feature Updates
- `features_by_repo` (list): List of repositories with important features
  - Each item contains:
    - `section_number` (str): Section number (e.g., "1.1")
    - `repo_name` (str): Short repository name (e.g., "vllm")
    - `repo_full_name` (str): Full repository name (e.g., "vllm-project/vllm")
    - `features` (list): List of feature updates
      - `title` (str): Feature title
      - `pr_number` (str): PR number (if available)
      - `pr_title` (str): PR title (if available)
      - `description` (str): Full feature description

### Cloud Integrations
- `cloud_integrations_by_repo` (list): List of repositories with cloud integrations
  - Each item contains:
    - `section_number` (str): Section number (e.g., "2.1")
    - `repo_name` (str): Short repository name
    - `repo_full_name` (str): Full repository name
    - `integrations` (list): List of cloud integrations
      - `cloud_provider` (str): Provider name (e.g., "AWS Bedrock")
      - `title` (str): Integration title
      - `pr_number` (str): PR number (if available)
      - `pr_title` (str): PR title (if available)
      - `description` (str): Full integration description

### Visualization
- `chart_image_path` (str): Relative path to activity chart image

### Analysis & Insights
- `interpretation` (str): Interpretation of community activity trends
- `emerging_insights` (str|None): Optional emerging insights section (for future use)

## Customizing the Template

### 1. Modify Existing Template

Edit `report_template.md.j2` to customize:
- Section headers and formatting
- Data presentation style
- Language and terminology
- Additional metadata

Example customization:
```jinja2
{% if features_by_repo %}
## 📊 Feature Updates This Week
{% for repo_info in features_by_repo %}
...
{% endfor %}
{% endif %}
```

### 2. Create a New Template

1. Copy `report_template.md.j2` to a new file (e.g., `report_template_en.md.j2` for English)
2. Modify the content as needed
3. Update `report_generator.py` to use the new template:

```python
# In _render_with_jinja2 method
template = env.get_template('report_template_en.md.j2')
```

### 3. Template Syntax

The templates use Jinja2 syntax:

**Variables**:
```jinja2
{{ variable_name }}
```

**Conditionals**:
```jinja2
{% if condition %}
  content
{% else %}
  alternative
{% endif %}
```

**Loops**:
```jinja2
{% for item in list %}
  {{ item.property }}
{% endfor %}
```

**Filters**:
```jinja2
{{ date|upper }}  {# Convert to uppercase #}
{{ text|default('N/A') }}  {# Default value #}
```

## Example Usage

### Basic Report Generation
```bash
python scripts/report_generator.py \
  --dynamodb-script /path/to/dynamodb_manager.py \
  --output-dir report_output
```

### Custom Parameters
```bash
python scripts/report_generator.py \
  --dynamodb-script /path/to/dynamodb_manager.py \
  --output-dir custom_reports \
  --days 30 \
  --max-features 10
```

## Template Development Tips

1. **Test with Sample Data**: Create a test script that generates template_data and renders it
2. **Use Comments**: Add Jinja2 comments for clarity: `{# This is a comment #}`
3. **Whitespace Control**: Use `-` for trimming:
   - `{{- variable }}` - trim before
   - `{{ variable -}}` - trim after
4. **Escape Special Characters**: Use `|safe` filter for HTML/markdown that should not be escaped

## Troubleshooting

### Template Not Found
Ensure the template file is in the `templates/` directory and has the `.j2` extension.

### Variable Not Rendering
Check that:
1. Variable name matches exactly (case-sensitive)
2. Variable is included in `template_data` dict in `report_generator.py`
3. Variable is not `None` or empty when expected

### Unexpected Formatting
- Check for extra whitespace in template
- Use `trim_blocks=True` and `lstrip_blocks=True` in Jinja2 environment
- Review the Jinja2 whitespace control documentation

## Resources

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- [Markdown Guide](https://www.markdownguide.org/)
