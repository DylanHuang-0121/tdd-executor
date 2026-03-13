#!/usr/bin/env python3
"""
TDD Toolkit - Main Entry Point
直接运行：python -m tdd_toolkit [command]
"""
import sys
from pathlib import Path

# 确保能从父目录导入
sys.path.insert(0, str(Path(__file__).parent))

def main():
    from tdd_pipeline import TDDPipeline, PipelineStatus
    from issue_tracker import IssueTracker
    import argparse
    
    parser = argparse.ArgumentParser(description="TDD Toolkit - 强约束 TDD 流水线")
    parser.add_argument("command", choices=["pipeline", "record", "list", "init", "progress"],
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
        print("✅ TDD Toolkit 已初始化")
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
            print("  python -m tdd_toolkit record --feature 'webhook-approval' --error-type 'AssertionError' --message '审批逻辑失败' --pipeline-node 'run_tests'")
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
            print("  python -m tdd_toolkit progress --project webhook-approval --target run_tests")
            sys.exit(1)
        
        pipeline = TDDPipeline(args.project)
        pipeline.progress_to(args.target)


if __name__ == "__main__":
    main()


# 也支持直接运行单模块命令
command_line = sys.argv[1:] if len(sys.argv) > 1 else []
if command_line and command_line[0] == "pipeline":
    # 处理 pipeline 命令
    if len(command_line) < 2:
        print("❌ 需要提供项目名称和目标节点")
    else:
        project = command_line[1]
        target = command_line[2] if len(command_line) > 2 else None
        pipeline = TDDPipeline(project)
        if target:
            pipeline.progress_to(target)
        else:
            print(f"📊 Pipeline 状态：{pipeline.pipeline_status.value}")