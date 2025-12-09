# GenAI Report Mailer

通过邮件发送GenAI洞察报告，支持极客风格HTML格式。

## 快速开始

### 1. 安装依赖

```bash
pip install pyyaml markdown2 boto3
# 或使用 uv:
uv pip install pyyaml markdown2 boto3
```

注：boto3 仅在启用 S3 上传功能时需要

### 2. 配置邮箱（163邮箱）

```bash
# 复制配置文件模板
cp config/email_config.example.yaml config/email_config.yaml

# 编辑配置文件，填入你的163邮箱地址
nano config/email_config.yaml
```

### 3. 设置环境变量（密码）

```bash
# 设置SMTP密码环境变量（163邮箱授权密码）
export SMTP_PASSWORD="your-163-authorization-password"
```

### 4. 发送报告

```bash
python3 scripts/send_report.py \
  --report ../../report_output/GenAI_Insight_Report_20251205.md \
  --config config/email_config.yaml
```

## 163邮箱设置步骤

1. **登录163邮箱**: https://mail.163.com
2. **进入设置**: 设置 > POP3/SMTP/IMAP
3. **开启SMTP服务**: 启用"SMTP服务"
4. **生成授权密码**:
   - 点击"生成授权密码"
   - 完成短信验证
   - 复制授权密码（**不是登录密码**）
5. **设置环境变量**:
   ```bash
   export SMTP_PASSWORD="你的授权密码"
   ```

## 预览模式

在不发送邮件的情况下预览HTML：

```bash
python3 scripts/send_report.py \
  --report path/to/report.md \
  --config config/email_config.yaml \
  --dry-run
```

会生成 `preview.html` 文件并在浏览器中打开。

## 功能特性

✅ **极客风格HTML**: 暗色主题、等宽字体、语法高亮
✅ **多收件人支持**: 支持To、CC、BCC
✅ **内联图片**: 图表直接嵌入邮件
✅ **纯文本后备**: 支持非HTML邮件客户端
✅ **环境变量**: 密码通过环境变量设置，安全可靠
✅ **多SMTP支持**: 163、Gmail、Outlook、AWS SES等
✅ **S3上传**: 可选将HTML报告上传到S3，文件名格式为 YYYY-mm-dd.html
✅ **自动索引页**: 每次上传报告时自动生成并更新 index.html，列出所有可用报告

## 配置说明

### 163邮箱配置（推荐）

```yaml
smtp:
  host: smtp.163.com
  port: 465
  use_tls: false
  use_ssl: true
  username: your-email@163.com
  password: ${SMTP_PASSWORD}  # 从环境变量读取

sender:
  name: GenAI Insight Bot
  email: your-email@163.com

recipients:
  to:
    - recipient1@example.com
    - recipient2@example.com

# S3上传（可选）
s3:
  enabled: true
  bucket: your-bucket-name
  region: us-east-1
  prefix: genai-reports  # 可选：文件夹路径
  custom_domain: reports.example.com  # 可选：CloudFront域名
```

### Gmail配置（备选）

```yaml
smtp:
  host: smtp.gmail.com
  port: 587
  use_tls: true
  use_ssl: false
  username: your-email@gmail.com
  password: ${SMTP_PASSWORD}
```

## 环境变量设置方式

### 临时设置（当前会话）

```bash
export SMTP_PASSWORD="your-password"
python3 scripts/send_report.py --report report.md --config config/email_config.yaml
```

### 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）

```bash
echo 'export SMTP_PASSWORD="your-password"' >> ~/.bashrc
source ~/.bashrc
```

### 使用 .env 文件（推荐）

```bash
# 创建 .env 文件
echo 'SMTP_PASSWORD=your-password' > .env

# 使用时加载
source .env
python3 scripts/send_report.py --report report.md --config config/email_config.yaml
```

## 与 genai-insight-reporter 集成

```bash
# 步骤1: 生成报告
python3 .claude/skills/genai-insight-reporter/scripts/report_generator.py \
  --dynamodb-script path/to/dynamodb_manager.py \
  --output-dir report_output \
  --date 2025-12-05

# 步骤2: 设置密码环境变量
export SMTP_PASSWORD="your-163-authorization-password"

# 步骤3: 发送邮件
python3 .claude/skills/genai-report-mailer/scripts/send_report.py \
  --report report_output/GenAI_Insight_Report_20251205.md \
  --config .claude/skills/genai-report-mailer/config/email_config.yaml
```

## 故障排查

### 认证失败

- **检查授权密码**: 使用163的授权密码，不是登录密码
- **检查环境变量**: `echo $SMTP_PASSWORD` 确认已设置
- **重新生成**: 在163邮箱设置中重新生成授权密码

### 连接被拒绝

- **检查端口**: 163使用465端口（SSL）
- **检查配置**: 确认 `use_ssl: true`, `use_tls: false`
- **防火墙**: 确保防火墙允许465端口

### 图片不显示

- **检查路径**: 确认图片文件存在
- **查看日志**: 脚本会显示附加的图片信息
- **邮件客户端**: 某些客户端默认屏蔽图片

### S3上传失败

- **AWS凭证**: 运行 `aws configure` 配置凭证
- **权限问题**: 确保IAM策略包含 `s3:PutObject` 和 `s3:ListBucket` 权限
- **boto3未安装**: 运行 `pip install boto3`

## S3索引页功能

当启用S3上传时，脚本会自动生成并维护一个 `index.html` 页面：

### 功能特点

- **自动更新**: 每次上传报告时自动更新索引页
- **报告列表**: 显示所有已上传的报告，按日期降序排列
- **统计信息**: 显示总报告数和最新更新时间
- **风格一致**: 使用与报告相同的 Claude Code 极客风格设计
- **直接访问**: 点击日期即可查看对应的完整报告

### 访问索引页

索引页的URL格式：

```bash
# 使用S3直接访问
https://your-bucket-name.s3.region.amazonaws.com/genai-reports/index.html

# 使用CloudFront自定义域名
https://reports.example.com/genai-reports/index.html
```

### 索引页示例

索引页包含以下内容：

1. **标题和描述**: GenAI Insight Reports
2. **统计卡片**:
   - 总报告数
   - 最新更新日期
3. **报告表格**:
   - 报告日期（可点击）
   - 文件大小
   - 最后修改时间

### CloudFront配置建议

如果使用CloudFront分发，可以设置 `index.html` 作为默认根对象：

1. 在CloudFront分发设置中
2. 设置"默认根对象"为 `index.html`（或 `genai-reports/index.html`）
3. 访问域名根路径即可自动显示索引页

## 安全最佳实践

1. ✅ **使用环境变量** 存储密码，不要直接写在配置文件中
2. ✅ **配置文件加入 .gitignore**，避免提交到版本控制
3. ✅ **使用授权密码** 而不是账号登录密码（163邮箱）
4. ✅ **定期更换** 授权密码
5. ✅ **最小权限** 只给必要的收件人

## 完整文档

详细文档请参考 [SKILL.md](SKILL.md)
