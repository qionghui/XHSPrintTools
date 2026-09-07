# .agent 目录说明

本目录是 AI Agent 的项目上下文仓库，遵循 viding code / Agent Skills 开放标准。

## 目录结构

```
.agent/
├── AGENTS.md              # 入口文件：项目概述 + 技术栈 + 代码约定 + 业务规则（Agent 首先读取）
│
├── rules/                 # 全局规则（必须始终遵守）
│   ├── README.md          # Rules 索引
│   ├── coding-style.md    # 编码风格规范（Delphi 命名、格式）
│   ├── business-rules.md  # 业务规则（标签格式、排序、组合商品）
│   ├── excel-operations.md# Excel OLE 操作规范
│   └── security-and-config.md  # 安全与配置文件规范
│
├── skills/                # Agent Skills（按需加载的专业技能包）
│   ├── README.md          # Skills 索引 + 路由约定
│   ├── delphi-debugging/  # Delphi 调试技能
│   │   └── SKILL.md       #   编译错误、运行时异常排查
│   ├── excel-data-processing/  # Excel 数据处理技能
│   │   └── SKILL.md       #   订单解析、组合商品、排序算法
│   └── label-formatting/  # 标签格式化技能
│       └── SKILL.md       #   字段格式、固定文案、打印尺寸
│
├── spec/                  # 项目规格（"蓝图"）
│   ├── requirements.md    # 功能需求 + 非功能需求 + 范围边界
│   ├── design.md          # 技术设计：架构、模块、异常策略、技术债务
│   └── tasks.md           # 开发任务：版本路线图、Bug 优先级、维护计划
│
├── wiki/                  # 项目知识库（"百科全书"）
│   ├── architecture.md    # 系统架构图、数据流、文件依赖
│   └── domain.md          # 业务领域知识：合规、概念解释、运营流程
│
└── links/                 # 外部资源索引
    └── resources.md       # 文档链接、工具链接、MCP 配置建议
```

## 阅读顺序指引

### 新 Agent 接入项目（推荐顺序）

1. **首先**: 读取本文件所在的 `AGENTS.md`（项目根目录下的 `.agent/AGENTS.md`）
   - 了解项目做什么、技术栈、文件结构
   - 掌握核心代码约定和业务规则
   - 清楚哪些操作是禁区

2. **然后**: 根据任务类型选择深入阅读
   - **写代码改 Delphi 源码** → `rules/coding-style.md` + `rules/excel-operations.md`
   - **改业务逻辑（标签/排序/组合商品）** → `rules/business-rules.md`
   - **排查 Bug** → 激活对应 Skill：`.agent/skills/*/SKILL.md`
   - **做架构级决策 / 大版本升级** → `spec/design.md` + `wiki/architecture.md`
   - **了解业务背景** → `wiki/domain.md` + `spec/requirements.md`

### 渐进式加载

不要一次性把所有文件读入上下文。遵循：
- 始终加载: AGENTS.md（入口）+ 需要的 Rules
- 按需加载: 1-2 个匹配的 Skill
- 深入加载: spec/ 和 wiki/ 中对应当前任务的 1-2 个文件

## 兼容性说明

本目录结构兼容以下 Agent 平台：
- **Trae / viding code**：原生支持 `.agent/` + `skills/` 结构
- **Claude Code**：可在项目根创建 `CLAUDE.md` → 软链接指向 `.agent/AGENTS.md`
- **Cursor**：可在 `.cursor/rules/` 中引用本目录文件
- **GitHub Copilot**：`.agent/AGENTS.md` 格式兼容 AGENTS.md 规范
