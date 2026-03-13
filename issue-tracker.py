#!/usr/bin/env python3
"""
Issue Tracker - 问题记录器
自动记录测试失败的问题，支持手动记录
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from utils import (
    ensure_directories,
    get_current_version,
    format_issue_id,
    timestamp,
    PIT_LIBRARY
)


class IssueTracker:
    """问题追踪器"""
    
    def __init__(self):
        ensure_directories()
        self.issues_file = PIT_LIBRARY / "all-issues.json"
        self.issues = self._load_issues()
    
    def _load_issues(self) -> list:
        """加载所有问题"""
        if not self.issues_file.exists():
            return []
        with open(self.issues_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_issues(self):
        """保存问题列表"""
        with open(self.issues_file, "w", encoding="utf-8") as f:
            json.dump(self.issues, f, indent=2, ensure_ascii=False)
    
    def record(self, details: Dict[str, Any], version: int = None) -> str:
        """
        记录一个新问题
        返回：issue_id
        """
        version = version or get_current_version()
        issue_id = format_issue_id(version)
        
        # 补全默认值
        issue = {
            "id": issue_id,
            "timestamp": timestamp(),
            "feature": details.get("feature", "unknown"),
            "error_type": details.get("error_type", "UnknownError"),
            "message": details.get("message", "未知错误"),
            "stack_trace": details.get("stack_trace", ""),
            "root_cause": details.get("root_cause", ""),
            "fix": details.get("fix", ""),
            "solution": details.get("solution", ""),
            "related_test": details.get("related_test", ""),
            "severity": details.get("severity", "medium"),
            "status": "open",  # open, fixed, archived
            "frequency": 1
        }
        
        # 写入单个文件
        issue_file = PIT_LIBRARY / f"{issue_id}-{sanitize_filename(details.get('error_type', 'error'))}.json"
        with open(issue_file, "w", encoding="utf-8") as f:
            json.dump(issue, f, indent=2, ensure_ascii=False)
        
        # 添加到总列表
        self.issues.append(issue)
        self._save_issues()
        
        # 输出结果
        print(f"\n✅ 问题已记录!")
        print(f"   ID: {issue_id}")
        print(f"   文件：{issue_file}")
        print(f"   类型：{issue['error_type']}")
        print(f"   严重性：{issue['severity']}")
        
        return issue_id
    
    def get_similar_issues(self, feature: str, top_k: int = 3) -> list:
        """查找相似的历史问题"""
        similar = []
        for issue in self.issues:
            if issue["status"] != "open":
                continue
            
            # 简单匹配：feature 包含或字段重叠
            if feature.lower() in issue.get("feature", "").lower():
                similar.append(issue)
            elif issue.get("error_type", "") == issue.get("error_type", ""):
                similar.append(issue)
        
        return similar[:top_k]
    
    def show_issues(self, feature: str = None):
        """列出问题"""
        issues = [i for i in self.issues if feature is None or feature in i.get("feature", "")]
        
        print(f"\n📋 问题列表 (共 {len(issues)} 个)\n")
        for issue in issues[-5:]:  # 只显示最近的 5 个
            print(f"## {issue['id']}: {issue['error_type']}")
            print(f"   功能：{issue['feature']}")
            print(f"   严重性：{issue['severity']}")
            print(f"   状态：{issue['status']}")
            print()
    
    def create_manual_record(self):
        """手动创建问题记录（交互式）"""
        print("📝 手动记录问题")
        print("=" * 50)
        
        details = {
            "feature": input("功能名称：").strip() or "unknown",
            "error_type": input("错误类型：").strip() or "ManualIssue",
            "message": input("错误信息：").strip() or "手动添加",
            "root_cause": input("根本原因（可选）：").strip() or "",
            "solution": input("解决方案（可选）：").strip() or "",
            "severity": input("严重性 (high/medium/low, 默认 medium): ").strip() or "medium"
        }
        
        return details


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(description="Issue Tracker - 问题记录器")
    parser.add_argument("command", choices=["record", "list", "search", "manual"], nargs="?",
                        help="操作命令")
    parser.add_argument("--feature", "-f", help="功能名称")
    parser.add_argument("--error-type", "-t", help="错误类型")
    parser.add_argument("--message", "-m", help="错误信息")
    parser.add_argument("--root-cause", "-c", help="根本原因")
    parser.add_argument("--solution", "-s", help="解决方案")
    parser.add_argument("--severity", help="严重性 (high/medium/low)")
    
    args = parser.parse_args()
    
    tracker = IssueTracker()
    
    if args.command == "record":
        # 自动记录模式
        details = {
            "feature": args.feature or "auto",
            "error_type": args.error_type or "AutoIssue",
            "message": args.message or "自动记录",
            "root_cause": args.root_cause or "",
            "solution": args.solution or "",
            "severity": args.severity or "medium"
        }
        tracker.record(details)
    
    elif args.command == "list":
        tracker.show_issues(args.feature)
    
    elif args.command == "search":
        if not args.feature:
            print("❌ 需要提供 --feature 参数")
            sys.exit(1)
        
        similar = tracker.get_similar_issues(args.feature)
        if similar:
            print(f"📊 找到 {len(similar)} 个相似问题:\n")
            for issue in similar:
                print(f"## {issue['id']}: {issue['error_type']}")
                print(f"   问题: {issue['message'][:50]}...")
                print(f"   方案：{issue['solution'][:50]}...\n")
        else:
            print("✅ 没有找到相似问题")
    
    elif args.command == "manual" or not args.command:
        # 交互式记录
        details = tracker.create_manual_record()
        tracker.record(details)


if __name__ == "__main__":
    main()