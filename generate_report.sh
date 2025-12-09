#!/bin/bash

# 添加定时任务
# 示例：每天早上 8 点执行
# crontab -e
# 0 8 * * * /home/ubuntu/workspace/genai-insight-agent/generate_report.sh

export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1

export PATH=/home/ubuntu/.local/bin/:$PATH

# 设置工作目录
cd -- "$(dirname -- "$0")"

# 生成报告日期
report_date=$(date -d "2 day ago" +%Y-%m-%d)

# 执行命令，记录日志
claude -p "生成${report_date}日的genai insight report, 并发送email" --dangerously-skip-permissions > /tmp/report-${report_date}.log

# 可选：记录执行时间
echo "Report generated at $(date)" >> /tmp/report-${report_date}.log