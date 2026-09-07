# Skills 索引

本目录下包含本项目可用的 Agent Skills。每个 Skill 是一个独立目录，核心文件为 `SKILL.md`。

## 渐进式加载说明

Agent 按以下三个阶段使用 Skills：

1. **阶段 1 - 发现**：仅加载各 Skill 的 `name` 和 `description`（~100 tokens）
2. **阶段 2 - 激活**：根据任务匹配，加载对应 Skill 的完整 `SKILL.md` 内容
3. **阶段 3 - 执行**：按需读取该 Skill 目录下的 `scripts/`、`references/`、`assets/` 附加资源

## 可用 Skills 列表

| Skill 目录 | 名称 | 适用场景 |
|-----------|------|---------|
| [delphi-debugging](./delphi-debugging/SKILL.md) | Delphi 调试技能 | 编译错误、运行时异常、OLE 残留、StringGrid 问题、事件调试 |
| [excel-data-processing](./excel-data-processing/SKILL.md) | Excel 数据处理技能 | goods.xlsx 配置变更、订单解析、组合商品展开、排序算法修改 |
| [label-formatting](./label-formatting/SKILL.md) | 标签格式化技能 | 标签字段格式、固定文案修改、日期格式、打印尺寸调整 |

## 路由约定

根据用户任务类型选择对应 Skill：

| 用户问题关键词 | 激活 Skill |
|-------------|-----------|
| 编译报错 / 运行报错 / 访问违规 / AV 错误 | delphi-debugging |
| Excel 读写出错 / 订单格式 / 组合商品 / 排序 | excel-data-processing |
| 标签改字 / 固定文案 / 日期格式 / 打印尺寸 / 打印偏移 | label-formatting |
| 新增功能 / 重构 / 架构调整 | 先加载 spec/ 目录，再按需激活 1-2 个 Skill |

## Skill 开发规范（新增 Skill 时遵循）

1. **目录命名**: 全小写，连字符分隔，不超过 64 字符。如 `code-review`、`data-migration`
2. **SKILL.md 格式**:
   ```markdown
   ---
   name: skill-name              # 必须与目录名一致
   description: >-               # 必须包含"做什么(WHAT)+什么时候用(WHEN)"
     一句话描述功能。
     适用于 A、B、C 等场景。
   version: 1.0.0                # 可选
   ---
   
   # Skill 标题
   
   ## 何时使用此技能
   ...
   
   ## 详细内容
   ...
   ```
3. **description 注意事项**:
   - 使用第三人称，不要用 "我" "你"
   - 1024 字符以内
   - 明确 WHAT + WHEN 才能正确触发
