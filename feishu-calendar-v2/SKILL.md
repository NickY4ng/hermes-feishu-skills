---
name: feishu-calendar-v2
version: 1.0.0
description: "飞书日历管理工具。触发词：查日历、看日程、今天有什么安排、创建日历、约个会议、安排个时间。用于查看、创建、修改、删除飞书日历日程。"
---

# feishu-calendar-v2

飞书日历管理 Skill，基于飞书 OpenAPI 直接调用，支持完整的增删改查功能。

## 功能特性

### ✅ 完整增删改查
- **查（Query）**: 查询指定时间段的日程
- **增（Create）**: 创建新日程（自动邀请当前用户为负责人）
- **改（Update）**: 修改已有日程
- **删（Delete）**: 删除日程

### 🔧 技术特点
- 基于飞书 OpenAPI 直接调用（真实 API，非模拟数据）
- 使用 `tenant_access_token`（应用身份）调用
- 创建日程后自动将当前用户加为 attendee（收到邀请通知）
- 默认用户 open_id：`YOUR_USER_OPEN_ID`
- 时间戳格式：Unix 秒（非毫秒）

## 使用方法

### 基本导入
```python
from feishu_calendar import FeishuCalendar

# 创建客户端
calendar = FeishuCalendar()

# 或者使用便捷函数
from feishu_calendar import query_events, create_event, update_event, delete_event
```

### 功能示例

#### 1. 查询日程
```python
# 查询今天下午的日程
events = query_events(
    start_time="2026-04-02T13:00:00+08:00",
    end_time="2026-04-02T18:00:00+08:00"
)

# 或者使用客户端
events = calendar.query(
    start_time="2026-04-02T13:00:00+08:00",
    end_time="2026-04-02T18:00:00+08:00"
)
```

#### 2. 创建日程
```python
# 创建新日程（自动加当前用户为负责人，会收到飞书邀请通知）
event_id = create_event(
    summary="会议标题",
    start_time="2026-04-02T14:00:00+08:00",
    end_time="2026-04-02T15:00:00+08:00",
    description="会议描述"
)
```

#### 3. 修改日程
```python
# 修改已有日程
updated_event = update_event(
    event_id="xxx_0",
    summary="新标题",
    start_time="2026-04-02T14:30:00+08:00",
    description="更新后的描述"
)
```

#### 4. 删除日程
```python
# 删除日程
success = delete_event(event_id="xxx_0")
```

## 测试

运行冒烟测试：
```bash
cd /path/to/feishu-calendar-v2
python3 smoke_test.py
```

## 设计原则

1. **真实 API**: 直接调用飞书 OpenAPI，非模拟数据
2. **自动邀请**: 创建日程时自动将当前用户加为 attendee，收到邀请通知
3. **简单直接**: 直接调用 OpenAPI，无中间层
4. **工程化**: 符合 Skill 开发规范

## 注意事项

### 关于「应用身份」的说明

本 skill 使用 `tenant_access_token`（应用身份）调用 API，而非用户身份。

**关键点**：用应用身份创建的日程，默认不会出现在用户的个人日历里。因此本 skill 在创建日程后会自动将用户加为 attendee（`rsvp_comment: "负责人"`），这样用户才能在日历中看到这条日程并收到邀请通知。

如果你去掉了这个逻辑，行程对自己是不可见的。

### 其他注意事项

- 创建日程后，用户会收到飞书日历邀请，需要接受才能在日历中显示
- 时间格式：ISO 8601（`2026-04-02T14:00:00+08:00`）
- API 时间戳单位：秒（Unix timestamp），不是毫秒

## 版本历史

- **v1.0.0** (2026-04-02): 初始版本
- **v1.1.0** (2026-04-22): 重写，接入真实 API；修复时间戳格式（秒）；添加 attendee 自动邀请功能
