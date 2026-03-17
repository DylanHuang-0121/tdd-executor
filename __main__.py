#!/usr/bin/env python3
"""
TDD Executor - Main Entry Point
直接运行：python __main__.py [command]
"""
import sys
from pathlib import Path

# 确保能从当前目录导入
sys.path.insert(0, str(Path(__file__).parent))

def main():
    from tdd_pipeline import TDDPipeline, PipelineStatus
    from issue_tracker import IssueTracker
    import argparse
    
    parser = argparse.ArgumentParser(description="TDD Executor - 强约束 TDD 流水线")
    parser.add_argument("command", choices=["pipeline", "record", "list", "init", "progress", "complete"],
                        help="操作命令")
    parser.add_argument("--project", "-p", help="项目名称")
    parser.add_argument("--target", "-t", help="目标节点", default=None)
    parser.add_argument("--feature", "-f", help="功能名称", default=None)
    parser.add_argument("--error-type", "-e", help="错误类型", default=None)
    parser.add_argument("--message", "-m", help="错误信息", default=None)
    parser.add_argument("--pipeline-node", help="Pipeline 节点", default=None)
    
    args = parser.parse_args()
    
    if args.command == "init":
        # 初始化 pit-library 和 tdd-sessions
        from utils import ensure_directories
        ensure_directories()
        print("✅ TDD Executor 已初始化")
        print(f"   pit-library: {Path.cwd() / 'pit-library'}")
        print(f"   tdd-sessions: {Path.cwd() / 'tdd-sessions'}")
    
    elif args.command == "pipeline":
        if not args.project:
            print("❌ 需要提供 --project 参数")
            sys.exit(1)
        
        pipeline = TDDPipeline(args.project)
        
        if args.target:
            pipeline.progress_to(args.target)
        else:
            print(f"📊 项目：{args.project}")
            print(f"   状态：{pipeline.pipeline_status.value}")
            print("\n可用节点:")
            for status in PipelineStatus:
                if status.value not in ["completed", "not_started", "failed"]:
                    print(f"   - {status.value.replace('_', ' ').title()}")
    
    elif args.command == "record":
        target_node = args.pipeline_node or "auto"
        tracker = IssueTracker()
        
        if not all([args.feature, args.error_type, args.message]):
            print("❌ 需要 --feature, --error-type, --message")
            print("\n用法示例:")
            print("  tdd-executor record --feature 'webhook-approval' --error-type 'AssertionError' --message '审批逻辑失败' --pipeline-node 'run_tests'")
            sys.exit(1)
        
        tracker.record({
            "feature": args.feature,
            "error_type": args.error_type,
            "message": args.message,
            "pipeline_node": target_node,
            "severity": "high"
        })
    
    elif args.command == "list":
        tracker = IssueTracker()
        tracker.show_issues(args.feature)
    
    elif args.command == "progress":
        if not args.project or not args.target:
            print("❌ 需要提供 --project 和 --target")
            print("\n用法示例:")
            print("  tdd-executor progress --project webhook-approval --target run_tests")
            sys.exit(1)
        
        pipeline = TDDPipeline(args.project)
        pipeline.progress_to(args.target)
    
    elif args.command == "complete":
        if not args.project:
            print("❌ 需要提供 --project 参数")
            print("\n用法示例:")
            print("  tdd-executor complete --project webhook-approval")
            sys.exit(1)
        
        pipeline = TDDPipeline(args.project)
        pipeline.complete_current_node(args.message or "")

if __name__ == "__main__":
    main()