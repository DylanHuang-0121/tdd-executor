#!/usr/bin/env python3
"""
TDD Runner - 测试驱动开发执行器
专为 Claude Code 设计，自动处理 TDD 循环和问题记录
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from utils import (
    ensure_directories,
    get_current_version,
    format_issue_id,
    timestamp,
    sanitize_filename,
    PIT_LIBRARY,
    TDD_SESSIONS
)


class TDDRManager:
    """TDD 运行时管理器"""
    
    def __init__(self, feature: str, test_dir: Path = None):
        ensure_directories()
        self.feature = feature
        self.test_dir = test_dir or (Path.cwd() / "tests")
        self.session_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_filename(feature)}"
        self.session_file = TDD_SESSIONS / f"{self.session_id}.md"
        
        # 初始化会话文件
        self._init_session()
    
    def _init_session(self):
        """初始化 TDD 会话记录"""
        self.session_file.write_text(f"""# TDD Session: {self.feature}

**时间**: {timestamp()}  
**会话 ID**: {self.session_id}  
**状态**: 进行中

## 功能需求
(待填写)

## 测试结果

## 记录的问题
- (自动记录)

---

*由 TDD Runner 自动生成*
""")
    
    def log(self, message: str, level: str = "info"):
        """记录到会话文件"""
        timestamp_str = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp_str}] [{level.upper()}] {message}\n"
        
        with open(self.session_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        print(f"[{level.upper()}] {message}")
    
    def run_tests(self, test_file: str) -> dict:
        """
        运行测试文件，返回结构化结果
        """
        self.log(f"运行测试：{test_file}")
        
        try:
            result = subprocess.run(
                ["pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            self.log("测试超时！已超过 60 秒", "error")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            self.log(f"测试运行失败：{str(e)}", "error")
            return {"success": False, "error": str(e)}
    
    def record_issue(self, error_details: dict):
        """记录测试失败的问题"""
        version = get_current_version()
        issue_id = format_issue_id(version)
        
        issue = {
            "id": issue_id,
            "timestamp": timestamp(),
            "session_id": self.session_id,
            "feature": self.feature,
            "error_type": error_details.get("error_type", "UnknownError"),
            "message": error_details.get("message", "未知错误"),
            "stack_trace": error_details.get("stack_trace", ""),
            "root_cause": "",  # 待 Classify
            "fix": "",  # 待解决
            "solution": "",  # 解决方案
            "related_test": error_details.get("test_file", ""),
            "severity": "high" if "timeout" in error_details.get("error", "").lower() else "medium"
        }
        
        issue_file = PIT_LIBRARY / f"{issue_id}-{error_details.get('error_type', 'error')}.json"
        with open(issue_file, "w", encoding="utf-8") as f:
            json.dump(issue, f, indent=2, ensure_ascii=False)
        
        # 记录到会话
        with open(self.session_file, "a", encoding="utf-8") as f:
            f.write(f"\n### 问题 #{issue_id}: {issue['error_type']}\n")
            f.write(f"- 错误信息：{issue['message']}\n")
            f.write(f"- 已保存到：{issue_file}\n\n")
        
        self.log(f"问题已记录：{issue_id} - {issue['error_type']}", "warning")
        print(f"\n📝 问题已保存到：{issue_file}\n")
        
        return issue_id


def find_test_files(test_dir: Path) -> list:
    """查找测试文件"""
    test_files = list(test_dir.glob("test_*.py"))
    if not test_files:
        print(f"⚠️ 未找到测试文件，请在 {test_dir} 创建 test_*.py 文件")
    return test_files


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("usage: python tdd-runner.py <feature> [--test-dir <path>]")
        print("  or: python tdd-runner.py --init  (初始化 pit-library)")
        sys.exit(1)
    
    if sys.argv[1] == "--init":
        print("✅ TDD Toolkit 初始化完成")
        print(f"   pit-library 路径：{PIT_LIBRARY}")
        print(f"   tdd-sessions 路径：{TDD_SESSIONS}")
        return
    
    feature_name = sys.argv[1]
    test_dir = None
    
    # 解析 --test-dir
    if "--test-dir" in sys.argv:
        idx = sys.argv.index("--test-dir")
        if idx + 1 < len(sys.argv):
            test_dir = Path(sys.argv[idx + 1])
    
    # 创建 TDD 管理器
    manager = TDDRManager(feature_name, test_dir)
    
    # 查找测试文件
    test_files = find_test_files(test_dir or Path.cwd() / "tests")
    
    if not test_files:
        print("\n📌 提示：没有测试文件，现在开始 TDD 吗？")
        print("   建议：创建一个简单的测试文件，例如 test_feature.py")
        print(f"   下面是一个示例测试模板:")
        print("""
```python
import pytest
from source_module import your_function

def test_basic():
    assert your_function(input) == expected
```
        """)
        return
    
    # 运行第一个测试文件
    manager.log(f"开始测试：{test_files[0]}")
    result = manager.run_test(str(test_files[0]))
    
    if result["success"]:
        manager.log("✅ 测试通过！")
    else:
        manager.log("❌ 测试失败，准备记录问题")
        manager.record_issue({
            "error_type": result.get("error", "TestFailed"),
            "message": result.get("stderr", "No output"),
            "test_file": str(test_files[0])
        })


if __name__ == "__main__":
    # 支持直接运行
    from utils import ensure_directories
    ensure_directories()
    main()