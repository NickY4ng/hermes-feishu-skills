---
name: feishu-task-v2
version: 1.0.0
description: "飞书任务管理工具。触发词：创建任务、查看任务、待办事项、任务清单、飞书任务。功能：创建、查询、更新飞书任务和清单，支持智能判断创建日历还是任务。"
---

# feishu-task-v2

全新的飞书任务管理Skill，基于飞书OpenAPI直接调用，支持完整的增删改查功能。
包含智能决策功能，自动判断应该创建日历还是任务。

## 功能特性

### ✅ 完整增删改查
- **查（Query）**: 查询任务（可按完成状态筛选）
- **增（Create）**: 创建新任务（支持截止时间、负责人）
- **改（Update）**: 修改已有任务
- **删（Delete）**: 删除任务
- **完成/重开**: 标记任务为已完成/未完成

### 🧠 智能决策
- **自动判断**: 根据用户输入判断应该创建日历还是任务
- **规则明确**:
  - **日历**: 有明确开始和结束时间（如"9:30-11:00"）
  - **任务**: 只有截止时间或无时间（如"下午前要交"）
- **置信度评估**: 提供决策置信度和理由

### 🔧 技术特点
- 基于飞书 OpenAPI 直接调用
- 使用 `tenant_access_token`（应用身份）调用
- 创建任务时**自动将当前用户设为负责人和关注人**
- 默认用户 open_id：`YOUR_USER_OPEN_ID`

## 使用方法

### 基本导入
```python
from skills.feishu_task import FeishuTask

# 创建客户端
task_client = FeishuTask()

# 或者使用便捷函数
from skills.feishu_task import (
    query_tasks, create_task, update_task,
    delete_task, complete_task, get_my_tasks
)
```

### 功能示例

#### 1. 查询任务
```python
# 查询所有任务
tasks = query_tasks()

# 查询未完成任务
incomplete_tasks = query_tasks(completed=False)

# 查询已完成任务
completed_tasks = query_tasks(completed=True)
```

#### 2. 创建任务
```python
# 创建带截止时间的任务（自动将当前用户设为负责人+关注人）
task_guid = create_task(
    summary="完成月度报告",
    description="整理数据并生成报告",
    due_time="2026-04-02T18:00:00+08:00"
)

# 创建无截止时间的任务
task_guid = create_task(
    summary="阅读行业报告",
    description="抽空阅读最新行业分析"
)
```

#### 3. 修改任务
```python
# 修改任务标题和描述
updated_task = update_task(
    task_guid="xxx",
    summary="新标题",
    description="更新后的描述"
)

# 标记任务为已完成
update_task(task_guid="xxx", completed=True)

# 或者使用便捷函数
complete_task(task_guid="xxx")
```

#### 4. 删除任务
```python
success = delete_task(task_guid="xxx")
```

#### 5. 智能决策
```python
from skills.feishu_task import analyze_task_type

# 分析应该创建日历还是任务
analysis = analyze_task_type("今天下午3点前完成报告")
print(analysis)
# 输出: {"type": "task", "confidence": 0.8, "reason": "只有截止时间，无具体时长"}

analysis = analyze_task_type("上午9:30-11:00开会")
print(analysis)  
# 输出: {"type": "calendar", "confidence": 0.9, "reason": "有明确时间范围"}
```

## 与feishu-calendar-v2配合使用

### 完整工作流
```python
from skills.feishu_task import analyze_task_type
from skills.feishu_calendar import create_event
from skills.feishu_task import create_task

def smart_create_schedule(user_input):
    """智能创建日程或任务"""
    analysis = analyze_task_type(user_input)
    
    if analysis["type"] == "calendar":
        # 提取时间信息并创建日历
        # 这里需要实际的时间解析逻辑
        event_id = create_event(
            summary="会议标题",
            start_time="2026-04-02T09:30:00+08:00",
            end_time="2026-04-02T11:00:00+08:00"
        )
        return {"type": "calendar", "event_id": event_id}
    else:
        # 创建任务
        task_guid = create_task(
            summary="待办事项",
            description=user_input
        )
        return {"type": "task", "task_guid": task_guid}
```

## 测试

运行完整测试套件：
```bash
cd ~/.hermes/skills/productivity/feishu-task-v2
python3 test_task.py
```

运行冒烟测试：
```bash
python3 smoke_test.py
```

运行智能决策测试：
```bash
python3 test_decision.py
```

## 设计原则

1. **自动设负责人**: 每次创建任务自动将当前用户设为负责人和关注人
2. **真实 API**: 直接调用飞书 Open API，非模拟数据
3. **简单直接**: 直接调用 OpenAPI，无中间层
4. **完整测试**: 每个功能都有对应测试

## 版本历史

- **v1.0.0** (2026-04-02): 初始版本
- **v1.1.0** (2026-04-22): 创建任务时自动将当前用户设为负责人+关注人