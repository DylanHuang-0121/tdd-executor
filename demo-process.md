# TDD Pipeline 使用流程

## 场景：实现一个 "Webhook 审批功能"

### 🔵 步骤 1: 初始化 Pipeline

```bash
cd /Users/dylan/.openclaw/workspace/tdd-toolkit

# 初始化 Webhook-approval 项目 Pipeline
python tdd-pipeline.py webhook-approval planning
```

**输出**：
```
✅ 已推进到：planning
📝 任务文档：tdd-sessions/tplanning.md
```

此时创建了两个文件：
- `tdd-sessions/webhook-approval-pipeline.json` - Pipeline 状态
- `tdd-sessions/webhook-approval-tasks.md` - 任务列表

---

### 📝 步骤 2: 完成任务规划（手动或让 Claude 做）

编辑 `tdd-sessions/tasks/planning.md`，填写：

```markdown
# TDD 任务文档：规划开发任务

**执行时间**: 2026-03-13 10:30:00

## 任务要求
- 明确要开发的单一功能点
- 确定输入输出接口
- 画出业务流程图
- 识别边界条件和异常场景

## 执行记录
### 功能需求
审批逻辑：
- 如果 amount > 1000，requires二次确认 = true
- 否则 requires二次确认 = false

### 流程图
```
input: {amount, demandId, description}
↓
if amount > 1000:
    requires二次确认 = true
else:
    requires二次确认 = false
↓
output: {approved: true, requires二次确认: bool}
```

### 边界条件
- amount = 0
- amount = 1000 (边界值)
- amount = 1001 (超过边界)
- amount = -1 (负数)
- demandId 为空字符串

⚠️ 问题：如果 amount 是字符串怎么办？
```

---

### 🟢 步骤 3: 推进到单元测试阶段

```bash
python tdd-pipeline.py webhook-approval unit_test
```

**输出**：
```
✅ 已推进到：unit_test
📝 任务文档：tdd-sessions/tasks/unit-test.md
```

---

### 🤖 步骤 4: 让 Claude Code 写测试

```bash
claude code --path /Users/dylan/.openclaw/workspace/tdd-toolkit/ \
  --prompt "根据 Webhook-approval 的项目规划，在 tests/ 目录创建 test_webhook_approval.py，编写 3 个测试用例：
  1. 测试 amount=1000 应该不需要二次确认
  2. 测试 amount=1001 应该需要二次确认
  3. 测试 amount=0 应该不需要二次确认
  
  先只写测试，不要实现代码"
```

Claude Code 会创建测试文件，并告诉你测试会失败（这是预期的！）。

---

### 🟡 步骤 5: 记录第一次测试失败

```bash
# 手动记录失败（或者让 Claude 自动调用）
python issue-tracker.py record \
  --feature "webhook-approval" \
  --error-type "AssertionError" \
  --message "test_approves_low_amount 失败：预期 requires_secondary=false，但实际为 true" \
  --pipeline-node "unit_test" \
  --severity "high"
```

**输出**：
```
✅ 问题已记录!
   ID: v003
   文件：/Users/dylan/.openclaw/workspace/tdd-toolkit/pit-library/v003-AssertionError.json
   节点：unit_test
```

---

### 🧑‍💻 步骤 6: 推进到代码实现

```bash
python tdd-pipeline.py webhook-approval code_impl
```

---

### 🤖 步骤 7: 让 Claude Code 实现代码

```bash
claude code --path /Users/dylan/.openclaw/workspace/tdd-toolkit/ \
  --prompt "读取 tests/test_webhook_approval.py 的测试用例，实现 approval.py 文件，确保测试通过"
```

Claude 会编写代码：

```python
def check_approval(amount: float) -> dict:
    """检查审批逻辑"""
    return {
        "approved": True,
        "requires_secondary": amount > 1000
    }
```

---

### 🟣 步骤 8: 推进到编译检查

```bash
python tdd-pipeline.py webhook-approval compile
```

---

### 🤖 步骤 9: 让 Claude Code 检查代码

```bash
claude code --path /Users/dylan/.openclaw/workspace/tdd-toolkit/ \
  --prompt "运行 pytest --collect-only tests/ 和 mypy approval.py，确保没有语法或类型错误"
```

---

### 🔴 步骤 10: 推进到运行测试

```bash
python tdd-pipeline.py webhook-approval run_tests
```

---

### 🤖 步骤 11: 让 Claude Code 运行测试

```bash
claude code --path /Users/dylan/.openclaw/workspace/tdd-toolkit/ \
  --prompt "运行 pytest -v tests/ 查看所有测试结果"
```

如果测试全部通过，恭喜！🎉

---

### 🟠 步骤 12: 如有失败，进入调试模式

```bash
python tdd-pipeline.py webhook-approval debug
```

然后分析 Claude Code 的错误日志，记录到 pit-library，修复后重新测试。

---

### ✅ 步骤 13: 完成流水线

```bash
python tdd-pipeline.py webhook-approval complete
```

这会：
- 标记流水线为完成
- 更新 `MEMORY.md`
- 输出完整报告

---

## 📊 完整的命令序列

```bash
# 初始化和推进
python tdd-pipeline.py webhook-approval planning
claude code --prompt "写测试..."
python tdd-pipeline.py webhook-approval unit_test

# 记录问题
python issue-tracker.py record --feature "webhook-approval" --error-type "..."

# 继续实现
python tdd-pipeline.py webhook-approval code_impl
claude code --prompt "实现代码..."
python tdd-pipeline.py webhook-approval compile
claude code --prompt "检查代码..."

# 最后测试
python tdd-pipeline.py webhook-approval run_tests
claude code --prompt "运行测试..."

# 完成
python tdd-pipeline.py webhook-approval debug  # 如有失败
python tdd-pipeline.py webhook-approval complete
```

---

## 🎯 核心优势

1. **强制顺序**：不能跳过任何节点
2. **完整记录**：每一步都有文档
3. **问题追踪**：自动记录到 pit-library
4. **自我提升**：每次踩坑都是学习机会
5. **可复用**：其他项目也可以沿用同样的流程

---

**这就是一个完整的、强约束的 TDD Pipeline！** 🚀