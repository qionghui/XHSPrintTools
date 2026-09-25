# XHSPrintTools - AGENTS.md

## 项目概述

XHSPrintTools 是一个用于打印商品标签的自动化工具，主要用于处理电商订单中的商品信息，生成并打印标准化的商品标签。该工具特别适用于农产品、干货等需要分装销售的场景。

## 技术栈

- **编程语言**: Python（主要） + Delphi / Object Pascal（遗留，已冻结，不再维护）
- **运行平台**: Windows
- **数据格式**: JSON, Excel (.xlsx, .xls)
- **核心依赖**:
  - Python: pandas, openpyxl, psutil, dtpweb（打印 SDK，见 vendor/dtpweb/）
  - Delphi: ComObj (Excel OLE自动化), System.JSON（仅 delphi/ 遗留源码）

## 项目结构

```
XHSPrintTools/
├── .agent/                  # AI Agent 配置目录（本目录）
│   ├── AGENTS.md            # 项目级规则（当前文件）
│   ├── rules/               # 编码规则和项目规范
│   ├── skills/              # Agent Skills（可复用技能）
│   ├── spec/                # 项目规格文档
│   └── wiki/                # 项目知识库
├── src/                     # Python 源码（主业务）
│   ├── main.py              # 桌面端主脚本（订单处理 + 标签生成）
│   ├── server.py            # 移动端标签打印服务（HTTP）
│   ├── ddprint.py           # 打印模块（DTPWeb 封装）
│   └── paths.py             # 共享路径解析（基于 __file__ 派生项目根）
├── config/                  # 配置文件（受版本控制）
│   ├── config.json
│   ├── goods_config.json
│   └── exempt_config.json
├── data/                    # 主数据（受版本控制）
│   └── goods.xlsx           # 商品配置（唯一主数据）
├── delphi/                  # Delphi 遗留源码（冻结，不再维护）
├── vendor/dtpweb/           # DTPWeb 打印 SDK（whl + 文档 + demo）
├── tools/                   # 独立小工具目录（各有自己的 AGENTS.md，与主业务隔离）
│   ├── goods-list-tool/     # 货品清单小票（Python，独立 rules）
│   └── postage-calc/        # 邮费计算（Python，独立）
├── scripts/                 # 启动脚本
│   ├── print.bat            # 启动桌面端 + 移动端服务
│   └── print-custom-date.bat
├── tests/                   # 测试
│   └── test_label.py
├── runtime/                 # 运行时产物（已 gitignore）
│   ├── application.lock     # 程序运行锁文件
│   ├── latest_print_file.xlsx
│   └── bak/                 # 订单文件备份目录
├── dist/                    # 编译输出（已 gitignore，如 PrintTools.exe / main.exe）
├── main.spec                # PyInstaller 打包配置
└── README.md                # 项目说明文档（面向人类）
```

## 路径约定（重要）

所有源码对配置/数据/运行时资源的定位，**统一通过 `src/paths.py`** 派生自 `__file__` 的项目根解析，**不依赖 CWD**。因此：
- 不要在代码中用裸文件名（`'config.json'`、`'goods.xlsx'`、`'bak'` 等）或 `os.getcwd()`。
- 新增资源请先在 `src/paths.py` 中定义常量，再在 `main.py`/`server.py` 中引用。
- 锁文件统一为 `runtime/application.lock`（不要再用 `lock.txt`）。
- 订单备份目录为 `runtime/bak/`（由 `paths.ensure_runtime_dirs()` 自动创建）。

## 构建与运行

### Python 主程序（主要）

1. 安装依赖：`pip install pandas openpyxl psutil`，并安装打印 SDK：`pip install vendor/dtpweb/dtpweb-2.5.20250212-py3-none-any.whl`
2. 运行桌面端：`python src/main.py`（或双击 `scripts/print.bat`，同时启动移动端 `server.py`）
3. 自定义打印日期：`python src/main.py --diy_date`（或 `scripts/print-custom-date.bat`）
4. 运行测试：`python tests/test_label.py`
5. PyInstaller 打包：`pyinstaller main.spec`（产物 `dist/main.exe`）

### Delphi 遗留编译（仅维护参考，不再更新）

1. 使用 Delphi / RAD Studio 打开 `delphi/PrintTools.dproj`
2. 按 `F9` 或 `Ctrl+F9` 编译项目
3. 输出文件：`delphi/Win32/Debug/PrintTools.exe`（产物不入库）

### 运行检查清单

- 确保 `config/config.json` 存在且配置正确
- 确保 `data/goods.xlsx` 存在
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

- **严禁**修改 `runtime/bak/` 目录下的备份文件
- **严禁**删除 `runtime/application.lock` 文件（除非确认程序已退出）
- **严禁**在代码中硬编码密码、API密钥等敏感信息
- **严禁**修改 `data/goods.xlsx` 中的规格ID字段（业务主键）

### ⚠️ 谨慎操作

- 修改 `config/config.json` 前先备份
- 修改标签格式前需与业务方确认
- 修改 `src/main.py` 的订单/打印核心逻辑后必须充分测试
- 修改 `delphi/UMain.pas` 中的 Excel 操作逻辑后必须充分测试（遗留代码）

### ✅ 推荐操作

- Python 改动后运行 `python tests/test_label.py` 验证标签组装逻辑
- 修改核心逻辑前先备份相关文件
- 新增资源路径一律经 `src/paths.py` 定义，不裸写文件名

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
- 小工具不得引用/修改主业务代码与数据（`src/`、`data/goods.xlsx`、`runtime/bak/` 等）
- 新增小工具时，复制 `tools/goods-list-tool/` 作为模板，修改其 `AGENTS.md` 即可
