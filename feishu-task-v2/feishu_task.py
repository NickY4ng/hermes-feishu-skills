#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书任务管理核心模块
基于飞书OpenAPI直接调用，支持完整的增删改查功能
"""

import sys
import os

# 添加当前目录到 path，以便导入 task_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_client import FeishuTaskClient

class FeishuTaskError(Exception):
    """飞书任务错误基类"""
    pass

class FeishuTask:
    """飞书任务客户端（真实API）"""

    def __init__(self):
        """初始化任务客户端，读取 ~/.hermes/.env 中的凭据"""
        # 加载 .env
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        os.environ[k.strip()] = v.strip()

        app_id = os.environ.get('FEISHU_APP_ID')
        app_secret = os.environ.get('FEISHU_APP_SECRET')

        if not app_id or not app_secret:
            raise FeishuTaskError("FEISHU_APP_ID 或 FEISHU_APP_SECRET 未在 ~/.hermes/.env 中配置")

        self._client = FeishuTaskClient(app_id=app_id, app_secret=app_secret)
        self._client.get_access_token()

    def query(self, completed: bool = None, **kwargs) -> list:
        """查询任务
        
        注意：需要飞书开发者后台开通「获取任务列表」权限(task:list)才能使用。
        如果返回 99991663 错误，说明缺少该权限。
        """
        result = self._client.list_tasks(completed=completed)
        if result.get('code') == 99991663:
            raise FeishuTaskError(
                "获取任务列表失败：应用缺少「获取任务列表」权限。"
                "请到飞书开发者后台 → 权限管理 → 添加 task:list 权限后重试。"
            )
        if result.get('code') != 0:
            raise FeishuTaskError(f"查询失败: {result.get('msg')}")

        items = result.get('data', {}).get('items', [])
        tasks = []
        for item in items:
            tasks.append({
                "task_guid": item.get('guid') or item.get('task_id'),
                "summary": item.get('summary'),
                "description": item.get('description', ''),
                "completed": item.get('completed', False),
                "due": item.get('due') if not item.get('completed') else None
            })
        return tasks

    # 默认用户 open_id（杨航），每次创建任务自动设为负责人+关注人
    DEFAULT_USER_OPEN_ID = 'YOUR_USER_OPEN_ID'

    def create(self, summary: str, description: str = "",
               due_time: str = None, assignee_id: str = None,
               follower_ids: list = None, current_user_id: str = None,
               **kwargs) -> str:
        """创建任务"""
        # 默认把用户自己设为负责人和关注人
        if assignee_id is None:
            assignee_id = self.DEFAULT_USER_OPEN_ID
        if follower_ids is None:
            follower_ids = [self.DEFAULT_USER_OPEN_ID]

        result = self._client.create_task(
            summary=summary,
            description=description,
            due_time=due_time,
            assignee_id=assignee_id,
            follower_ids=follower_ids
        )
        if result.get('code') != 0:
            raise FeishuTaskError(f"创建任务失败: {result.get('msg')}")

        task = result.get('data', {}).get('task', {})
        # 返回 guid（UUID格式），用于后续的修改/删除操作
        return task.get('guid', task.get('task_id', ''))

    def update(self, task_guid: str, **kwargs) -> dict:
        """修改任务"""
        result = self._client.update_task(task_guid, **kwargs)
        if result.get('code') != 0:
            raise FeishuTaskError(f"修改任务失败: {result.get('msg')}")
        return result.get('data', {})

    def delete(self, task_guid: str) -> bool:
        """删除任务"""
        result = self._client.delete_task(task_guid)
        if result.get('code') != 0:
            raise FeishuTaskError(f"删除任务失败: {result.get('msg')}")
        return True

    def complete(self, task_guid: str) -> bool:
        """标记任务为已完成"""
        return self.update(task_guid, completed=True)

    def reopen(self, task_guid: str) -> bool:
        """重新打开任务"""
        return self.update(task_guid, completed=False)

    def get_my_tasks(self, completed: bool = None) -> list:
        """获取我的任务"""
        return self.query(completed=completed)

    def get_overdue_tasks(self) -> list:
        """获取已过期任务"""
        tasks = self.query(completed=False)
        overdue = []
        for task in tasks:
            if task.get('due'):
                due_ts = int(task['due'].get('timestamp', 0)) / 1000
                if due_ts < datetime.now().timestamp():
                    overdue.append(task)
        return overdue


# 便捷函数
def query_tasks(completed: bool = None, **kwargs) -> list:
    """查询任务"""
    return FeishuTask().query(completed, **kwargs)

def create_task(summary: str, description: str = "",
                due_time: str = None, assignee_id: str = None,
                current_user_id: str = None, **kwargs) -> str:
    """创建任务"""
    return FeishuTask().create(summary, description, due_time, assignee_id, current_user_id, **kwargs)

def update_task(task_guid: str, **kwargs) -> dict:
    """修改任务"""
    return FeishuTask().update(task_guid, **kwargs)

def delete_task(task_guid: str) -> bool:
    """删除任务"""
    return FeishuTask().delete(task_guid)

def complete_task(task_guid: str) -> bool:
    """标记任务为已完成"""
    return FeishuTask().complete(task_guid)

def get_my_tasks(completed: bool = None) -> list:
    """获取我的任务"""
    return FeishuTask().get_my_tasks(completed)

def get_overdue_tasks() -> list:
    """获取已过期任务"""
    return FeishuTask().get_overdue_tasks()


# 智能决策（保留原有逻辑）
def should_create_calendar(text: str) -> bool:
    text_lower = text.lower()
    import re

    task_keywords = [
        '前要', '前完成', '前交', '前提交', '前处理',
        '今天内', '今日内', '尽快', '尽快完成',
        '记得', '提醒我', '待办', 'todo',
        '办一下', '处理一下', '做一下', '完成一下',
        '抽空', '有空时', '找个时间',
    ]
    for keyword in task_keywords:
        if keyword in text_lower:
            return False

    time_range_pattern = r'\d{1,2}[:：]\d{2}\s*[-~到]\s*\d{1,2}[:：]\d{2}'
    if re.search(time_range_pattern, text_lower):
        return True

    time_range_simple = r'\d{1,2}点\s*[-~到]\s*\d{1,2}点'
    if re.search(time_range_simple, text_lower):
        return True

    if '到' in text_lower or '至' in text_lower:
        time_pattern = r'\d{1,2}[:：]?\d{0,2}'
        parts = re.split(r'[到至]', text_lower)
        if len(parts) >= 2:
            if re.search(time_pattern, parts[0]) and re.search(time_pattern, parts[1]):
                return True

    meeting_keywords = ['开会', '会议', '讨论', '评审', '汇报', '早会', '例会']
    for keyword in meeting_keywords:
        if keyword in text_lower:
            return True

    return False

def analyze_task_type(text: str) -> dict:
    is_calendar = should_create_calendar(text)
    if is_calendar:
        return {
            "type": "calendar",
            "confidence": 0.8,
            "reason": "检测到明确的时间范围，建议创建日历日程",
            "suggested_time": "请提供具体的开始和结束时间"
        }
    else:
        return {
            "type": "task",
            "confidence": 0.7,
            "reason": "未检测到明确时间范围，建议创建任务",
            "suggested_time": "可设置截止时间（可选）"
        }


if __name__ == "__main__":
    from datetime import datetime
    print("飞书任务模块测试...")

    task_client = FeishuTask()

    # 测试查询
    tasks = task_client.get_my_tasks()
    print(f"我有 {len(tasks)} 个任务")

    # 测试创建
    task_guid = task_client.create(
        summary="测试任务-Hermes连接验证",
        description="这是一条测试任务，用于验证飞书任务创建功能是否正常。",
        due_time="2026-04-22T23:59:00+08:00"
    )
    print(f"创建任务GUID: {task_guid}")

    # 测试修改
    updated = task_client.update(task_guid, summary="修改后的测试任务")
    print(f"修改结果: {updated}")

    # 测试完成
    completed = task_client.complete(task_guid)
    print(f"完成任务: {completed}")

    # 测试删除
    deleted = task_client.delete(task_guid)
    print(f"删除结果: {deleted}")

    print("测试完成！")
