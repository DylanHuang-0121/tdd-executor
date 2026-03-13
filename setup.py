#!/usr/bin/env python3
"""
TDD Toolkit Setup
"""
import os
from pathlib import Path

def setup():
    """初始化工具"""
    directories = [
        "pit-library",
        "tdd-sessions"
    ]
    
    for dir_name in directories:
        path = Path.cwd() / dir_name
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录：{path}")
    
    print("\n🚀 TDD Toolkit 初始化完成！")
    print("\n下一步:")
    print("  1. 创建你的测试：python -m pytest --collect-only")
    print("  2. 运行测试：python -m pytest tests/")
    print("  3. 记录问题：python issue-tracker.py manual")


if __name__ == "__main__":
    setup()