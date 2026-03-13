# T-validate

# TDD Executor - 强约束 TDD 流水线执行器

## 📖 工具简介

TDD Executor 是一个强约束的 TDD 执行工具，支持：
- **断点续写**: 自动保存进度，支持中断后继续
- **问题追踪**: 记录调试过程中的问题和解决方案
- **多平台支持**: Aone Copilot、Claude Code、CodeFuse

---

## 🚀 一键安装

### 远程安装（推荐）

**使用 curl:**
```bash
# 安装到当前项目的 .aone_copilot/skills/ 目录
curl -fsSL https://raw.githubusercontent.com/DylanHuang-0121/tdd-executor/main/install.sh | bash

# 安装到指定项目的 .aone_copilot/skills/ 目录
curl -fsSL https://raw.githubusercontent.com/DylanHuang-0121/tdd-executor/main/install.sh | bash -s -- -d /path/to/project
```

**使用 wget:**
```bash
# 安装到当前项目的 .aone_copilot/skills/ 目录
wget -qO- https://raw.githubusercontent.com/DylanHuang-0121/tdd-executor/main/install.sh | bash

# 安装到指定项目的 .aone_copilot/skills/ 目录
wget -qO- https://raw.githubusercontent.com/DylanHuang-0121/tdd-executor/main/install.sh | bash -s -- -d /path/to/project
```

### 本地安装

```bash
# 克隆仓库
git clone https://github.com/DylanHuang-0121/tdd-executor.git
cd tdd-executor

# 安装到当前项目的 .aone_copilot/skills/ 目录
./install.sh

# 或安装到指定项目
./install.sh -d /path/to/your/project
```

### 安装结果

安装完成后，项目目录下会创建：

| 文件/目录 | 说明 |
|-----------|------|
| `.aone_copilot/skills/tdd-pipeline-executor/` | 技能目录（含 SKILL.md 和 Python 文件） |
| `.aone_copilot/skills/tdd-pipeline-executor/tdd-executor` | CLI 可执行脚本 |
| `pit-library/` | PIT 测试文件存储 |
| `tdd-sessions/` | 会话状态和问题记录 |

### 验证安装

```bash
# 在项目目录下运行
./aone_copilot/skills/tdd-pipeline-executor/tdd-executor --help
./aone_copilot/skills/tdd-pipeline-executor/tdd-executor init
```

---

## 📋 CLI 命令

### 初始化项目

```bash
cd /path/to/your/project
tdd-executor init
```

创建以下目录：
- `pit-library/` - PIT 测试文件存储
- `tdd-sessions/` - 会话状态和问题记录

### Pipeline 管理

```bash
# 创建新 Pipeline
tdd-executor pipeline --project my-feature

# 推进到指定节点
tdd-executor progress --project my-feature --target planning
```

### 问题记录

```bash
# 记录问题
tdd-executor record \
  --feature my-feature \
  --error-type AssertionError \
  --message "测试失败：边界条件未处理" \
  --pipeline-node run_tests

# 查看问题列表
tdd-executor list --feature my-feature
```

---

## 🎯 核心设计

### **TDD 流水线节点**

```
not_started → planning → write_test → run_tests → write_code → verify → completed
                                              ↓
                                           failed → debug → fix_implementation → run_tests
```

### **断点续写**

```python
# 状态自动保存在 tdd-sessions/<project>-state.json
{
  "project": "my-feature",
  "current_node": "run_tests",
  "completed_nodes": ["planning", "write_test"],
  "issues": [...]
}
```

---

## 📁 输出文件

```
tdd-sessions/
├── my-feature-state.json      # 断点状态
└── my-feature-issues.md       # 问题日志（Markdown 格式）

pit-library/
└── my-feature/                # PIT 测试文件
```

---

## 🔧 卸载

```bash
curl -fsSL https://raw.githubusercontent.com/DylanHuang-0121/tdd-executor/main/uninstall.sh | bash
```

或本地运行：
```bash
./uninstall.sh
```

---

**版本**: 1.0.0  
**作者**: Dylan Huang  
**开源**: [GitHub](https://github.com/DylanHuang-0121/tdd-executor)