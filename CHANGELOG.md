# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-22

### Added

- **feishu-chat-file**: Send files to Feishu chat via bot API
  - Upload files and send as chat attachments
  - Supports all file types (documents, images, etc.)
  - Sub-modules: feishu-docs, feishu-interactive-cards

- **feishu-calendar-v2**: Feishu Calendar management
  - Full CRUD for calendar events
  - Auto-invite user as attendee when creating events
  - Query events by time range

- **feishu-task-v2**: Feishu Task management
  - Full CRUD for tasks
  - Auto-assign user as assignee + follower when creating tasks
  - Smart decision: auto-detect whether to create a calendar event or task

### Notes

- All three skills use `tenant_access_token` (app identity), not user identity
- App identity requires manually adding users as attendees/assignees, which is done automatically by these skills
- Open-source version: credentials and personal IDs have been replaced with placeholders
