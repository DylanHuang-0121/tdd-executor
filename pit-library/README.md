# pit-library - 坑数据库

这个目录记录所有测试失败的问题，供后续开发避坑使用。

## 文件命名规则

```
v001-encoding-fix.json  # 版本 001，类型：编码问题
v002-api-timeout.json   # 版本 002，类型：API 超时
```

## 文件内容格式

```json
{
  "id": "v001",
  "timestamp": "2026-03-13T10:30:00",
  "feature": "webhook 审批",
  "error_type": "FileNotFoundError",
  "message": "Webhook 配置文件不存在",
  "stack_trace": "...",
  "root_cause": "使用相对路径读取文件，未检查文件存在",
  "fix": "使用 Path.resolve() 获取绝对路径",
  "solution": "添加文件存在检查",
  "severity": "high",
  "status": "open"
}
```

## 使用方式

1. 测试失败时自动记录到这里
2. 每次开发前检查 pit-library，避免重复踩坑
3. 问题修复后，将 `status` 改为 `fixed`

## 示例

- [v001-encoding-fix.json](./v001-encoding-fix.json) - encoding 处理问题
- [v002-api-timeout.json](./v002-api-timeout.json) - API 超时问题

---

*由 IssueTracker 自动生成*