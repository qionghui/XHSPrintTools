# Rules 索引

本目录存放项目编码规则、业务规范、操作流程等 **静态约束类文档**。

Rules 与 Skills 的区别：
- **Rules** = 全局必须遵守的规则，Agent 始终遵循（类似法律）
- **Skills** = 按需激活的专业知识，特定任务才加载（类似专家顾问）

## Rules 列表

| 规则文件 | 主题 | 关键内容 |
|---------|------|---------|
| [coding-style.md](./coding-style.md) | 编码风格 | Delphi 命名约定、控件前缀、代码格式、注释规范 |
| [business-rules.md](./business-rules.md) | 业务规则 | 标签字段格式、拼音排序表、组合商品算法、订单规范 |
| [excel-operations.md](./excel-operations.md) | Excel 操作规范 | try-finally 标准模板、行/列索引、StringGrid 映射、常见坑 |
| [security-and-config.md](./security-and-config.md) | 安全与配置 | 配置文件结构、禁区操作、文件路径处理最佳实践 |

## 加载策略

Agent 在本项目中工作时，**始终加载** 以下 Rules（作为上下文的一部分）：
1. `coding-style.md` - 确保代码风格一致
2. `security-and-config.md` - 防止误操作破坏数据

根据任务类型 **按需加载**：
- 修改 UMain.pas 的 Excel 相关逻辑 → 额外加载 `excel-operations.md`
- 修改标签内容、格式、排序 → 额外加载 `business-rules.md`

## 新增 Rule 建议

当出现以下情况时，考虑新增 Rule 文件：
1. 某个约定被违反 2 次以上（说明需要明确文档化）
2. 新人上手时反复询问的问题
3. 涉及安全、合规、数据丢失风险的操作
