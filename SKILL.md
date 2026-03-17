---
name: tdd-pipeline-executor
description: Execute TDD workflow with strong constraints using TDD Toolkit CLI. Use when implementing features with strict TDD process, checkpointing, issue tracking, and breakpoint continuation.
---

# TDD Pipeline 执行器（强约束版）

## 设计理念

本技能结合 LLM 的理解能力和脚本的强约束能力：
- **LLM 负责决策**：理解需求、规划任务、分析问题
- **脚本负责执行**：强制顺序、状态管理、问题记录

### 为什么需要脚本强约束？

LLM 输出具有概率特性，可能"理解偏差"。即使是先进的模型，也可能：
- 跳过关键步骤
- 理解错误或模糊处理
- 无法保证 100% 遵守流程

关键场景需要确定性：
- TDD 流程：必须先写测试，再写代码
- 断点续写：必须按顺序执行，不能跳过
- 问题记录：必须记录完整信息

脚本的不可变性保证：
- 代码逻辑是确定的，不会"理解偏差"
- 可以强制执行顺序和约束
- 失败时明确报错，不会"模糊处理"

## 何时使用

**适用场景：**
- 需要严格遵循 TDD 流程开发功能
- 需要断点续写能力（中断后继续）
- 需要记录开发过程中的问题
- 需要确保不会跳过关键步骤
- 需要系统化的开发流程追踪

**不适用场景：**
- 简单的一次性脚本
- 不需要 TDD 流程的快速原型
- 只需要简单代码生成的场景

## 核心工作流

### 完整的 TDD 循环

```
┌─────────────────────────────────────────┐
│  1. 初始化项目                           │
│  python3 __main__.py init             │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  2. 创建 Pipeline                       │
│  python3 __main__.py pipeline         │
│  --project <project-name>               │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  3. 按顺序推进节点                       │
│  planning → unit_test → code_impl       │
│  → compile → run_tests → debugging      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  4. 记录问题（如需要）                   │
│  python3 __main__.py record           │
└─────────────────────────────────────────┘
```

## CLI 命令详解

### 1. 初始化项目

```bash
python3 __main__.py init
```

**作用：**
- 创建 `pit-library/` 目录 - 问题记录存储
- 创建 `tdd-sessions/` 目录 - 会话状态存储

**输出示例：**
```
✅ TDD Toolkit 已初始化
   pit-library: /path/to/project/pit-library
   tdd-sessions: /path/to/project/tdd-sessions
```

### 2. 创建 Pipeline

```bash
python3 __main__.py pipeline --project <project-name>
```

**作用：**
- 创建 pipeline 状态文件
- 生成任务列表模板
- 初始化任务文档结构

**参数：**
- `--project, -p`: 项目名称（必需）

**输出示例：**
```
📊 项目：webhook-approval
   状态：not_started

可用节点:
   - Planning
   - Unit Test
   - Code Implementation
   - Compile
   - Run Tests
   - Debugging
```

### 3. 推进到指定节点

```bash
python3 __main__.py progress --project <project-name> --target <target-node>
```

**强约束机制：**
- 必须按顺序推进
- 脚本会检查前一个节点是否完成
- 不能跳过节点

**参数：**
- `--project, -p`: 项目名称（必需）
- `--target, -t`: 目标节点（必需）

**可用节点（按顺序）：**
1. `planning` - 任务规划
2. `unit_test` - 编写单元测试
3. `code_implementation` - 实现代码
4. `compile` - 编译/检查
5. `run_tests` - 运行测试
6. `debugging` - 调试回溯

**错误示例：**
```
❌ 不能推进到 code_implementation - 前一个节点未完成
请先完成上一个任务节点
```

### 4. 记录问题

```bash
python3 __main__.py record \
  --feature <feature-name> \
  --error-type <error-type> \
  --message <error-message> \
  --pipeline-node <current-node>
```

**参数：**
- `--feature, -f`: 功能名称（必需）
- `--error-type, -e`: 错误类型（必需）
- `--message, -m`: 错误信息（必需）
- `--pipeline-node`: Pipeline 节点（可选，默认 auto）

**输出示例：**
```
✅ 问题已记录!
   ID: v001
   文件：pit-library/v001-AssertionError.json
   类型：AssertionError
   严重性：high
   节点：run_tests
```

### 5. 查看问题列表

```bash
python3 __main__.py list --feature <feature-name>
```

**参数：**
- `--feature, -f`: 功能名称（可选）

**输出示例：**
```
📋 问题列表 (共 3 个)

## v001: AssertionError
   功能：webhook-approval
   严重性：high
   状态：open
```

## Agent 执行流程

### 标准执行模式

1. **规划阶段**
   ```
   Agent 行动：
   - 理解需求
   - 运行：python3 __main__.py progress --project <name> --target planning
   - 创建任务文档
   ```

2. **测试阶段**
   ```
   Agent 行动：
   - 编写测试代码
   - 运行：python3 __main__.py progress --project <name> --target unit_test
   - 运行测试（预期失败）
   ```

3. **实现阶段**
   ```
   Agent 行动：
   - 编写实现代码
   - 运行：python3 __main__.py progress --project <name> --target code_implementation
   - 运行测试（预期通过）
   ```

4. **验证阶段**
   ```
   Agent 行动：
   - 运行：python3 __main__.py progress --project <name> --target compile
   - 运行：python3 __main__.py progress --project <name> --target run_tests
   - 确保所有测试通过
   ```

5. **调试阶段**（如需要）
   ```
   Agent 行动：
   - 如果测试失败
   - 运行：python3 __main__.py progress --project <name> --target debugging
   - 运行：python3 __main__.py record 记录问题
   - 修复后重新测试
   ```

## 强约束机制详解

### 顺序执行

脚本会自动检查：
- 前一个节点必须完成
- 不能跳过节点
- 每个节点有明确的验收标准

**如果尝试跳过：**
```
❌ 不能推进到 code_implementation - 前一个节点未完成
请先完成上一个任务节点
```

### 断点续写

状态保存在 `tdd-sessions/<project-name>-pipeline.json`：

```json
{
  "project": "webhook-approval",
  "status": "unit_test",
  "current_index": 2,
  "completed_tasks": [0, 1],
  "nodes": [
    {
      "id": "planning",
      "name": "任务规划",
      "status": "completed",
      "executed_at": "2026-03-13T13:56:00"
    },
    {
      "id": "unit_test",
      "name": "编写单元测试",
      "status": "in_progress",
      "executed_at": "2026-03-13T14:00:00"
    }
  ]
}
```

**中断后重新运行：**
- 自动从上次位置继续
- 不需要手动指定起始节点
- 保证不会遗漏任何步骤

### 问题记录

问题保存在 `pit-library/v<version>-<error-type>.json`：

```json
{
  "id": "v001",
  "timestamp": "2026-03-13T13:56:00",
  "feature": "webhook-approval",
  "error_type": "AssertionError",
  "message": "Expected true but got false",
  "stack_trace": "...",
  "pipeline_node": "run_tests",
  "severity": "high",
  "status": "open"
}
```

**问题追踪：**
- 每个问题有唯一 ID
- 记录完整的错误上下文
- 支持后续分析和复盘

## 与现有技能的配合

本技能可以与以下技能配合使用：

### test-driven-development
- **TDD 方法论指导**：提供 TDD 的理论基础和最佳实践
- **本技能**：提供具体的执行工具和强约束机制

### systematic-debugging
- **系统化调试**：提供调试的方法论
- **本技能**：提供问题记录和追踪机制

### brainstorming
- **需求分析**：帮助理解需求和规划
- **本技能**：将规划转化为可执行的任务列表

## 注意事项

### 必须遵守

1. **不要绕过脚本**：所有状态推进必须通过 CLI
2. **遵循强约束**：不要尝试手动修改状态文件
3. **记录所有问题**：遇到问题立即使用 `record` 命令记录
4. **保持顺序**：必须按节点顺序推进

### 最佳实践

1. **每个功能点创建一个 Pipeline**：便于追踪和管理
2. **及时记录问题**：不要等到最后才记录
3. **定期查看问题列表**：使用 `list` 命令检查未解决的问题
4. **利用断点续写**：中断后不要重新开始，继续之前的 Pipeline

## 示例对话

**用户**：实现一个 webhook 审批功能

**Agent 执行流程**：

```bash
# 1. 初始化（如果还没初始化）
python3 __main__.py init

# 2. 创建 Pipeline
python3 __main__.py pipeline --project webhook-approval

# 3. 规划阶段
python3 __main__.py progress --project webhook-approval --target planning
# Agent 创建任务文档，规划功能点

# 4. 测试阶段
python3 __main__.py progress --project webhook-approval --target unit_test
# Agent 编写测试代码
# 运行测试（预期失败）

# 5. 实现阶段
python3 __main__.py progress --project webhook-approval --target code_implementation
# Agent 编写实现代码
# 运行测试（预期通过）

# 6. 验证阶段
python3 __main__.py progress --project webhook-approval --target compile
python3 __main__.py progress --project webhook-approval --target run_tests
# 确保所有测试通过

# 7. 如果失败，记录问题
python3 __main__.py record \
  --feature webhook-approval \
  --error-type AssertionError \
  --message "Expected true but got false" \
  --pipeline-node run_tests

# 8. 调试并重新测试
python3 __main__.py progress --project webhook-approval --target debugging
# Agent 分析问题，修复代码
# 重新运行测试
```

## 输出文件结构

执行完成后，会生成以下文件结构：

```
project/
├── pit-library/
│   ├── all-issues.json          # 所有问题列表
│   ├── v001-AssertionError.json # 单个问题详情
│   └── v002-TimeoutError.json   # 更多问题...
└── tdd-sessions/
    ├── webhook-approval-pipeline.json    # Pipeline 状态
    ├── webhook-approval-tasks.md         # 任务列表
    └── tasks/
        ├── planning.md          # 规划任务文档
        ├── unit-test.md         # 测试任务文档
        └── code-impl.md         # 实现任务文档
```

## 故障排查

### 问题：无法推进到下一个节点

**原因**：前一个节点未完成

**解决**：
1. 检查当前状态：`python3 __main__.py pipeline --project <name>`
2. 确保前一个节点的任务已完成
3. 如果确实需要跳过，需要手动修改状态文件（不推荐）

### 问题：找不到项目状态文件

**原因**：未创建 Pipeline 或路径错误

**解决**：
1. 确认已运行 `init` 命令
2. 检查 `tdd-sessions/` 目录是否存在
3. 使用正确的项目名称

### 问题：问题记录失败

**原因**：缺少必需参数

**解决**：
1. 确保提供了 `--feature`, `--error-type`, `--message`
2. 检查 `pit-library/` 目录权限
3. 查看错误信息并修正

## 版本兼容性

- **Python 版本**：3.7+
- **依赖**：
  - 标准库：`json`, `pathlib`, `datetime`, `argparse`
  - 无外部依赖

## 更新日志

- **v0.1.0** (2026-03-13)
  - 初始版本
  - 支持基本的 Pipeline 管理
  - 支持问题记录和追踪
  - 支持断点续写

---

**维护者**：TDD Toolkit Team  
**最后更新**：2026-03-13
