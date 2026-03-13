#!/usr/bin/env python3
"""
TDD Pipeline - 强约束的 TDD 流水线
确保每一步都按顺序执行，无法跳过
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

from utils import (
    ensure_directories,
    timestamp,
    PIT_LIBRARY,
    TDD_SESSIONS,
    WORKSPACE_ROOT
)


class PipelineStatus(Enum):
    """流水线状态"""
    NOT_STARTED = "not_started"
    PLANNING = "planning"      # 任务规划
    UNIT_TEST = "unit_test"    # 编写测试用例
    CODE_IMPLEMENTATION = "code_implementation"  # 实现代码
    COMPILE = "compile"         # 编译/检查
    RUN_TESTS = "run_tests"     # 运行测试
    DEBUGGING = "debugging"     # 回溯调试
    TEST_PASSED = "test_passed" # 测试通过
    FAILED = "failed"          # 最终失败【不能继续】


@dataclass
class PipelineNode:
    """流水线节点"""
    id: str
    name: str
    status: PipelineStatus
    executed_at: Optional[str] = None
    result: Optional[str] = None
    issues: List[Dict] = None
    next_allowed: bool = True  # 是否允许进入下一步
    
    def to_dict(self):
        d = asdict(self)
        d['status'] = self.status.value
        return d


class TDDPipeline:
    """强约束 TDD 流水线管理器"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.pipeline_file = TDD_SESSIONS / f"{project_name}-pipeline.json"
        self.task_list_file = TDD_SESSIONS / f"{project_name}-tasks.md"
        self.pipeline_status = self._load_or_init()
        self.current_node = self._find_current_node()
        
    def _load_or_init(self) -> PipelineStatus:
        """加载或初始化流水线状态"""
        if self.pipeline_file.exists():
            with open(self.pipeline_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return PipelineStatus(data['status'])
        
        # 初始化新的流水线
        self._init_new_pipeline()
        return PipelineStatus.PRE_START
    
    def _find_current_node(self) -> PipelineStatus:
        """找到当前应该执行的节点"""
        for node in PipelineStatus:
            if self.pipeline_status.value == node.value:
                return node
        return PipelineStatus.NOT_STARTED
    
    def _init_new_pipeline(self):
        """初始化新的流水线"""
        self.pipeline = [
            PipelineNode("planning", "任务规划", PipelineStatus.NOT_STARTED),
            PipelineNode("unit_test", "编写单元测试", PipelineStatus.NOT_STARTED),
            PipelineNode("code_impl", "实现代码", PipelineStatus.NOT_STARTED),
            PipelineNode("compile", "编译/检查", PipelineStatus.NOT_STARTED),
            PipelineNode("run_tests", "运行测试", PipelineStatus.NOT_STARTED),
            PipelineNode("debug", "回溯调试", PipelineStatus.NOT_STARTED),
            PipelineNode("done", "完成", PipelineStatus.NOT_STARTED),
        ]
        
        # 设置初始状态
        self.pipeline[0].status = PipelineStatus.PRE_START
        self._save_pipeline_state()
        self._create_task_list_template()
    
    def _create_task_list_template(self):
        """创建任务列表模板"""
        task_list = f"""# TDD Pipeline 任务列表 - {self.project_name}

**创建时间**: {timestamp()}  
**当前状态**: {self.pipeline_status.value}

---

## 🔵 任务 1: 规划开发任务 (必须完成)
- [ ] 明确需求
- [ ] 识别功能点
- [ ] 画出核心流程图
- [ ] 确定边界条件
- [ ] 记录到：`tasks/01-planning.md`

## 🟢 任务 2: 写单元测试 (必须完成)
- [ ] 确定测试文件位置 (tests/xxx_test.py)
- [ ] 编写测试用例
- [ ] 覆盖正常路径
- [ ] 覆盖异常路径
- [ ] 边界条件测试
- [ ] 首次运行测试（可能失败）
- [ ] 记录到：`tasks/02-unit-test.md`

## 🟡 任务 3: 实现代码 (必须完成)
- [ ] 读取测试用例
- [ ] 编写实现代码
- [ ] 确保通过测试
- [ ] 代码审查（self-review）
- [ ] 记录到：`tasks/03-code-impl.md`

## 🟣 任务 4: 编译/检查 (必须完成)
- [ ] py.test 检查语法
- [ ] mypy 类型检查（如有）
- [ ] flake8/black 风格检查
- [ ] 确保无警告
- [ ] 记录到：`tasks/04-compile.md`

## 🔴 任务 5: 运行测试 (必须完成)
- [ ] pytest -v tests/
- [ ] 所有测试通过
- [ ] 覆盖率 > 80%
- [ ] 记录到：`tasks/05-run-tests.md`

## 🟠 任务 6: 调试回溯 (如失败)
- [ ] 分析错误日志
- [ ] 检查测试用例是否正确
- [ ] 检查实现代码是否有 bug
- [ ] 记录错误到 pit-library
- [ ] 修复后重新测试
- [ ] 环形迭代直到通过
- [ ] 记录到：`tasks/06-debug.md`

## ✅ 任务 7: 完成
- [ ] 所有测试通过
- [ ] 代码审查通过
- [ ] 提交 commit
- [ ] 更新 MEMORY.md
- [ ] 标记流水线为完成
"""
        self.task_list_file.write_text(task_list)
    
    def _save_pipeline_state(self):
        """保存流水线状态"""
        state = {
            'project': self.project_name,
            'created_at': timestamp(),
            'status': self.pipeline_status.value,
            'nodes': [node.to_dict() for node in self.pipeline]
        }
        
        with open(self.pipeline_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def progress_to(self, target: str):
        """推进到指定节点"""
        target_status = PipelineStatus(target)
        
        # 检查是否允许推进（前一个节点必须完成）
        if not self._check_progression_allowed(target_status):
            print(f"❌ 不能推进到 {target_status.value} - 前一个节点未完成")
            print("请先完成上一个任务节点")
            return False
        
        # 更新当前节点状态
        for node in self.pipeline:
            if node.id == target.lower().replace(" ", "_"):
                node.status = PipelineStatus.COMPLETED
                node.executed_at = timestamp()
        
        # 更新流水线状态
        self.pipeline_status = target_status
        
        # 自动创建对应的任务文档
        task_doc = self._create_task_doc(target)
        
        # 保存
        self._save_pipeline_state()
        self._update_task_list()
        
        print(f"✅ 已推进到：{target_status.value}")
        print(f"📝 任务文档：{task_doc}")
        
        return True
    
    def _check_progression_allowed(self, target: PipelineStatus) -> bool:
        """检查是否可以推进到目标节点"""
        if target == PipelineStatus.PRE_START:
            return True
        
        # 找到目标节点的前一个节点
        prev_index = list(PipelineStatus).index(target) - 1
        if prev_index < 0:
            return True
        
        prev_status = list(PipelineStatus)[prev_index]
        current = self._find_current_node()
        
        # 检查前一个节点是否完成
        if current == prev_status or current == PipelineStatus.COMPLETED:
            return True
        
        return False
    
    def _create_task_doc(self, target: str) -> str:
        """创建对应的任务文档"""
        doc_name = target.replace(" ", "-").lower()
        doc_file = TDD_SESSIONS / f"tasks" / f"{doc_name}.md"
        
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        
        doc_content = f"""# TDD 任务文档：{target}

**执行时间**: {timestamp()}  
**进度**: {self.pipeline_status.value}

## 任务要求
{self._get_task_requirements(target)}

## 执行记录
```
TODO: 记录执行过程和结果
```

## 问题记录
```
TODO: 记录遇到的问题
```

## 验收标准
{self._get_task_acceptance(target)}
"""
        
        doc_file.write_text(doc_content)
        return str(doc_file)
    
    def _get_task_requirements(self, target: str) -> str:
        """获取任务要求"""
        requirements = {
            "planning": """
- 明确要开发的单一功能点
- 确定输入输出接口
- 画出业务流程图
- 识别边界条件和异常场景
""",
            
            "unit_test": """
- 创建测试文件 (tests/)
- 编写测试用例（至少 3 个）
- 覆盖正常路径
- 覆盖异常路径
- 边界条件测试
""",
            
            "code_impl": """
- 读取测试用例
- 实现对应代码
- 确保能单元测试通过
- 代码简洁、可读
""",
            
            "compile": """
- pytest --collect-only 检查语法
- mypy 类型检查（如有）
- flake8/black 风格检查
- 解决所有警告
""",
            
            "run_tests": """
- pytest -v tests/
- 所有测试必须通过
- 覆盖率 > 80%
- 记录测试结果
""",
            
            "debug": """
- 分析错误原因
- 检查测试用例是否有问题
- 检查实现代码是否有 bug
- 记录问题到 pit-library
- 修复后重新测试
"""
        }
        
        return requirements.get(target.lower().replace(" ", "_"), "TODO")
    
    def _get_task_acceptance(self, target: str) -> str:
        """获取验收标准"""
        acceptance = {
            "planning": """
- 任务文档已创建
- 明确了功能点
- 识别了边界条件
- 流程图或说明文档
""",
            
            "unit_test": """
- 测试文件已创建
- 测试用例覆盖主要场景
- 首次运行测试（可能失败）
""",
            
            "code_impl": """
- 实现代码已创建
- 代码能编译/解析
- 通过单轮测试
""",
            
            "compile": """
- 无语法错误
- 无类型错误
- 无风格警告
""",
            
            "run_tests": """
- pytest 全部通过
- 覆盖率达标
- 测试结果已记录
""",
            
            "debug": """
- 错误原因已定位
- 问题已记录到 pit-library
- 修复后测试通过
"""
        }
        
        return acceptance.get(target.lower().replace(" ", "_"), "TODO")
    
    def _update_task_list(self):
        """更新主任务列表"""
        if not self.task_list_file.exists():
            return
        
        with open(self.task_list_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 简单的更新逻辑：添加执行时间戳
        lines = content.split("\n")
        output = []
        for line in lines:
            if "任务 1:" in line:
                output.append(f"## 🔵 任务 1: 规划开发任务 (当前正在执行)")
            else:
                output.append(line)
        
        with open(self.task_list_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output))
    
    def debug_issue(self, error: Dict):
        """记录调试问题"""
        tracker = IssueTracker()
        tracker.record(error)
        print(f"✅ 问题已记录到 pit-library")
    
    def complete_pipeline(self):
        """完成整个流水线"""
        self.pipeline_status = PipelineStatus.COMPLETED
        
        # 最后一条记录
        completion_record = {
            "project": self.project_name,
            "completed_at": timestamp(),
            "total_duration": "N/A",
            "issues_recorded": "N/A"
        }
        
        # 更新 MEMORY.md
        with open(WORKSPACE_ROOT / "MEMORY.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n## TDD Pipeline 完成\n")
            f.write(f"- 项目：{self.project_name}\n")
            f.write(f"- 完成时间：{completion_record['completed_at']}\n")
        
        self._save_pipeline_state()
        print("✅ TDD Pipeline 完成!")
        print("📝 结果已记录到 MEMORY.md")


# 主程序入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python tdd-pipeline.py <project-name> <target-node>")
        print("  python tdd-pipeline.py webhook-approval planning")
        print("  python tdd-pipeline.py webhook-approval run_tests")
        sys.exit(1)
    
    project = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None
    
    pipeline = TDDPipeline(project)
    
    if target:
        pipeline.progress_to(target)
    else:
        print("📊 当前状态:")
        print(json.dumps(pipeline.pipeline_status.value, indent=2))
        print("\n可用节点:")
        for node in PipelineStatus:
            if node.value != "completed" and node.value != "not_started":
                print(f"  - {node.value.replace('_', ' ').title()}")