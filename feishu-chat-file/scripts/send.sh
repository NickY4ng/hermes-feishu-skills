#!/bin/bash
# 飞书文件发送脚本
# 用法: send_feishu_file.sh <file_path> [chat_id]
# chat_id 默认为当前 home channel

set -e

# 读取凭据
APP_ID="YOUR_APP_ID"
APP_SECRET=$(grep FEISHU_APP_SECRET ~/.hermes/.env | cut -d= -f2)
HOME_CHAT_ID="YOUR_CHAT_ID"

# 参数
FILE_PATH="$1"
CHAT_ID="${2:-$HOME_CHAT_ID}"

if [ -z "$FILE_PATH" ]; then
    echo "用法: $0 <file_path> [chat_id]"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "文件不存在: $FILE_PATH"
    exit 1
fi

FILE_NAME=$(basename "$FILE_PATH")

# 1. 获取 token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
    -H "Content-Type: application/json" \
    -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2. 上传文件
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file_type=stream" \
    -F "file_name=$FILE_NAME" \
    -F "file=@$FILE_PATH" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('file_key','') or sys.exit(1))")

# 3. 发送文件消息
RESULT=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{\"receive_id\":\"$CHAT_ID\",\"msg_type\":\"file\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('code')==0 else d.get('msg', str(d)))")

echo "$RESULT"
