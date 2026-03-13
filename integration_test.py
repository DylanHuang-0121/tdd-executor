#!/usr/bin/env python3
"""
集成测试：展示 OpenClaw 和问题记录工作流
"""
import sys
import json
from pathlib import Path

# 添加到路径
sys.path.insert(0, str(Path(__file__).parent))

from tdd_pipeline import TDDPipeline


def example_openclaw_workflow():
    """
    模拟 OpenClaw 工作流：
    1. OpenClaw 生成任务列表和问题
    2. 本工具执行任务
    3. 记录问题到知识库
    """
    print("=" * 60)
    print("🚀 OpenClaw 集成测试")
    print("=" * 60)
    
    # 1. OpenClaw 生成的任务列表
    task_list = [
        {"action": "read_requirements"},
        {"action": "write_test", "output": "feature_test.java"},
        {"action": "run_test", "expected": "failure"},
        {"action": "write_code", "output": "feature.java"},
        {"action": "run_test", "expected": "success", "pass_gate": True},
        {"action": "fix_implementation"},
        {"action": "run_test", "expected": "success", "pass_gate": True},
        {"action": "refactor"},
    ]
    
    # 2. OpenClaw 记录的问题（用于知识库保鲜）
    issues = [
        {
            "title": "边界条件验证缺失",
            "stage": "unit_test",
            "description": "当卡号为 null 时应该抛出 IllegalArgumentException",
            "solution": "添加空值检查逻辑：if (cardNo == null) throw new IllegalArgumentException(...)",
            "code_snippet": "if (cardNo == null) throw new IllegalArgumentException(\"Card number cannot be null\");",
            "test_case": "testAddCard_NullCardNo"
        },
        {
            "title": "Webhook 签名验证失败",
            "stage": "debug",
            "description": "签名验证时只支持 RSA-SHA256，不支持 RSA-PSS",
            "solution": "增加 RSA-PSS 支持，添加密钥类型检查",
            "code_snippet": "if (hasAttr(key, 'pss_key')) { use_pss_validation(); }",
            "test_case": "testWebhookSignature_RSAPSS"
        }
    ]
    
    print("\n📋 任务列表:")
    for i, task in enumerate(task_list, 1):
        print(f"  {i}. {task['action']}")
    
    print(f"\n📝 记录问题：{len(issues)} 个")
    for issue in issues:
        print(f"  - {issue['title']}")
    
    # 3. 创建执行器
    print("\n🔧 创建执行器...")
    pipeline = TDDPipeline("integration-test", task_list)
    
    # 4. 记录问题
    print("\n💾 记录问题...")
    for issue in issues:
        pipeline.add_issue(issue)
    
    # 5. 执行任务
    print("\n⚡ 执行任务...")
    tasks_executed = 0
    while pipeline.execute_next_task():
        tasks_executed += 1
        if tasks_executed == 3:  # 演示用，执行前 3 个任务就停止
            print("\n🛑 执行暂停（演示用）")
            break
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("✅ 集成测试完成！")
    print("=" * 60)
    print("\n📁 生成的文件:")
    print("  - tdd-sessions/integration-test-state.json (断点)")
    print("  - tdd-sessions/integration-test-issues.md (问题日志)")
    
    print("\n📊 状态:")
    print(f"  - 已执行任务：{tasks_executed}")
    print(f"  - 总任务数：{len(task_list)}")
    print(f"  - 记录问题：{len(issues)}")
    
    print("\n🔄 下一次执行会自动续写...")
    
    return pipeline


if __name__ == "__main__":
    example_openclaw_workflow()