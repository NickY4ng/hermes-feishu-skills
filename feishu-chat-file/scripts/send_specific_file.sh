#!/bin/bash
# 发送特定文件

APP_ID="YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
RECEIVER_ID="YOUR_USER_OPEN_ID"
FILE_PATH="./.openclaw/workspace/货物流向分析维度框架.md"

if [ ! -f "$FILE_PATH" ]; then
    echo "文件不存在: $FILE_PATH"
    exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")
echo "发送文件: $FILE_NAME"

# 1. 获取token
TOKEN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/")

TENANT_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TENANT_TOKEN" ]; then
    echo "获取token失败"
    exit 1
fi

# 2. 上传文件
UPLOAD_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file_type=stream" \
  -F "file_name=$FILE_NAME" \
  -F "duration=300" \
  -F "file=@$FILE_PATH" \
  "https://open.feishu.cn/open-apis/im/v1/files")

FILE_KEY=$(echo "$UPLOAD_RESPONSE" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$FILE_KEY" ]; then
    echo "上传失败"
    exit 1
fi

# 3. 发送消息
MESSAGE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TENANT_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"receive_id\":\"$RECEIVER_ID\",\"msg_type\":\"file\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}" \
  "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id")

MESSAGE_ID=$(echo "$MESSAGE_RESPONSE" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$MESSAGE_ID" ]; then
    echo "发送失败"
    exit 1
fi

echo "✅ 文件已发送到聊天窗口"
echo "消息ID: $MESSAGE_ID"