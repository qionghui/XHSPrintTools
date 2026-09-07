# my-tool 局部规则 — 货品清单小票

> ## ⚠️ 隔离边界声明
> 本工具独立于 XHSPrintTools 主业务（商品标签打印）。
>
> 主项目 `.agent/` 中的以下规则【不适用】于本目录：
> - `rules/business-rules.md`（标签格式、拼音排序、组合商品）
> - `rules/excel-operations.md`（Delphi Excel OLE 操作模板）
> - `skills/label-formatting/`、`skills/excel-data-processing/`、`skills/delphi-debugging/`
> - `spec/` 下所有业务需求与设计文档
>
> 仍然生效的通用规则：
> - `rules/security-and-config.md` 中的通用安全原则（不硬编码密钥、不提交敏感信息）
> - `rules/coding-style.md` 中与语言无关的部分（注释规范、错误处理原则）

## 工具用途

货品清单小票生成工具。读取工程目录下的 Excel 文件（物品、重量、价格），
通过 DTPWeb 打印助手逐行打印货品清单小票，支持自动分页。

> 借鉴主项目 `ddPrint.py` 的 DTPWeb 打印方式，但逻辑独立、排版针对清单场景重新设计。

## 技术栈

- **语言**: Python 3.x
- **运行平台**: Windows
- **打印库**: `dtpweb`（德途 DTPWeb 打印助手，与主项目 ddPrint.py 相同）
- **数据读取**: `pandas` + `openpyxl`
- **依赖**: 在 `requirements.txt` 中声明，按需安装

## 目录结构

```
tools/my-tool/
├── AGENTS.md          # 本文件（独立 rules）
├── main.py            # 主脚本入口（CLI 参数、Excel 读取、编排）
├── printer.py         # DTPWeb 打印封装（多页分页打印）
├── requirements.txt   # Python 依赖清单
├── data/              # 输入 Excel 存放目录
└── output/            # 输出/预览文件目录
```

## 输入数据格式

### Excel 文件要求

- **格式**: `.xlsx` 或 `.xls`
- **位置**: 默认读取 `data/` 目录，也可通过 `-i/--input` 指定路径
- **必需列**:

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| 物品 | 文本 | 物品名称 | 新疆若羌红枣 |
| 重量 | 文本/数字 | 重量（含单位） | 250克 |
| 价格 | 数字/文本 | 单价或小计 | 15.00 |

- **列名匹配**: 大小写不敏感，允许前后空格
- **空行处理**: 跳过"物品"列为空的行
- **NaN 处理**: 所有单元格读取后检查 NaN，转为空字符串

## 打印排版规则

### 页面参数（均可通过命令行覆盖）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--page-width` | 50 mm | 页面宽度（打印机纸宽） |
| `--page-height` | 80 mm | 单页高度 |
| `--font-height` | 3.0 mm | 正文字号 |
| `--title-font` | 4.0 mm | 标题字号 |
| `--margin` | 2 mm | 左右边距 |
| `--line-gap` | 1.5 mm | 行间距额外增量 |

### 版面布局（单页，从上到下）

```
┌──────────────────────────────────────┐ ← y=0
│            货品清单                   │  ← 标题（仅首页, title_font）
│            2026-08-10                │  ← 日期（仅首页, font_height）
├──────────────────────────────────────┤
│ 物品            重量      价格        │  ← 表头行（每页都有）
│ 红枣            250克     ¥15.00     │  ← 数据行区
│ 银耳            100克     ¥20.00     │
│ ...                                  │   ◀── 数据行下边界不可越过 safe_bottom_y
│                                      │
│────── safe_bottom_y（预留分界）──────│   ◀── 固定 2 行高度的页脚安全区
│ 合计: 5种 ¥55.00        第 1/2 页   │  ← 页脚行（合计行左 + 页码右，同一y）
└──────────────────────────────────────┘ ← y=page_height
```

### 底部安全区 & 重叠防护（强制性规则）

为防止**数据行最后一行**与**合计行/页码**发生视觉重叠，强制执行：

1. **每页预留 2 行高度的页脚安全区**（即 `2 × (font_height + line_gap)`）：
   - 即使单页数据很少，预留行也要存在（可呈空白），保证打印风格统一
   - 预留 2 行而不是 1 行，是为了给"合计行"与"数据行最后一行"之间留出视觉呼吸距离

2. **`safe_bottom_y` 计算**（数据行不可越界）：
   ```
   footer_rows = 2                         # 预留的页脚行数
   line_h = font_height + line_gap
   safe_bottom_y = page_height - margin - footer_rows × line_h
   ```
   数据行写入时的循环条件必须是：
   ```
   while 有数据 AND (当前 y + line_h) <= safe_bottom_y:
       写入一行数据
       y += line_h
   ```

3. **页脚行的 y 坐标固定**（不随数据量浮动）：
   ```
   footer_y = page_height - margin - font_height
   ```
   - 最后一页且仅一页：在 `footer_y` 左侧写合计，**不写页码**
   - 最后一页且多页：在 `footer_y` 左侧写合计，右侧写页码 `第 x/n 页`
   - 中间续页（非末页）：在 `footer_y` 右侧写页码，左侧留白

4. **页脚左右列不重叠的 x 分区**（基于 50mm 宽）：
   ```
   合计列: x = margin (2mm)          左对齐，最大宽度 ≈ 30mm
   页码列: x = page_width - margin - 16mm    右对齐预留宽度 ≈ 16mm
   ```

### 分页算法

1. **阶段 A — 粗分页数估算**（只用来确定 total_pages，不做正式排版）：
   ```
   每页预留 = 2 行页脚 + 表头 1 行 + 首页标题区
   ```
2. **阶段 B — 正式分页排版**：知道 total_pages 后逐页生成
   - 每一页先写顶部内容（标题/日期/表头），确定数据起始 y
   - 按 `safe_bottom_y` 阈值写数据行，**严格不越过**
   - 填完一页后下一页继续，直至所有物品分配完毕
3. **阶段 C — 写页脚**：
   - 末页写合计（+页码，多页时）
   - 中间续页仅写页码（多页时）

### 列坐标定义（基于 50mm 宽度）

| 列 | x 坐标 | 对齐 | 说明 |
|----|--------|------|------|
| 物品 | margin (2) | 左对齐 | 物品名称 |
| 重量 | page_width × 0.55 | 左对齐 | 重量 |
| 价格 | page_width - margin | 左对齐 | 价格（含 ¥ 前缀） |

> 列坐标按 `page_width` 等比例缩放，切换宽度时自动适配。

### 分页算法

1. **计算每页行数**:
   ```
   首页可用高度 = page_height - title_area - header_area - bottom_margin
   续页可用高度 = page_height - header_area - bottom_margin
   每页行数 = 可用高度 ÷ (font_height + line_gap)
   ```
2. **逐行填充**: 按顺序将物品行填入当前页，装不下则换新页
3. **合计行**: 仅出现在最后一页底部
4. **页码标注**: 续页底部右侧标注 `第 x/n 页`（当总页数 > 1）

### DTPWeb 调用规范

每页对应一次完整的 DTPWeb 打印任务：

```python
api = DTPWeb()
api.check_plugin()
printers = api.get_printers()
api.open_printer(**printers[0])
api.set_print_darkness(7.5)

for page in pages:
    api.start_job(width=page_width, height=page_height)
    for text_item in page.texts:
        api.draw_text(text_item['text'], x=text_item['x'], y=text_item['y'],
                      width=page_width - margin, height=font_height,
                      fontHeight=font_height)
    api.commit_job(orientation=0)

api.close_printer()
```

**关键约定**:
- `orientation=0`（纵向，清单不旋转）
- `start_job` / `commit_job` 必须成对调用，每页一对
- `draw_text` 中 `width` 参数 = `page_width - margin`（限制文本绘制宽度）
- 所有坐标单位为**毫米**
- NaN 文本必须跳过，不能传给 `draw_text`

## 命令行接口

```bash
python main.py [-i INPUT] [--page-width W] [--page-height H]
               [--font-height F] [--title TEXT] [--date DATE]
               [--dry-run] [--verbose]
```

| 参数 | 说明 |
|------|------|
| `-i, --input` | 输入 Excel 路径（默认: data/ 目录第一个 .xlsx） |
| `--page-width` | 页面宽度 mm（默认 50） |
| `--page-height` | 页面高度 mm（默认 80） |
| `--font-height` | 正文字号 mm（默认 3.0） |
| `--title-font` | 标题字号 mm（默认 4.0） |
| `--margin` | 边距 mm（默认 2.0） |
| `--line-gap` | 行间距增量 mm（默认 1.5） |
| `--title` | 小票标题（默认"货品清单"） |
| `--date` | 小票日期 YYYY-MM-DD（默认今天） |
| `--dry-run` | 仅排版预览，不实际打印 |
| `--verbose` | 详细日志 |

## Python 编码规范

### 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块/文件名 | snake_case | `data_loader.py` |
| 函数/变量 | snake_case | `get_receipt_data()` |
| 类名 | PascalCase | `ReceiptPrinter` |
| 常量 | UPPER_SNAKE | `MAX_RETRY = 3` |

### 代码风格

- 缩进: 4 个空格（禁止 Tab）
- 行宽: 不超过 100 字符
- 文件编码: UTF-8（文件头可加 `# -*- coding: utf-8 -*-`）
- 导入顺序: 标准库 → 第三方库 → 本地模块，各组之间空一行

```python
import os
import json
from pathlib import Path

import pandas as pd

from utils import format_receipt
```

### 错误处理

- 文件/网络操作必须 try-except，捕获**具体异常**而非裸 `Exception`
- 对外接口返回明确状态，不要静默失败
- 使用 `logging` 而非 `print` 输出运行信息

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)
```

### 路径处理

- 优先使用 `pathlib.Path`，不要字符串拼接路径
- 相对路径基于本工具目录，不依赖项目根目录

```python
# ✅ 推荐
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / 'data' / 'receipt.json'

# ❌ 避免
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'receipt.json')
```

## 运行与调试

```bash
cd tools/my-tool
pip install -r requirements.txt
python main.py
```

## 与主业务的关系

本工具与主业务（XHSPrintTools 商品标签打印）**逻辑独立**：

### 🚫 禁止
- 不要 import 或引用主业务 `PrintTools/` 下的 Delphi 代码
- 不要修改主业务的 `goods.xlsx`、`config.json`、`exempt_config.json`
- 不要在主业务 `bak/` 目录写入文件
- 不要复用主业务的标签格式规则（50mm×40mm 标签等）

### ✅ 允许
- 独立读写本工具目录下的文件
- 如需商品数据，应通过明确的数据导出/复制方式，不直接耦合主业务文件
- 可共享项目根的 git 仓库、开发环境配置

## 安全与边界

- 认证信息（API 密钥、Token、密码）严禁写入代码，使用 `.env` 或环境变量
- `.env` 文件必须加入 `.gitignore`
- 输出文件默认放在本工具目录下的 `output/` 子目录，不污染项目根
