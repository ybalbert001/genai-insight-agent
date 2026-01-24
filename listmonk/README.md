# 通过ListMonk构建订阅系统

> github repo: https://github.com/knadh/listmonk
>
> listMonk 文档: https://listmonk.app/docs/apis/apis/

## 安装ListMonk
```bash
# Download the compose file to the current directory.
curl -LO https://github.com/knadh/listmonk/raw/master/docker-compose.yml
# Run the services in the background.
docker compose up -d
```

## 创建API User(UI操作)

为了获取添加subscriber的授权
user_name : subscriber-admin
access_token: <access_token>

## 创建一个public List(UI操作)
List Name: genai-sa-newsletter
> private list不能在公网被订阅
> 此外禁用 Send opt-in confirmation

## 添加一个subscriber(API操作)
```bash
curl -u 'subscriber-admin:<access_token>' 'http://localhost:9000/api/subscribers' -H 'Content-Type: application/json' \
    --data '{"email":"subscriber@domain.com","name":"The Subscriber","status":"enabled","lists":[1],"attribs":{"city":"Bengaluru","projects":3,"stack":{"languages":["go","python"]}}}'
```

## 删除一个subscriber(API操作)
```bash
curl -u 'subscriber-admin:<access_token>' \
  -X POST 'http://localhost:9000/api/subscribers/query/delete' \
  -H 'Content-Type: application/json' \
  --data-raw '{"query":"subscribers.email = '\''ybalbert@amazon.com'\''"}'
```

## 获取List中的所有subscriber(API操作)
```bash
curl -u 'subscriber-adder:<access_token>' 'http://localhost:9000/api/subscribers??list_id=1&page=1&per_page=100'
```
