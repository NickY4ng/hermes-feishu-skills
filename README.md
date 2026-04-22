# hermes-feishu-skills

飞书（Feishu/Lark）技能集，为 [Hermes Agent](https://github.com/NickY4ng/hermes-feishu-skills) 打造。包含三个开源 skill：

## 技能列表

### 1. feishu-chat-file
通过飞书聊天窗口直接发送文件。文件作为消息附件出现在聊天窗口，接收者点击即可下载。

**触发词**：发我、发给你、文件发我、发个文件、发到飞书

**核心功能**：
- 上传任意文件到飞书群/会话
- 支持文本、图片、文档等所有文件类型
- 静默失败，不打扰用户

**文件结构**：
```
feishu-chat-file/
├── SKILL.md
├── scripts/
│   ├── send.sh              # 主发送脚本
│   ├── send_correct_file.sh
│   └── ...
├── feishu-docs/             # 飞书云文档管理
├── feishu-interactive-cards/# 飞书交互卡片
└── references/
```

---

### 2. feishu-calendar-v2
飞书日历管理工具，支持完整的增删改查功能。

**触发词**：查日历、看日程、今天有什么安排、创建日历、约个会议

**核心功能**：
- 查询指定时间段的日程
- 创建新日程（自动邀请日历所有者）
- 修改/删除已有日程
- 查询今日/未来日程

**使用示例**：
```python
from feishu_calendar import FeishuCalendar, query_events, create_event

# 创建日程
event_id = create_event(
    summary="会议标题",
    start_time="2026-04-02T09:30:00+08:00",
    end_time="2026-04-02T11:00:00+08:00",
    description="会议描述"
)

# 查询日程
events = query_events(
    start_time="2026-04-02T00:00:00+08:00",
    end_time="2026-04-02T23:59:59+08:00"
)
```

---

### 3. feishu-task-v2
飞书任务管理工具，支持完整的增删改查功能，包含智能决策（自动判断创建日历还是任务）。

**触发词**：创建任务、查看任务、待办事项、任务清单、飞书任务

**核心功能**：
- 查询任务（可按完成状态筛选）
- 创建任务（支持截止时间、负责人）
- 修改/删除/完成任务
- 智能判断应该创建日历还是任务

**使用示例**：
```python
from feishu_task import FeishuTask, create_task, query_tasks

# 创建任务
task_guid = create_task(
    summary="完成月度报告",
    description="整理数据并生成报告",
    due_time="2026-04-02T18:00:00+08:00"
)

# 查询任务
incomplete = query_tasks(completed=False)
```

---

## 配置说明

### 1. 创建飞书应用

1. 前往 [飞书开放平台](https://open.feishu.cn/app) 创建应用
2. 获取 `App ID` 和 `App Secret`
3. 开通所需权限：
   - **日历**：`calendar:calendar`（读写日历）
   - **任务**：`task:list`（获取任务列表）
   - **消息**：`im:message`（发送消息）

### 2. 配置环境变量

在 `~/.hermes/.env` 中添加：

```
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret_here
```

### 3. 获取用户 open_id（仅日历/任务）

```python
# 方法一：通过飞书管理后台查询用户 open_id
# 方法二：调用 API 时传入 user_open_id 参数
```

---

## 目录结构

```
hermes-feishu-skills/
├── README.md
├── LICENSE
├── feishu-chat-file/
│   ├── SKILL.md
│   ├── scripts/
│   ├── feishu-docs/
│   ├── feishu-interactive-cards/
│   └── references/
├── feishu-calendar-v2/
│   ├── SKILL.md
│   ├── feishu_calendar.py
│   ├── feishu_oauth.py
│   ├── test_calendar.py
│   └── smoke_test.py
└── feishu-task-v2/
    ├── SKILL.md
    ├── feishu_task.py
    ├── task_client.py
    ├── test_task.py
    └── smoke_test.py
```

---

## License

MIT License
