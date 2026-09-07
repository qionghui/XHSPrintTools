# XHSPrintTools - AGENTS.md

## 项目概述

XHSPrintTools 是一个用于打印商品标签的自动化工具，主要用于处理电商订单中的商品信息，生成并打印标准化的商品标签。该工具特别适用于农产品、干货等需要分装销售的场景。

## 技术栈

- **编程语言**: Delphi / Object Pascal (主要) + Python (辅助脚本)
- **开发环境**: Delphi / RAD Studio (VCL框架)
- **数据格式**: JSON, Excel (.xlsx, .xls)
- **运行平台**: Windows
- **核心依赖**:
  - Delphi: ComObj (Excel OLE自动化), System.JSON
  - Python: pandas, openpyxl, psutil

## 项目结构

```
XHSPrintTools/
├── .agent/                  # AI Agent 配置目录（本目录）
│   ├── AGENTS.md            # 项目级规则（当前文件）
│   ├── rules/               # 编码规则和项目规范
│   ├── skills/              # Agent Skills（可复用技能）
│   ├── spec/                # 项目规格文档
│   └── wiki/                # 项目知识库
├── PrintTools/              # Delphi 项目源码
│   ├── PrintTools.dpr       # 项目主文件
│   ├── PrintTools.dproj     # Delphi 项目配置
│   ├── UMain.pas            # 主窗体单元
│   ├── UMain.dfm            # 主窗体布局
│   └── goods.xlsx           # 商品配置文件
├── tools/                   # 独立小工具目录（各有自己的 AGENTS.md）
│   └── my-tool/             # 货品清单小票（Python，独立 rules）
│       └── AGENTS.md        # 该工具局部规则（与主业务隔离）
├── bak/                     # 订单文件备份目录
├── PrintTools.exe           # 编译输出的可执行文件
├── README.md                # 项目说明文档（面向人类）
└── application.lock         # 程序运行锁文件
```

## 构建与运行

### Delphi 项目编译

1. 使用 Delphi / RAD Studio 打开 `PrintTools/PrintTools.dproj`
2. 按 `F9` 或 `Ctrl+F9` 编译项目
3. 输出文件: `PrintTools.exe` 位于项目根目录

### 运行检查清单

- 确保 `config.json` 存在且配置正确
- 确保 `goods.xlsx` 存在于可执行文件同目录
- 确保打印机已连接并配置好标签尺寸 (50mm × 40mm)

## 代码约定

### Delphi / Object Pascal 编码规范

1. **命名约定**:
   - 类名: `T` 前缀 (如 `TForm1`)
   - 成员变量: `F` 前缀 (如 `ForderExcelDirectory`)
   - 常量: 全小写或首字母大写 (如 `goodlist`)
   - 控件名: 类型缩写前缀 (如 `StringGrid1`, `Button1`, `pgc1`)

2. **代码组织**:
   - `interface` 部分声明类型和方法
   - `implementation` 部分实现方法
   - 使用 `{$R *.dfm}` 关联窗体资源

3. **错误处理**:
   - 使用 `try...except...end` 捕获异常
   - 对文件操作、Excel OLE 操作必须包在 try-finally 中确保资源释放

### 文件路径处理

- 路径中的斜杠统一转换为反斜杠: `StringReplace(Path, '/', '\', [rfReplaceAll])`
- 使用 `IncludeTrailingPathDelimiter()` 确保路径末尾有分隔符
- 使用 `ExtractFilePath(ParamStr(0))` 获取可执行文件所在目录

### Excel OLE 操作规范

```pascal
ExcelApp := CreateOleObject('Excel.Application');
try
  ExcelApp.Visible := False;
  ExcelApp.DisplayAlerts := False;
  // ... 操作代码
finally
  ExcelApp.Quit;
  ExcelApp := Unassigned;
end;
```

## 核心业务规则

### 标签字段格式

| 字段 | 格式示例 |
|------|---------|
| 成分 | 成分：新疆若羌红枣 |
| 规格 | 规格：散装称重 |
| 净重 | 净重：250克 |
| 保质期 | 保质期：12个月 |
| 产地 | 产地：新疆 |
| 等级 | 等级：特级 |
| 储存方式 | 储存方式：密封冰箱冷藏 |
| 包装日期 | 包装日期：YYYY-MM-DD |

### 组合商品子项格式

格式: `子项规格ID#数量,子项规格ID#数量`
示例: `6710cce9edb7ca0001035123#1,6710cce9edb7ca0001035124#2`

### 订单文件命名

手动打单文件名格式: `yyyyMMdd_hhnnss手动打单.xlsx`
示例: `20260810_153000手动打单.xlsx`

## 安全与边界

### 🚫 禁止操作

- **严禁**修改 `bak/` 目录下的备份文件
- **严禁**删除 `application.lock` 文件（除非确认程序已退出）
- **严禁**在代码中硬编码密码、API密钥等敏感信息
- **严禁**修改 `goods.xlsx` 中的规格ID字段（业务主键）

### ⚠️ 谨慎操作

- 修改 `config.json` 前先备份
- 修改标签格式前需与业务方确认
- 修改 UMain.pas 中的 Excel 操作逻辑后必须充分测试

### ✅ 推荐操作

- 每次修改后在 Delphi IDE 中编译确认无错误
- 修改核心逻辑前先备份相关文件
- 新增功能优先考虑向后兼容

## 子目录独立 Rules（tools/）

`tools/` 下的每个子目录是**与主业务无关的独立小工具**，各自拥有局部的 `AGENTS.md`，实现规则隔离。

### 层级加载机制

Agent 在 `tools/{tool}/` 下工作时，rules 按以下优先级叠加（后者覆盖前者）：

1. `~/.agents/AGENTS.md` — 全局用户规则（始终生效）
2. `.agent/AGENTS.md` — 本文件（项目级，主业务规则）
3. `tools/{tool}/AGENTS.md` — 子目录局部规则（★ 小工具专属）

### 隔离约定

- 子目录的 `AGENTS.md` 顶部声明**隔离边界**：明确哪些主业务规则不适用
- 通用安全规则（不硬编码密钥、不提交敏感信息）在所有层级始终生效
- 小工具不得引用/修改主业务代码与数据（`PrintTools/`、`goods.xlsx`、`bak/` 等）
- 新增小工具时，复制 `tools/my-tool/` 作为模板，修改其 `AGENTS.md` 即可
