# 外部资源索引

本文件管理项目相关的外部链接和资源。

## 开发工具

| 资源 | 链接 | 用途 |
|------|------|------|
| Delphi / RAD Studio 官方文档 | https://docwiki.embarcadero.com/RADStudio/ | VCL 控件、语法参考 |
| Delphi Basics (教程) | https://www.delphibasics.co.uk/ | Pascal 语法速查 |
| COM/OLE 编程参考 | https://learn.microsoft.com/en-us/windows/win32/com/ | Excel OLE 自动化原理 |

## Agent Skills 规范参考

| 资源 | 链接 | 用途 |
|------|------|------|
| Agent Skills 官方规范 | https://agentskills.io/specification | SKILL.md 格式标准 |
| AGENTS.md 标准 | https://agentsstandard.com/ | 多层级配置加载顺序 |
| GitHub Copilot AGENTS.md 最佳实践 | https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/ | 优秀案例分析 |

## 业务参考

| 资源 | 说明 |
|------|------|
| 保康滋补商行 - 内部系统 | 电商平台后台：订单导出入口 |
| 打印机型号 | 需确认具体型号（当前默认 50mm×40mm 热敏标签机） |
| goods.xlsx 维护人 | 运营同事负责新增商品 |

## MCP 工具建议（可选配置）

如需扩展 Agent 能力，可在 IDE 中配置以下 MCP Servers：

| MCP Server | 用途 |
|-----------|------|
| 文件系统 | 已内置，用于读写 .agent 目录 |
| 浏览器 (mcp-server-chromium) | 查阅 Delphi 文档、官方 API |
| GitHub | 如项目迁移到 Git，可用于 PR/Issue 操作 |
