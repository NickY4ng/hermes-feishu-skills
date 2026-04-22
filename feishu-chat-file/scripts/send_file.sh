#!/bin/bash
# feishu-chat-file: 通过飞书聊天窗口直接发送文件

set -e

# 配置
CONFIG="${0%/*}/../references/config.yaml"

if [ -f "$CONFIG" ]; then
    APP_ID=$(grep 'app_id:' "$CONFIG" | awk '{print $2}' | tr -d '"' | tr -d "'")
    APP_SECRET=$(grep 'app_secret:' "$CONFIG" | awk '{print $2}' | tr -d '"' | tr -d "'")
    DEFAULT_RECEIVER=$(grep 'default_receiver:' "$CONFIG" | awk '{print $2}' | tr -d '"' | tr -d "'")
fi

# 参数检查
if [ $# -lt 1 ]; then
    echo "用法: $0 <文件路径> [接收者open_id]"
    exit 1
fi

FILE_PATH="$1"
RECEIVER_ID="${2:-${DEFAULT_RECEIVER:-ou_ef2ea35962c9b8aa6f68976a109eb52c}}"

if [ ! -f "$FILE_PATH" ]; then
    echo "错误: 文件不存在: $FILE_PATH"
    exit 1
fi

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo "错误: 请在 config.yaml 中配置 app_id 和 app_secret"
    exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")

echo "[发送] 准备发送文件: $FILE_NAME"
echo "[接收者] $RECEIVER_ID"

# 1. 获取访问令牌
TENANT_TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/" | \
  grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TENANT_TOKEN" ]; then
    echo "[失败] 获取访问令牌失败"
    exit 1
fi
echo "[成功] 获取访问令牌"

# 2. 上传文件
echo "[上传] 上传文件..."
UPLOAD_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -F "file_type=stream" \
  -F "file_name=$FILE_NAME" \
  -F "duration=300" \
  -F "file=@$FILE_PATH" \
  "https://open.feishu.cn/open-apis/im/v1/files")

FILE_KEY=$(echo "$UPLOAD_RESPONSE" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$FILE_KEY" ]; then
    echo "[失败] 文件上传失败"
    echo "响应: $UPLOAD_RESPONSE"
    exit 1
fi
echo "[成功] file_key: $FILE_KEY"

# 3. 发送消息
echo "[发送] 发送文件消息..."

# 构造JSON (content需要是序列化后的字符串)
MESSAGE_JSON=$(python3 -c "import json; print(json.dumps({'receive_id': '$RECEIVER_ID', 'msg_type': 'file', 'content': json.dumps({'file_key': '$FILE_KEY'})}))" )

MESSAGE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$MESSAGE_JSON" \
  "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id")

MESSAGE_ID=$(echo "$MESSAGE_RESPONSE" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$MESSAGE_ID" ]; then
    echo "[失败] 消息发送失败"
    echo "响应: $MESSAGE_RESPONSE"
    exit 1
fi

echo "[完成] 文件发送成功！"
echo "  文件名: $FILE_NAME"
echo "  消息ID: $MESSAGE_ID"
