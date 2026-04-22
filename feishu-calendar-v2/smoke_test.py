#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书日历Skill冒烟测试
快速验证基本功能是否正常
"""

import sys
import os
import json
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("飞书日历Skill冒烟测试")
print(f"测试时间: {datetime.now().isoformat()}")
print("=" * 60)

test_results = []

def record_test(name, status, details=""):
    """记录测试结果"""
    test_results.append({
        "name": name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    
    if status == "passed":
        print(f"✅ {name}: 通过")
    elif status == "failed":
        print(f"❌ {name}: 失败 - {details}")
    else:
        print(f"⏭️  {name}: 跳过 - {details}")

# 测试1: 文件结构检查
print("\n1. 文件结构检查...")
required_files = [
    ("SKILL.md", "技能说明文档"),
    ("feishu_calendar.py", "核心模块"),
    ("test_calendar.py", "测试套件"),
    ("smoke_test.py", "冒烟测试")
]

all_files_ok = True
for filename, description in required_files:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        record_test(f"文件存在: {filename}", "passed", description)
    else:
        record_test(f"文件存在: {filename}", "failed", f"{description} 缺失")
        all_files_ok = False

# 测试2: 模块导入检查
print("\n2. 模块导入检查...")
try:
    from feishu_calendar import FeishuCalendar, query_events, create_event, update_event, delete_event
    record_test("模块导入", "passed", "所有模块导入成功")
except ImportError as e:
    record_test("模块导入", "failed", f"导入失败: {e}")
    all_files_ok = False

# 测试3: 类初始化
print("\n3. 类初始化测试...")
if all_files_ok:
    try:
        calendar = FeishuCalendar()
        record_test("类初始化", "passed", "FeishuCalendar初始化成功")
    except Exception as e:
        record_test("类初始化", "failed", f"初始化失败: {e}")
        all_files_ok = False
else:
    record_test("类初始化", "skipped", "文件不完整，跳过")

# 测试4: 便捷函数测试
print("\n4. 便捷函数测试...")
if all_files_ok:
    try:
        # 测试查询函数
        events = query_events(
            start_time="2026-04-02T10:00:00+08:00",
            end_time="2026-04-02T11:00:00+08:00"
        )
        record_test("查询函数", "passed", f"返回 {len(events)} 条结果")
        
        # 测试创建函数
        event_id = create_event(
            summary="冒烟测试日程",
            start_time="2026-04-02T10:00:00+08:00",
            end_time="2026-04-02T11:00:00+08:00"
        )
        record_test("创建函数", "passed", f"生成ID: {event_id}")
        
        # 测试修改函数
        updated = update_event(event_id, summary="修改后的标题")
        record_test("修改函数", "passed", "修改成功")
        
        # 测试删除函数
        deleted = delete_event(event_id)
        record_test("删除函数", "passed", "删除成功")
        
    except Exception as e:
        record_test("便捷函数", "failed", f"函数测试失败: {e}")
        all_files_ok = False
else:
    record_test("便捷函数", "skipped", "前置测试失败，跳过")

# 测试5: 错误处理
print("\n5. 错误处理测试...")
if all_files_ok:
    try:
        from feishu_calendar import FeishuCalendarError
        record_test("错误类导入", "passed", "FeishuCalendarError可导入")
    except Exception as e:
        record_test("错误类导入", "failed", f"错误类导入失败: {e}")
else:
    record_test("错误处理", "skipped", "前置测试失败，跳过")

# 生成测试报告
print("\n" + "=" * 60)
print("测试报告")
print("=" * 60)

# 统计结果
passed = sum(1 for r in test_results if r["status"] == "passed")
failed = sum(1 for r in test_results if r["status"] == "failed")
skipped = sum(1 for r in test_results if r["status"] == "skipped")
total = len(test_results)

print(f"总检查项: {total}")
print(f"通过: {passed}")
print(f"失败: {failed}")
print(f"跳过: {skipped}")

print("\n详细结果:")
for result in test_results:
    status_icon = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "⏭️"
    print(f"  {status_icon} {result['name']:30} {result.get('details', '')}")

print("\n" + "=" * 60)
if failed == 0 and all_files_ok:
    print("🎉 冒烟测试通过！Skill基本功能正常。")
    
    # 保存测试报告
    report = {
        "skill_name": "feishu-calendar-v2",
        "test_type": "smoke_test",
        "test_date": datetime.now().isoformat(),
        "results": test_results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "all_ok": all_files_ok
        }
    }
    
    report_dir = os.path.join(os.path.dirname(__file__), "test-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"报告保存: {report_file}")
    
else:
    print("⚠️ 冒烟测试发现问题，请检查失败项。")
    sys.exit(1)