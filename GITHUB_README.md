# TDD Execution Engine

**轻量级 TDD 执行器 + OpenClaw 知识库保鲜工具**

一个用于执行 TDD（Test-Driven Development）任务的工具，专门配合 OpenClaw 主引擎使用，自动执行测试、代码、验证、调试的流程，并记录问题供知识库保鲜。

---

## 🎯 功能特点

### **核心职责划分**

- **OpenClaw（主引擎）**: 需求理解 → 功能拆解 → 生成任务列表
- **本工具（执行器）**: 执行任务列表 → 按顺序执行 → 记录问题

### **关键特性**

✅ **扁平任务列表** - 不再区分阶段，直接执行任务  
✅ **断点续写** - 每步完成后自动保存状态  
✅ **强约束** - 每个任务必须完成才能进入下一个  
✅ **验收标准** - 通过测试通过率高作为 pass_gate  
✅ **问题记录** - 自动记录问题供 OpenClaw 知识库保鲜  

---

## 🚀 快速开始

### **1. 基本用法**

```python
from tdd_pipeline import TDDPipeline

# 定义任务列表
task_list = [
    {"action": "read_requirements"},
    {"action": "write_test", "output": "feature_test.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "write_code", "output": "feature.java"},
    {"action": "run_test", "expected": "success", "pass_gate": True},
]

# 创建执行器并执行
pipeline = TDDPipeline("feature-name", task_list)

# 自动断点续写执行
while pipeline.execute_next_task():
    pass
```

### **2. 调试循环**

```python
task_list = [
    {"action": "write_test", "output": "test.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "write_code", "output": "code.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "fix_implementation"},
    {"action": "run_test", "expected": "success", "pass_gate": True},
]

pipeline = TDDPipeline("debug-loop", task_list)
# 执行...
```

---

## 🔧 支持的 Action

| Action | 描述 | 参数 |
|--------|------|------|
| `read_requirements` | 从 OpenClaw 读取需求 | - |
| `write_test` | 生成测试代码 | `output`: 输出文件路径 |
| `run_test` | 运行测试 | `expected`: "success" \| "failure"<br>`pass_gate`: True/False |
| `write_code` | 生成实现代码 | `output`: 输出文件路径 |
| `fix_implementation` | 修复实现问题 | - |
| `refactor` | 重构代码 | - |
| `record_issue` | 记录问题（用于知识库） | 从 OpenClaw 提供的问题 JSON |

---

## 📋 问题记录

### **OpenClaw 提供问题格式**

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

### **问题日志输出**

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
```

---

## 🔄 断点续写

### **自动进行**

```bash
# 第一次执行
python -c "
from tdd_pipeline import TDDPipeline
task_list = [...]
pipeline = TDDPipeline('feature', task_list)
pipeline.execute_next_task()  # 执行到 task-3
"

# 第二次执行（断点续写）
python -c "
from tdd_pipeline import TDDPipeline
task_list = [...]
pipeline = TDDPipeline('feature', task_list)  # 自动从 task-3 继续
pipeline.execute_next_task()
"
```

### **状态文件**

```
tdd-sessions/
├── feature-name-state.json      # 断点状态
└── feature-name-issues.md       # 问题日志（Markdown 格式）
```

---

## 📁 项目结构

```
tdd-toolkit/
├── tdd-pipeline.py              # 核心执行器
├── utils.py                     # 工具函数
├── examples/
│   ├── simple-tdd-example.py    # 简单示例
│   └── java-tdd-example.md      # Java 测试规范
├── tdd-sessions/                # 执行状态和日志
└── README.md                    # 完整文档
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

## 🔄 集成工作流程

```
┌─────────────────────────────────────────┐
│  OpenClaw                              │
│  - 理解需求                                 │
│  - 拆解成大功能点                        │
│  - 生成任务列表                          │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  TDD Pipeline Executor                  │
│  - 执行任务列表                          │
│  - 单元测试 → 写代码 → 验证 → 调试         │
│  - 记录问题                            │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  OpenClaw 知识库保鲜                     │
│  - 读取问题日志                          │
│  - 更新 MEMORY.md                        │
│  - 记录经验教训                        │
└─────────────────────────────────────────┘
```

---

## 🚀 项目提交到 GitHub

### **准备工作**

1. **创建 GitHub 仓库**

```bash
# 在你的 GitHub Dashboard 创建新仓库
# 例如：https://github.com/你的用户名/tdd-pipeline
```

2. **配置 Git**

```bash
cd /Users/dylan/.openclaw/workspace/tdd-toolkit
git init
git add .
git commit -m "Initial commit: TDD 执行器 + OpenClaw 知识库保鲜"
```

3. **关联远程仓库**

```bash
git remote add origin https://github.com/你的用户名/tdd-pipeline.git
git push -u origin main
```

### **提交清单**

- ✅ `tdd-pipeline.py` - 核心执行器
- ✅ `utils.py` - 工具函数
- ✅ `examples/` - 示例代码
- ✅ `README.md` - 完整文档
- ✅ `GITHUB_README.md` - GitHub 专用文档
- ✅ `requirements.txt` - 依赖（可选）

---

## 📊 扩展方向

1. **多语言支持**: Java、Python、TypeScript
2. **CI/CD 集成**: 自动化执行任务
3. **代码扫描**: 自动生成问题记录
4. **覆盖率报告**: 集成 JaCoCo、Istanbul 等
5. **可视化**: WebUI 展示执行进度

---

## 💬 使用说明

### **1. 使用示例**

```bash
# 运行示例
python examples/simple-tdd-example.py

# 查看问题日志
cat tdd-sessions/demo-feature-issues.md
```

### **2. OpenClaw 集成**

OpenClaw 需要生成类似这样的任务列表：

```json
{
  "project": "webhook-approval",
  "task_list": [
    {"action": "read_requirements"},
    {"action": "write_test", "output": "webhook_approval_test.java"},
    {"action": "run_test", "expected": "failure"},
    {"action": "write_code", "output": "webhook_approval.java"},
    {"action": "run_test", "expected": "success", "pass_gate": true}
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

然后调用：

```python
from tdd_pipeline import TDDPipeline

pipeline = TDDPipeline(data["project"], data["task_list"])
while pipeline.execute_next_task():
    pass

# 记录问题
for issue in data["issues"]:
    pipeline.add_issue(issue)
```

---

## 📄 许可证

MIT License

---

**作者**: OpenClaw 团队  
**版本**: 0.1.0  
**更新时间**: 2026-03-13