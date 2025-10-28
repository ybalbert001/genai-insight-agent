## 如何通过curl 发送http request 触发hellogithub的日报
```bash
curl -X POST 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run' \
--header 'Authorization: Bearer app-lJpX4GANg9d6pud8ciHnh9EJ' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {"task": "获取https://hellogithub.com/ 中前5个AI相关的项目，把相关项目的信息以json形式输出。\n\n## 参考步骤：\n1. 勾选https://hellogithub.com/的AI 标签\n2. 顺序点击进入每个项目(前5个)\n3. 获取详细信息包括：Stars数量，新增stars in Past 6 days, 项目描述, url 和 tags\n\n## 参考输出格式\n[\n{\n  \"name\": \"..\",\n  \"stars\" : \"..\",\n  \"new_stars_past_7_days\" : \"..\",\n  \"description\": \"...\",\n  \"url\" : \"...\",\n  \"tags\" : [...]\n}\n..\n]"},
  "response_mode": "blocking",
  "user": "news_officer"
}'
```

## 如何通过curl 发送http request 触发github repo 分析
```bash
curl -X POST 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run' \
--header 'Authorization: Bearer app-UWkAZ1R1rFKh5ppB5iONDzSx' \
--header 'Content-Type: application/json' \
--data-raw '{
  "inputs": {"repo": "https://github.com/vllm-project/vllm", "start_date":"$start_date"},
  "response_mode": "blocking",
  "user": "github_analyzer"
}'
```

```bash
pip install schedule
```