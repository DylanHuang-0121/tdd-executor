"""
TDD Pipeline 工具函数和异常追踪器
"""
from pathlib import Path
from datetime import datetime
import os
import json
from typing import List, Optional

# 项目基础路径（根据运行环境自动调整）
WORKSPACE_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PIT_LIBRARY = WORKSPACE_ROOT / "pit-library"
TDD_SESSIONS = WORKSPACE_ROOT / "tdd-sessions"


def ensure_directories():
    """确保所有必要的目录存在"""
    PIT_LIBRARY.mkdir(parents=True, exist_ok=True)
    TDD_SESSIONS.mkdir(parents=True, exist_ok=True)


def get_current_version() -> int:
    """获取当前库中的版本号"""
    ensure_directories()
    files = list(PIT_LIBRARY.glob("v*.json"))
    return len(files) + 1 if files else 0


def format_issue_id(version: int) -> str:
    """格式化问题 ID，例如 v001"""
    return f"v{version:03d}"


def get_today_path() -> str:
    """获取今天的日期路径"""
    return datetime.now().strftime("%Y-%m-%d")


def timestamp() -> str:
    """获取当前 ISO 时间戳"""
    return datetime.now().isoformat()


def sanitize_filename(text: str) -> str:
    """清理文件名中的非法字符"""
    return "".join(c for c in text if c.isalnum() or c in " _-").strip()[:50]


class IssueTracker:
    """问题追踪器 - 用于记录测试失败的问题"""
    
    def __init__(self):
        ensure_directories()
        self.issues_file = PIT_LIBRARY / "all-issues.json"
        self.issues = self._load_issues()
    
    def _load_issues(self) -> list:
        """加载所有问题"""
        if not self.issues_file.exists():
            return []
        with open(self.issues_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    def _save_issues(self):
        """保存问题列表"""
        with open(self.issues_file, "w", encoding="utf-8") as f:
            json.dump(self.issues, f, indent=2, ensure_ascii=False)
    
    def record(self, details: dict, version: int = None) -> str:
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
            "frequency": 1,
            "pipeline_node": details.get("pipeline_node", "")
        }
        
        # 写入单个文件
        issue_file = PIT_LIBRARY / f"{issue_id}-{sanitize_filename(details.get('error_type', 'error'))}.json"
        with open(issue_file, "w", encoding="utf-8") as f:
            json.dump(issue, f, indent=2, ensure_ascii=False)
        
        # 添加到总列表
        self.issues.append(issue)
        self._save_issues()
        
        print(f"\n✅ 问题已记录!")
        print(f"   ID: {issue_id}")
        print(f"   文件：{issue_file}")
        print(f"   类型：{issue['error_type']}")
        print(f"   严重性：{issue['severity']}")
        print(f"   节点：{details.get('pipeline_node', 'auto')}")
        
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
    
    def search_by_error(self, error_type: str) -> list:
        """按错误类型搜索问题"""
        return [i for i in self.issues if i.get("error_type") == error_type]
    
    def fix_issue(self, issue_id: str):
        """标记问题已修复"""
        for issue in self.issues:
            if issue["id"] == issue_id:
                issue["status"] = "fixed"
                issue["fixed_at"] = timestamp()
                self._save_issues()
                return True
        
        return False
    
    def get_unfinished_in_node(self, pipeline_node: str) -> list:
        """获取某个节点的未解决问题"""
        return [i for i in self.issues if 
                i.get("pipeline_node") == pipeline_node.lower() and 
                i.get("status") == "open"]