#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书日历管理核心模块
基于飞书OpenAPI直接调用，支持完整的增删改查功能
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import List, Dict, Optional


# 默认用户 open_id（杨航）
DEFAULT_USER_OPEN_ID = 'YOUR_USER_OPEN_ID'


def _read_secret_from_env_file() -> Optional[str]:
    """从 ~/.hermes/.env 读取 FEISHU_APP_SECRET"""
    env_path = os.path.expanduser('~/.hermes/.env')
    if not os.path.exists(env_path):
        return None
    with open(env_path) as f:
        for line in f:
            if line.startswith('FEISHU_APP_SECRET=') and '=' in line[20:]:
                return line.strip().split('=', 1)[1].strip()
    return None


class FeishuCalendarError(Exception):
    """飞书日历错误基类"""
    pass


class FeishuCalendar:
    """飞书日历客户端"""

    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or os.environ.get('FEISHU_APP_ID') or 'cli_a93a403a0139dcd1'
        _env_secret = os.environ.get('FEISHU_APP_SECRET')
        if app_secret:
            self.app_secret = app_secret
        elif _env_secret and len(_env_secret) > 10:
            self.app_secret = _env_secret
        else:
            self.app_secret = _read_secret_from_env_file() or _env_secret
        self.access_token = None
        self.base_url = 'https://open.feishu.cn/open-apis'

    def get_access_token(self) -> str:
        """获取飞书访问令牌"""
        url = f'{self.base_url}/auth/v3/tenant_access_token/internal'
        data = json.dumps({
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') != 0:
                raise FeishuCalendarError(f"获取token失败: {result.get('msg')}")
            self.access_token = result['tenant_access_token']
            return self.access_token

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """发送 HTTP 请求"""
        if not self.access_token:
            self.get_access_token()

        url = f'{self.base_url}{endpoint}'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            # Token 过期时自动刷新重试
            if e.code == 400 and '99991663' in error_body:
                self.get_access_token()
                headers['Authorization'] = f'Bearer {self.access_token}'
                req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
                try:
                    with urllib.request.urlopen(req) as response:
                        return json.loads(response.read().decode('utf-8'))
                except urllib.error.HTTPError as e2:
                    error_body = e2.read().decode('utf-8')
            raise FeishuCalendarError(f"HTTP Error {e.code}: {error_body}")

    def query(self, start_time: str, end_time: str, user_open_id: str = None, **kwargs) -> List[Dict]:
        """
        查询日程

        Args:
            start_time: 开始时间（ISO 8601格式，如 2026-04-02T13:00:00+08:00）
            end_time: 结束时间（ISO 8601格式）
            user_open_id: 用户的 open_id，不传则使用默认用户

        Returns:
            日程列表
        """
        uid = user_open_id or DEFAULT_USER_OPEN_ID
        # 将时间转为时间戳（毫秒）
        def to_ts(s):
            s = s.replace('+08:00', '') if '+08:00' in s else s
            dt = datetime.fromisoformat(s)
            return str(int(dt.timestamp()))  # seconds, not milliseconds

        endpoint = f'/calendar/v4/calendars/primary/events?start_time={to_ts(start_time)}&end_time={to_ts(end_time)}&user_id_type=open_id'
        result = self._make_request('GET', endpoint)

        if result.get('code') != 0:
            raise FeishuCalendarError(f"查询日程失败: {result.get('msg')}")

        items = result.get('data', {}).get('items', [])
        events = []
        for item in items:
            start_obj = item.get('start_time', {})
            end_obj = item.get('end_time', {})
            # 格式化时间戳为可读字符串
            start_str = start_obj.get('timestamp', '')
            end_str = end_obj.get('timestamp', '')
            try:
                start_readable = datetime.fromtimestamp(int(start_str)).strftime('%Y-%m-%d %H:%M')
                end_readable = datetime.fromtimestamp(int(end_str)).strftime('%H:%M')
            except (ValueError, TypeError):
                start_readable = start_str
                end_readable = end_str
            events.append({
                'event_id': item.get('event_id', ''),
                'summary': item.get('summary', '无标题'),
                'start': f'{start_readable}',
                'end': f'{end_readable}',
                'description': item.get('description', ''),
            })
        return events

    def create(self, summary: str, start_time: str, end_time: str,
               description: str = "", user_open_id: str = None, **kwargs) -> str:
        """
        创建日程

        Args:
            summary: 日程标题
            start_time: 开始时间（ISO 8601格式）
            end_time: 结束时间（ISO 8601格式）
            description: 日程描述
            user_open_id: 用户的 open_id，默认设为负责人

        Returns:
            创建的日程ID
        """
        uid = user_open_id or DEFAULT_USER_OPEN_ID

        def to_ts(s):
            # API expects Unix timestamp in seconds (not milliseconds)
            s = s.replace('+08:00', '') if '+08:00' in s else s
            dt = datetime.fromisoformat(s)
            return str(int(dt.timestamp()))  # seconds, not milliseconds

        data = {
            'summary': summary,
            'start_time': {
                'timestamp': to_ts(start_time),
                'timezone': 'Asia/Shanghai'
            },
            'end_time': {
                'timestamp': to_ts(end_time),
                'timezone': 'Asia/Shanghai'
            },
            'description': description,
        }

        endpoint = '/calendar/v4/calendars/primary/events?user_id_type=open_id'
        result = self._make_request('POST', endpoint, data)

        if result.get('code') != 0:
            raise FeishuCalendarError(f"创建日程失败: {result.get('msg')}")

        event_id = result.get('data', {}).get('event', {}).get('event_id', '')

        # 把用户自己加为负责人（ attendee）
        if uid:
            try:
                self._make_request('POST',
                    f'/calendar/v4/calendars/primary/events/{event_id}/attendees?user_id_type=open_id',
                    {
                        'attendees': [{'type': 'user', 'user_id': uid, 'rsvp_comment': '负责人'}],
                        'need_notification': True
                    })
            except Exception:
                pass  # 添加失败不影响主流程

        return event_id

    def update(self, event_id: str, **kwargs) -> Dict:
        """
        修改日程

        Args:
            event_id: 日程ID
            **kwargs: 要修改的字段

        Returns:
            更新后的日程信息
        """
        data = {}
        update_fields = []

        if 'summary' in kwargs:
            data['summary'] = kwargs['summary']
            update_fields.append('summary')
        if 'description' in kwargs:
            data['description'] = kwargs['description']
            update_fields.append('description')
        def to_ts(s):
            s = s.replace('+08:00', '') if '+08:00' in s else s
            dt = datetime.fromisoformat(s)
            return str(int(dt.timestamp()))  # seconds

        if 'start_time' in kwargs:
            data['start_time'] = {'timestamp': to_ts(kwargs['start_time']), 'timezone': 'Asia/Shanghai'}
            update_fields.append('start_time')
        if 'end_time' in kwargs:
            data['end_time'] = {'timestamp': to_ts(kwargs['end_time']), 'timezone': 'Asia/Shanghai'}
            update_fields.append('end_time')

        endpoint = f'/calendar/v4/calendars/primary/events/{event_id}?user_id_type=open_id'
        result = self._make_request('PATCH', endpoint, {'update_fields': update_fields, **data})

        if result.get('code') != 0:
            raise FeishuCalendarError(f"修改日程失败: {result.get('msg')}")

        return result.get('data', {})

    def delete(self, event_id: str) -> bool:
        """
        删除日程

        Args:
            event_id: 日程ID

        Returns:
            是否删除成功
        """
        endpoint = f'/calendar/v4/calendars/primary/events/{event_id}'
        result = self._make_request('DELETE', endpoint)

        if result.get('code') != 0:
            raise FeishuCalendarError(f"删除日程失败: {result.get('msg')}")

        return True

    def get_today_events(self, user_open_id: str = None) -> List[Dict]:
        """获取今天的日程"""
        today = datetime.now()
        start_time = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        return self.query(
            start_time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            end_time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            user_open_id=user_open_id
        )

    def get_upcoming_events(self, hours: int = 24, user_open_id: str = None) -> List[Dict]:
        """获取未来指定小时内的日程"""
        now = datetime.now()
        start_time = now.isoformat()
        end_time = (now + timedelta(hours=hours)).isoformat()
        return self.query(start_time, end_time, user_open_id=user_open_id)


# 便捷函数
def query_events(start_time: str, end_time: str, **kwargs) -> List[Dict]:
    """查询日程（便捷函数）"""
    return FeishuCalendar().query(start_time, end_time, **kwargs)

def create_event(summary: str, start_time: str, end_time: str,
                 description: str = "", user_open_id: str = None, **kwargs) -> str:
    """创建日程（便捷函数）"""
    return FeishuCalendar().create(summary, start_time, end_time, description, user_open_id, **kwargs)

def update_event(event_id: str, **kwargs) -> Dict:
    """修改日程（便捷函数）"""
    return FeishuCalendar().update(event_id, **kwargs)

def delete_event(event_id: str) -> bool:
    """删除日程（便捷函数）"""
    return FeishuCalendar().delete(event_id)

def get_today_events(user_open_id: str = None) -> List[Dict]:
    """获取今天日程（便捷函数）"""
    return FeishuCalendar().get_today_events(user_open_id)

def get_upcoming_events(hours: int = 24, user_open_id: str = None) -> List[Dict]:
    """获取未来日程（便捷函数）"""
    return FeishuCalendar().get_upcoming_events(hours, user_open_id)
