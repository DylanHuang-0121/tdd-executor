# TDD 轻量级执行器 + OpenClaw 知识库保鲜

## 📖 工具简介

这是一个 TDD 执行工具，专门配合 OpenClaw 使用：

- **OpenClaw（主引擎）**: 需求分析 → 功能拆解 → 生成任务列表 → 记录问题
- **本工具（执行器）**: 执行任务列表 → 按顺序执行 → 记录问题 → 供知识库保鲜

---

## 🎯 核心设计

### **分工明确**

```
┌─────────────────────────────────────────┐
│  OpenClaw (需求理解 & 功能拆解)          │
│  - 理解需求                              │
│  - 拆解成大功能点                        │
│  - 生成任务列表                          │
│  - 记录问题到知识库                      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  TDD 执行器 (执行小任务)                  │
│  - 执行 task 列表                        │
│  - 单元测试 → 写代码 → 验证 → 调试         │
│  - 记录问题供 OpenClaw 保鲜              │
└─────────────────────────────────────────┘
```

---

## 🚀 使用方式

### **1. 基本用法**

```python
from tdd_pipeline import TDDPipeline

# 定义任务列表（Flatten，不区分阶段）
task_list = [
    {"action": "read_requirements"},
    {"action": "write_test", "output": "feature_test.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "write_code", "output": "feature.java"},
    {"action": "run_test", "expected": "success", "pass_gate": True},
    {"action": "record_issue"}  # 记录问题
]

# 创建执行器
pipeline = TDDPipeline("feature-name", task_list)

# 执行（断点续写自动进行）
while pipeline.execute_next_task():
    pass
```

### **2. 调试循环**

```python
task_list = [
    {"action": "read_requirements"},
    {"action": "write_test", "output": "test.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "write_code", "output": "code.java"},
    {"action": "run_test", "expected": "failure"},  # 第一次失败
    {"action": "fix_implementation"},              # 修复
    {"action": "record_issue"},                    # 记录问题
    {"action": "run_test", "expected": "success", "pass_gate": True},
]

pipeline = TDDPipeline("debug-loop", task_list)
# 执行...
```

---

## 📋 支持的 Action

| Action | 描述 | 参数 |
|--------|------|------|
| `write_test` | 编写测试代码 | `output`: 输出文件路径 |
| `run_test` | 运行测试 | `expected`: "success" \| "failure"<br>`pass_gate`: True/False |
| `write_code` | 编写实现代码 | `output`: 输出文件路径 |
| `fix_implementation` | 修复实现问题 | - |
| `refactor` | 重构 | - |
| `read_requirements` | 从 OpenClaw 读取需求 | - |
| `record_issue` | 记录问题 | 从 OpenClaw 提供的问题 JSON |

---

## 🔧 问题记录格式

### **OpenClaw 提供的问题格式**

```json
{
  "issue_data": {
    "title": "卡片验证边界问题",
    "stage": "unit_test",
    "description": "当卡号为 null 时应该抛出 IllegalArgumentException",
    "solution": "添加空值检查逻辑",
    "code_snippet": "if (cardNo == null) throw new IllegalArgumentException(...)",
    "test_case": "testAddCard_NullCardNo throws IllegalArgumentException"
  }
}
```

### **执行器记录问题**

```python
pipeline.add_issue(issue_data)
```

---

## 📁 输出文件

### **状态文件**

```
tdd-sessions/
├── feature-name-state.json      # 断点状态
└── feature-name-issues.md       # 问题日志（Markdown 格式）
```

### **问题日志格式**

```markdown
# feature-name - TDD 问题日志

## 概览
- **项目**: feature-name
- **问题数量**: 3
- **最后更新**: 2026-03-13 11:20

## 问题列表

### Issue-001: 边界条件验证缺失
**发现时间**: 2026-03-13 11:20
**阶段**: unit_test
**描述**: 当卡号为 null 时没有抛出异常
**解决**: 添加空值检查逻辑
**代码片段**: if (cardNo == null) throw new IllegalArgumentException(...)
**测试用例**: testAddCard_NullCardNo throws IllegalArgumentException

## 总结
这是一个边界验证问题...
```

---

## 🔄 断点续写

### **自动进行**

```python
# 第一次执行
pipeline = TDDPipeline("feature", task_list)
pipeline.execute_next_task()  # 执行到 task-3

# 第二次执行（断点续写）
pipeline = TDDPipeline("feature", task_list)  # 自动从 task-3 继续
```

### **状态文件**

```json
{
  "project": "feature",
  "current_index": 3,
  "completed_tasks": [0, 1],
  "last_updated": "2026-03-13T11:20:00",
  "task_count": 5,
  "issues": [...]
}
```

---

## ✅ 验收标准

### **测试通过 = 完成**

所有 `pass_gate: True` 的任务必须：
- 测试全部通过
- 无 `expected: "failure"` 的情况

### **强约束**

- 每个任务必须完成才能进入下一个
- `pass_gate: True` 不通过 → 阻塞后续任务

---

## 📊 与 OpenClaw 的集成

### **OpenClaw 输出 JSON**

```json
{
  "project": "webhook-approval",
  "task_list": [
    {"action": "read_requirements"},
    {"action": "write_test", "output": "webhook_approval_test.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "write_code", "output": "webhook_approval.java"},
    {"action": "run_test", "expected": "success", "pass_gate": true},
    {"action": "record_issue"}
  ],
  "issues": [
    {
      "title": "Webhook 签名验证失败",
      "stage": "debug",
      "description": "签名验证时不支持 RSA-PSS",
      "solution": "增加 RSA-PSS 支持",
      "code_snippet": "if (digest == RSA-PSS) ...",
      "test_case": "testWebhookSignature_RSAPSS"
    }
  ]
}
```

---

## 🚀 快速入门

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行示例
cd /Users/dylan/.openclaw/workspace/tdd-toolkit
python examples/simple-tdd-example.py

# 3. 查看生成的问题日志
cat tdd-sessions/demo-feature-issues.md
```

---

## 📝 扩展方向

1. **多语言支持**: Java、Python、TypeScript
2. **CI/CD 集成**: 自动化执行任务
3. **代码扫描**: 自动生成问题记录
4. **覆盖率报告**: 集成 JaCoCo、Istanbul 等

---

**版本**: 0.1.0  
**作者**: OpenClaw 团队  
**开源**: GitHub