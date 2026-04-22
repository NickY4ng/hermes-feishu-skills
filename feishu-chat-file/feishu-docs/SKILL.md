---
name: feishu-docs
description: 飞书云文档管理工具。触发词：创建飞书文档、新建文档、写个文档、查看飞书文档、读取飞书文档。功能：创建、读取、更新、删除飞书云文档（Docx格式）。
---

# Feishu Docs - 飞书文档管理

操作飞书新版文档(Docx)的技能，基于飞书开放平台 API 实现文档全生命周期管理。

## 功能特性

| 功能 | 说明 |
|------|------|
| 文档 CRUD | 创建、获取、更新（全量替换）、删除文档 |
| 内容追加 | 向已有文档末尾追加 Markdown/HTML 内容 |
| 内容转换 | 通过飞书服务端 API 将 Markdown/HTML 转换为文档块 |
| 块操作 | 获取文档块列表（自动分页）、插入子块、删除块 |
| 权限管理 | 添加协作者、查看权限成员列表 |
| 文件管理 | 按文件夹列出文件、按关键词搜索文档 |

## 环境变量

```bash
export FEISHU_APP_ID=YOUR_APP_ID
export FEISHU_APP_SECRET=***
```

## 核心命令

```bash
# 创建文档（含 Markdown 内容）
node bin/cli.js create -f <folder_token> -t "标题" -c "# 内容\n\n..."

# 获取文档
node bin/cli.js get -d <doc_id> --format markdown --include-content

# 追加内容
node bin/cli.js update -d <doc_id> --append -c "## 补充\n\n新内容"

# 搜索文档
node bin/cli.js search -q "关键词"

# 列出文件夹文件
node bin/cli.js list -f <folder_token>
```

## API 方法

| 方法 | 说明 |
|------|------|
| createDocument(folderToken, title) | 创建空文档 |
| getDocument(documentId) | 获取文档信息 |
| appendToDocument(documentId, content) | 向文档末尾追加内容 |
| searchDocuments(query, folderToken) | 按关键词搜索文档 |
| addPermissionMember(token, memberId, perm) | 添加权限成员 |

## 触发词
- "创建飞书文档"、"新建文档"
- "查看飞书文档"、"读取飞书文档"
- "写个文档"、"写个飞书文档"
