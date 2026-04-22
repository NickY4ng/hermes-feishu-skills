---
name: feishu-chat-file
version: 1.0.0
description: 通过飞书聊天窗口直接发送文件。文件作为消息附件出现在聊天窗口，接收者点击即可下载。
author: Hermes
trigger:
  ["发我", "发给你", "文件发我", "发个文件", "发到飞书", "发过去", "发送文件"]

## 使用方法

用户说触发词时，直接执行：

```bash
bash ~/.hermes/skills/feishu-chat-file/scripts/send.sh <file_path> [chat_id]
```

- `file_path`: 文件绝对路径（必需）
- `chat_id`: 可选，默认发到 home channel
---

# 飞书聊天文件发送 Skill

## 核心方法（2026-04-21 验证通过）

使用**绽放 bot**（`YOUR_APP_ID`）发送文件到当前会话：

**两步走：**
1. **上传文件**获取 `file_key`（`im/v1/files`，`file_type=stream`）
2. **发送文件消息**到当前 chat（`im/v1/messages`，`receive_id_type=chat_id`）

---

## 正确参数

| 参数 | 值 |
|------|-----|
| app_id | `YOUR_APP_ID`（绽放 bot） |
| app_secret | `~/.hermes/.env` 里的 `FEISHU_APP_SECRET` |
| file_type（上传） | `stream`（不是 `csv`/`file`/`image`） |
| receive_id_type（发送） | `chat_id` |
| receive_id | 当前会话 `YOUR_CHAT_ID`（或任意有效 chat_id） |

---

## curl 方式

```bash
# 1. 获取 token
TOKEN=$(curl -s 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"YOUR_APP_ID","app_secret":"你的SECRET"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2. 上传文件
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file_name=$(basename $FILE_PATH)" \
  -F "file=@$FILE_PATH" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('file_key',''))")

# 3. 发送文件消息
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"YOUR_CHAT_ID\",\"msg_type\":\"file\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}"
```

---

## 封装脚本

```bash
feishu-chat-file/scripts/send.sh <file_path> [chat_id]
```

- 默认 chat_id：`YOUR_CHAT_ID`（当前会话）
- 不需要 open_id，直接用 chat_id

---

## 常见错误

| 错误码 | 原因 | 解决 |
|--------|------|------|
| 234001 | `file_type` 用了 `csv`/`file` | 用 `stream` |
| 99992361 | `open_id cross app` | 不要用 open_id，改用 chat_id |
| 230001 | `content` 格式错误 | 必须是 `{"file_key": "..."}` JSON 字符串 |

---

## 凭证来源

- app_id：`YOUR_APP_ID`（写死在脚本里）
- app_secret：读取 `~/.hermes/.env` 的 `FEISHU_APP_SECRET`
