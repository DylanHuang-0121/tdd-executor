#!/usr/bin/env python3
"""
演示自动执行 + 断点续写
"""
import sys
from pathlib import Path

# 添加 tdd-toolkit 到路径
sys.path.insert(0, str(Path(__file__).parent))

from tdd_pipeline import TDDPipeline, TDDAutoExecutor
from utils import TDD_SESSIONS, ensure_directories


def demo_new_pipeline():
    """演示新的自动执行 + 断点续写"""
    print("=" * 60)
    print("🚀 TDD Pipeline - 自动执行 + 断点续写演示")
    print("=" * 60)
    
    # 1. 第一次执行：初始化
    print("\n💡 第一次执行：初始化 Pipeline")
    pipeline = TDDPipeline("demo-project", resume_if_exists=False)
    pipeline.execute_next_node()
    
    # 2. 模拟：手动记录任务完成
    print("\n📝 任务文档已创建:")
    task_docs = list(TDD_SESSIONS.glob("demo-project-tasks.md"))
    if task_docs:
        print(f"   - {task_docs[0]}")
    
    # 3. 保存断点
    print("\n💾 保存断点")
    pipeline.save_checkpoint("After Planning Phase")
    
    # 4. 退出
    
    # 5. 第二次执行：断点续写
    print("\n" + "=" * 60)
    print("🔄 第二次执行：断点续写")
    print("=" * 60)
    
    pipeline2 = TDDPipeline("demo-project", resume_if_exists=True)
    print(f"   当前节点：{pipeline2.pipeline[pipeline2.current_index].name}")
    print(f"   断点计数：{pipeline2.checkpoint_count}")
    
    # 6. 继续执行
    pipeline2.execute_next_node()


def demo_auto_executor():
    """演示自动执行器"""
    print("\n" + "=" * 60)
    print("🤖 自动执行器演示")
    print("=" * 60)
    
    executor = TDDAutoExecutor("demo-auto", resume_if_exists=False)
    executor.run(prompt="执行到断点后暂停")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        demo_auto_executor()
    else:
        demo_new_pipeline()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("\n💡 你会看到:")
    print("  1. 第一次执行创建 Pipeline")
    print("  2. 保存断点")
    print("  3. 第二次执行继续（断点续写）")
    print("  4. 代码化的强约束（不能跳过节点）")