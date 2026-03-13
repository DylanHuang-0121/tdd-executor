#!/usr/bin/env python3
"""
Simple TDD 例子：演示任务列表格式

这个例子展示如何生成任务列表并执行
"""
from pathlib import Path
from tdd_pipeline import TDDPipeline


# 示例 1: 基本循环结构
def example_basic_tdd():
    """
    基本 TDD 循环
    
    write_test → run_test(failure) → write_code → run_test(success)
    """
    task_list = [
        {"action": "write_test", "output": "example_test.java"},
        {"action": "run_test", "expected": "failure"},  # 预期失败
        {"action": "write_code", "output": "example.java"},
        {"action": "run_test", "expected": "success", "pass_gate": True},  # 验收标准
    ]
    
    pipeline = TDDPipeline("example-basic", task_list)
    
    # 任务 1: 生成测试
    pipeline.execute_next_task()
    
    # 任务 2: 运行测试（失败）
    pipeline.execute_next_task()
    
    # 任务 3: 编写代码
    pipeline.execute_next_task()
    
    # 任务 4: 运行测试（成功，pass_gate）
    pipeline.execute_next_task()


# 示例 2: 调试循环结构
def example_debug_loop():
    """
    调试循环
    
    write_test → run_test(failure) → write_code → run_test(failure) → fix → run_test(success)
    """
    task_list = [
        {"action": "write_test", "output": "example_test.java"},
        {"action": "run_test", "expected": "failure"},
        {"action": "write_code", "output": "example.java"},
        {"action": "run_test", "expected": "failure"},  # 这次还是失败
        {"action": "fix_implementation"},  # 修复问题
        {"action": "run_test", "expected": "success", "pass_gate": True},
    ]
    
    pipeline = TDDPipeline("example-debug", task_list)
    
    # 逐步执行
    for i in range(len(task_list)):
        print(f"\n=== 执行任务 {i+1} ===")
        success = pipeline.execute_next_task()
        if success and i == len(task_list) - 1:
            print("✅ 所有任务完成！")


# 示例 3: 复杂功能点
def example_complex_feature():
    """
    复杂功能点的任务列表
    
    需求理解（OpenClaw）→ 分发到这里
    """
    task_list = [
        {"action": "read_requirements"},
        {"action": "write_test", "output": "complex_feature_test.java"},
        {"action": "run_test", "expected": "failure"},
        {"action": "write_code", "output": "complex_feature.java"},
        {"action": "run_test", "expected": "failure"},  # 只有部分通过
        {"action": "fix_implementation"},
        {"action": "run_test", "expected": "success", "pass_gate": True},  # 全部通过
        {"action": "refactor"},  # 可选的优化
        {"action": "run_test", "expected": "success", "pass_gate": True},
    ]
    
    pipeline = TDDPipeline("example-complex", task_list)
    
    # 执行所有任务
    while pipeline.execute_next_task():
        pass


# 示例 4: 从 OpenClaw 接收任务列表
def example_from_openclaw():
    """
    OpenClaw 会生成一个任务列表，这个工具负责执行
    
    OpenClaw 输出：
    {
        "project": "some-feature",
        "task_list": [
            {"action": "write_test", ...},
            {"action": "run_test", ...},
            ...
        ]
    }
    """
    # OpenClaw 分发的任务列表
    task_list_from_openclaw = [
        {"action": "write_test", "output": "feature_test.java"},
        {"action": "run_test", "expected": "failure"},
        {"action": "write_code", "output": "feature.java"},
        {"action": "run_test", "expected": "success", "pass_gate": True},
    ]
    
    # 这个工具运行任务
    pipeline = TDDPipeline("some-feature", task_list_from_openclaw)
    
    while pipeline.execute_next_task():
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("Simple TDD 例子展示")
    print("=" * 60)
    
    print("\n示例 1: 基本 TDD 循环")
    # example_basic_tdd()
    
    print("\n示例 2: 调试循环")
    # example_debug_loop()
    
    print("\n示例 3: 复杂功能点")
    # example_complex_feature()
    
    print("\n示例 4: 从 OpenClaw 接收任务列表")
    # example_from_openclaw()
    
    print("\n" + "=" * 60)
    print("提示：取消注释上面要演示的例子")
    print("=" * 60)