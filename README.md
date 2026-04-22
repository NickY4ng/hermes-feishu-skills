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

### 第一步：创建飞书应用

1. 前往 [飞书开放平台](https://open.feishu.cn/app)，点击「创建企业自建应用」
2. 填写应用名称（如 `Hermes-Feishu`）和描述，点击创建
3. 进入应用详情页，点击「凭证与基础信息」标签
4. 复制 `App ID`（格式：`cli_xxx`）和 `App Secret`

### 第二步：开通权限

> 权限开通路径：进入应用 → 左侧菜单「权限管理」→ 搜索并开通以下权限

**通用权限（三个 skill 都需要）：**
| 权限名称 | 权限标识 | 用途 |
|---------|---------|------|
| 获取 tenant_access_token | `auth:app_access_token` | 调用 API 的身份验证 |
| 发送消息 | `im:message` | 发送文件/文字消息 |

**feishu-calendar-v2 专用：**
| 权限名称 | 权限标识 | 用途 |
|---------|---------|------|
| 读写日历 | `calendar:calendar` | 查询/创建/修改/删除日历日程 |

**feishu-task-v2 专用：**
| 权限名称 | 权限标识 | 用途 |
|---------|---------|------|
| 获取任务列表 | `task:list` | 查询任务（**注意：需单独开通，见下方说明**） |
| 读写任务 | `task:task` | 创建/修改/删除任务 |

> ⚠️ **「获取任务列表」权限是特殊权限**：默认不显示在权限搜索列表中。需要到 [飞书开发者后台](https://open.feishu.cn/app) → 你的应用 → 「权限管理」→ 切换到「已添加的权限」Tab → 搜索 `task:list` 并手动开通。如果搜索不到，需要先在「权限管理」页面右上角开启「显示所有权限」。

### 第三步：配置环境变量

在 `~/.hermes/.env` 中添加：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxx      # 第一步复制的 App ID
FEISHU_APP_SECRET=your_app_secret_here  # 第一步复制的 App Secret
```

### 第四步：获取你的 open_id（用于日历/任务操作）

**方法一：通过飞书客户端**
1. 打开飞书 PC 客户端，点击左上角头像 →「设置」
2. 找到「账号信息」，里面就有 open_id（格式：`ou_xxx`）

**方法二：通过飞书开放平台 API**
```bash
# 用你的 App ID 和 Secret 换 open_id
curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"YOUR_APP_ID","app_secret":"YOUR_APP_SECRET"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])"
```
然后调用 [获取用户信息 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/contact-v3/user/get)，传入任意用户的手机号或邮箱，即可获取其 open_id。

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
