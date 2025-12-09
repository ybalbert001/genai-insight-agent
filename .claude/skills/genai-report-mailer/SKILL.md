---
name: genai-report-mailer
description: "Send GenAI insight reports via email with a sleek, geek-style HTML design. Supports multiple recipients, SMTP configuration, automatic Markdown-to-HTML conversion with embedded images, and S3 upload. Use when asked to send, email, or deliver GenAI insight reports."
---

# GenAI Report Mailer

## Overview

Sends GenAI insight reports via email with professional, geek-style HTML formatting. The skill:

1. Reads SMTP configuration and recipient list from config file
2. Converts Markdown reports to HTML with custom geek-style CSS
3. Embeds chart images as inline attachments
4. Sends multipart emails (HTML + plain text fallback)
5. Supports multiple recipients and CC/BCC
6. Optionally uploads HTML reports to S3 bucket (YYYY-mm-dd.html format)
7. Automatically generates and updates index.html page listing all reports

## Quick Start

### 1. Configure Email Settings

Create or edit the config file:

```bash
cp .claude/skills/genai-report-mailer/config/email_config.example.yaml \
   .claude/skills/genai-report-mailer/config/email_config.yaml
```

Edit `email_config.yaml` with your settings:

```yaml
smtp:
  host: smtp.gmail.com
  port: 587
  use_tls: true
  username: your-email@gmail.com
  password: your-app-password  # Use app password for Gmail

sender:
  name: GenAI Insight Bot
  email: your-email@gmail.com

recipients:
  to:
    - recipient1@example.com
    - recipient2@example.com
  cc: []
  bcc: []

email:
  subject_prefix: "[GenAI Insight]"

# S3 Upload (Optional)
s3:
  enabled: true
  bucket: your-bucket-name
  region: us-east-1
  prefix: genai-reports
```

### 2. Send a Report

```bash
python3 .claude/skills/genai-report-mailer/scripts/send_report.py \
  --report report_output/GenAI_Insight_Report_20251205.md \
  --config .claude/skills/genai-report-mailer/config/email_config.yaml
```

## When to Use This Skill

Use this skill when the user requests:
- "Send the GenAI report via email"
- "Email the insight report to [recipients]"
- "Deliver the report to the team"
- "Mail the latest GenAI analysis"

## Features

### Geek-Style HTML Design

The email template features:
- **Dark theme**: Dark background with bright text (high contrast)
- **Monospace fonts**: Code-style typography for technical content
- **Syntax highlighting**: Color-coded sections and metrics
- **Responsive layout**: Optimized for desktop and mobile
- **Inline images**: Charts embedded directly in email
- **Clean typography**: Clear hierarchy and spacing

### Email Configuration

**SMTP Providers Supported**:
- Gmail (smtp.gmail.com:587)
- Outlook/Office365 (smtp.office365.com:587)
- AWS SES (email-smtp.region.amazonaws.com:587)
- Custom SMTP servers

**Security**:
- TLS/SSL encryption support
- App password authentication (recommended for Gmail)
- Credentials stored in local config (not in code)

### Multiple Recipients

Support for:
- **To**: Primary recipients (visible to all)
- **CC**: Carbon copy recipients (visible to all)
- **BCC**: Blind carbon copy (hidden from others)

### S3 Upload (Optional)

Automatically upload HTML reports to S3:
- **File naming**: YYYY-mm-dd.html (e.g., 2025-12-09.html)
- **S3 path**: Configurable bucket and prefix
- **URL generation**: Returns S3 URL or custom domain URL
- **AWS credentials**: Supports AWS CLI, environment variables, or IAM roles
- **Requirements**: boto3 package (`pip install boto3`)
- **Auto Index**: Automatically generates index.html listing all reports

### Index Page Generation

When S3 upload is enabled, an index page is automatically generated:

**Features**:
- Lists all uploaded reports in chronological order (newest first)
- Displays report metadata: date, file size, last modified time
- Shows statistics: total report count, latest update date
- Matches the same Claude Code geek-style design as reports
- Automatically updated with each new report upload

**Access**:
- S3 URL: `https://bucket.s3.region.amazonaws.com/prefix/index.html`
- CloudFront: `https://custom-domain.com/prefix/index.html`

**Required Permissions**: `s3:PutObject`, `s3:ListBucket`

## Usage

### Basic Usage

```bash
python3 scripts/send_report.py \
  --report path/to/report.md \
  --config path/to/email_config.yaml
```

### Advanced Options

```bash
python3 scripts/send_report.py \
  --report report_output/GenAI_Insight_Report_20251205.md \
  --config config/email_config.yaml \
  --subject "Custom Subject Line" \
  --dry-run  # Preview email without sending
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--report` | Yes | Path to Markdown report file |
| `--config` | Yes | Path to email config YAML file |
| `--subject` | No | Custom email subject (overrides config) |
| `--dry-run` | No | Preview HTML without sending email |

## Configuration File Format

### email_config.yaml

```yaml
# SMTP Server Configuration
smtp:
  host: smtp.gmail.com          # SMTP server hostname
  port: 587                     # SMTP port (587 for TLS, 465 for SSL)
  use_tls: true                 # Use TLS encryption
  username: your-email@gmail.com
  password: your-app-password   # Use app-specific password

# Sender Information
sender:
  name: GenAI Insight Bot       # Display name
  email: your-email@gmail.com   # From address

# Recipient Lists
recipients:
  to:                           # Primary recipients
    - alice@example.com
    - bob@example.com
  cc:                           # CC recipients (optional)
    - manager@example.com
  bcc:                          # BCC recipients (optional)
    - archive@example.com

# Email Settings
email:
  subject_prefix: "[GenAI Insight]"  # Added to report date
  reply_to: your-email@gmail.com      # Reply-to address (optional)

# S3 Upload Configuration (Optional)
s3:
  enabled: true                       # Enable/disable S3 upload
  bucket: your-bucket-name            # S3 bucket name
  region: us-east-1                   # AWS region
  prefix: genai-reports               # Optional: S3 key prefix (folder)
  custom_domain: reports.example.com  # Optional: Custom domain for URLs
```

### Gmail Setup

For Gmail, you need to use an **App Password**:

1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use this password in `email_config.yaml`

## HTML Template Design

The geek-style template includes:

### Color Scheme
- Background: `#0d1117` (GitHub dark)
- Text: `#c9d1d9` (light gray)
- Headings: `#58a6ff` (blue)
- Accent: `#f85149` (red), `#56d364` (green)
- Code blocks: `#161b22` background

### Typography
- Headers: `-apple-system, BlinkMacSystemFont, 'Segoe UI'`
- Body: `'Courier New', Courier, monospace`
- Metrics: `'SF Mono', 'Monaco', 'Inconsolata'`

### Layout Sections
1. **Header**: Report title and date
2. **Data Sources**: GitHub repos and sources
3. **Priority Updates**: Feature highlights with PR links
4. **Cloud Integrations**: Provider-specific updates
5. **Community Metrics**: Chart and interpretation
6. **Footer**: Generation timestamp and branding

## Output

### Email Structure

```
From: GenAI Insight Bot <your-email@gmail.com>
To: recipient1@example.com, recipient2@example.com
Subject: [GenAI Insight] Report - 2025-12-05

[Multipart message]
├── text/plain (Markdown fallback)
└── text/html (Geek-style HTML)
    └── inline images (charts)
```

### Preview Mode

Use `--dry-run` to preview:
- Saves HTML to `preview.html`
- Opens in default browser
- No email sent

## Workflow Integration

### With genai-insight-reporter

```bash
# Step 1: Generate report
python3 .claude/skills/genai-insight-reporter/scripts/report_generator.py \
  --dynamodb-script path/to/dynamodb_manager.py \
  --output-dir report_output \
  --date 2025-12-05

# Step 2: Send via email
python3 .claude/skills/genai-report-mailer/scripts/send_report.py \
  --report report_output/GenAI_Insight_Report_20251205.md \
  --config .claude/skills/genai-report-mailer/config/email_config.yaml
```

### Automated Daily Reports

```bash
#!/bin/bash
# daily_report.sh

DATE=$(date +%Y-%m-%d)

# Generate report
python3 scripts/report_generator.py \
  --date $DATE \
  --output-dir reports

# Send email
python3 scripts/send_report.py \
  --report reports/GenAI_Insight_Report_${DATE//-/}.md \
  --config config/email_config.yaml

echo "Report sent for $DATE"
```

## Requirements

### Python Dependencies

```bash
pip install pyyaml markdown2 premailer boto3
# or with uv:
uv pip install pyyaml markdown2 premailer boto3
```

- **pyyaml**: Parse YAML config files
- **markdown2**: Convert Markdown to HTML
- **premailer**: Inline CSS for email compatibility
- **boto3**: AWS SDK for S3 upload (optional, only needed if S3 upload is enabled)

### Python Version

- Python 3.7+

## Troubleshooting

### SMTP Authentication Failed

**Problem**: "Authentication failed" error

**Solutions**:
- Gmail: Use app password instead of account password
- Verify username and password in config
- Check 2FA settings

### Connection Refused

**Problem**: "Connection refused to SMTP server"

**Solutions**:
- Verify SMTP host and port
- Check firewall settings
- Try port 465 (SSL) instead of 587 (TLS)

### Images Not Displaying

**Problem**: Charts not showing in email

**Solutions**:
- Ensure chart files exist at specified paths
- Check image file permissions
- Some email clients block external images (inline images should work)

### Email Goes to Spam

**Problem**: Emails landing in spam folder

**Solutions**:
- Use authenticated SMTP (not relay)
- Add SPF/DKIM records to your domain
- Ask recipients to whitelist sender address
- Avoid spam trigger words in subject

### S3 Upload Issues

**Problem**: AWS credentials not found or access denied

**Solutions**:
- Configure AWS CLI: `aws configure`
- Ensure IAM policy includes `s3:PutObject` permission
- Install boto3 if needed: `pip install boto3`

## Best Practices

1. **Security**:
   - Never commit `email_config.yaml` with real credentials
   - Use environment variables for CI/CD
   - Use app passwords instead of account passwords
   - Keep config file in `.gitignore`

2. **Testing**:
   - Always test with `--dry-run` first
   - Send test emails to yourself before production
   - Verify HTML rendering in multiple email clients

3. **Scheduling**:
   - Use cron for automated daily reports
   - Add error handling and logging
   - Set up alerts for send failures

4. **Recipients**:
   - Keep recipient lists in config, not code
   - Use BCC for large distribution lists
   - Provide unsubscribe mechanism if needed

## Example Invocation by Claude

```python
import subprocess

# After generating report
report_path = "report_output/GenAI_Insight_Report_20251205.md"
config_path = ".claude/skills/genai-report-mailer/config/email_config.yaml"

result = subprocess.run([
    "python3",
    ".claude/skills/genai-report-mailer/scripts/send_report.py",
    "--report", report_path,
    "--config", config_path
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Report sent successfully!")
    print(result.stdout)
else:
    print(f"❌ Failed to send report:")
    print(result.stderr)
```

## Notes

- Email template is optimized for common email clients (Gmail, Outlook, Apple Mail)
- Inline CSS ensures consistent rendering across clients
- Plain text fallback provided for non-HTML email clients
- Charts are embedded as inline images (not external links)
- Configuration file is excluded from version control for security
