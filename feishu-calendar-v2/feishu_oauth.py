#!/usr/bin/env python3
"""
飞书 OAuth 授权流程 - 获取 user_access_token
一次性运行，完成后 token 会存到 ~/.hermes/.env
"""
import urllib.request
import urllib.parse
import json
import os
import webbrowser
from threading import Thread
import time

APP_ID = 'YOUR_APP_ID'
APP_SECRET = 'MjtlozmlObB0l7iLn5PKqcEXqjXMyqd3'
REDIRECT_URI = 'http://localhost:8765/callback'

def start_server():
    """启动本地HTTP服务器接收callback"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if '/callback' in self.path:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Authorized!</h1><p>You can close this page.</p></body></html>')
                # 提取code
                query = urllib.parse.parse_qs(self.path.split('?')[1])
                self.server.auth_code = query.get('code', [''])[0]
                self.server.auth_received = True
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            pass  # 静默
    
    server = HTTPServer(('localhost', 8765), Handler)
    server.auth_received = False
    return server

def main():
    print('=== 飞书 OAuth 授权 ===\n')
    
    # 1. 构造授权URL
    params = urllib.parse.urlencode({
        'app_id': APP_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'calendar_oauth',
        'response_type': 'code',
    })
    auth_url = f'https://open.feishu.cn/open-apis/authen/v1/authorize?{params}'
    
    print(f'授权链接: {auth_url}\n')
    
    # 2. 打开浏览器
    print('正在打开浏览器...')
    webbrowser.open(auth_url)
    
    # 3. 启动本地server等callback
    print('等待授权回调...')
    server = start_server()
    server.handle_request()  # 处理一次请求
    
    code = getattr(server, 'auth_code', None)
    if not code:
        print('未收到授权码，流程取消')
        return
    
    print(f'收到授权码: {code[:20]}...\n')
    
    # 4. 用code换user_access_token
    print('交换token...')
    url = 'https://open.feishu.cn/open-apis/authen/v1/oidc/access_token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'app_id': APP_ID,
        'app_secret': APP_SECRET,
    }
    req = urllib.request.Request(url,
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if result.get('code') != 0:
                msg = result.get('msg', 'unknown error')
                print(f'Exchange failed: {msg}')
                return
            
            data = result.get('data', {})
            access_token = data.get('access_token', '')
            refresh_token = data.get('refresh_token', '')
            expires_in = data.get('expires_in', 0)
            
            print(f'✅ 成功! access_token: {access_token[:20]}...')
            print(f'   refresh_token: {refresh_token[:20]}...')
            print(f'   有效期: {expires_in}秒\n')
            
            # 5. 存到 ~/.hermes/.env
            env_path = os.path.expanduser('~/.hermes/.env')
            env_content = f'''FEISHU_USER_ACCESS_TOKEN={access_token}
FEISHU_USER_REFRESH_TOKEN={refresh_token}
FEISHU_USER_TOKEN_EXPIRES_IN={expires_in}
FEISHU_USER_TOKEN_CREATE_AT={int(time.time())}
'''
            with open(env_path, 'a' if os.path.exists(env_path) else 'w') as f:
                f.write(env_content)
            print(f'✅ token已保存到 {env_path}')
            
    except urllib.error.HTTPError as e:
        print(f'交换失败: {e.read().decode()}')

if __name__ == '__main__':
    main()
