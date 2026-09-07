# 技术设计文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    主程序循环                         │
│  (Python main.py 或 Delphi Timer 轮询)               │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ 订单扫描  │   │ 手动打单  │   │ 文件备份  │
  └────┬─────┘   └────┬─────┘   └──────────┘
       │               │
       ▼               ▼
  ┌─────────────────────────────────┐
  │        标签数据生成引擎          │
  │  - 规格ID匹配                   │
  │  - 组合商品展开                  │
  │  - 排序处理                     │
  └───────────────┬─────────────────┘
                  ▼
        ┌───────────────────┐
        │   打印模块        │
        │  (PrintTools.exe) │
        └───────────────────┘
```

## 2. 核心模块设计

### 2.1 Delphi 窗体模块 (UMain.pas)

#### 类结构

```
TForm1
├── 私有字段
│   ├── ForderExcelDirectory: String      # 订单目录
│   ├── FSpecIDColumn: Integer            # 规格ID列索引
│   ├── FRowHeights: Integer              # 默认行高（用于筛选恢复）
│   └── goodlist / goodpylist: array      # 商品拼音对照表
│
├── 核心方法
│   ├── FormCreate                        # 初始化：加载goods、加载配置、填充列表
│   ├── LoadExcelToGrid                   # Excel → StringGrid 加载
│   ├── SaveGridToExcel                   # StringGrid → Excel 保存（筛选数量>0）
│   ├── ApplyFilter                       # 拼音搜索筛选
│   ├── AutoSizeColumns                   # 自动列宽
│   ├── FindPYValue                       # 商品名 → 拼音缩写
│   ├── SaveExemptConfig / LoadExemptConfig  # 免打配置读写
│   └── Timer1Timer                       # 自动加载 latest_print_file
│
└── 事件处理
    ├── StringGrid1MouseDown              # 数量/免打 左增右减
    ├── StringGrid2MouseDown              # 打印进度标记
    ├── CheckListBox1Click(Check)         # 商品类别快速选择
    └── Button1/3/4Click                  # 保存手动打单
```

#### 关键数据结构

```pascal
// 商品常量数组（如需新增商品，同步扩展这两个数组）
Const
  goodlist: array[0..13] of string = (
    '莲子', '银耳', '百合', '金线莲','桂圆',
    '姬松茸', '龙须草', '五指毛桃', '鹿茸菇', '红枣',
    '雪梨干', '羊肚菌', '风鼓草', '铁棍山药'
  );
  goodpylist: array[0..13] of string = (
    'lz', 'ye', 'bh', 'jxl','gy',
    'jsl','lxc','wzmt','llg','hz',
    'xlg','ydj','fgc','sy'
  );
```

### 2.2 Excel 交互设计

#### 读写流程

```
加载流程 (LoadExcelToGrid):
  CreateOleObject → Open Workbook → 获取 UsedRange
  → 遍历列: 查找规格ID列，复制列名到 Grid 第0行
  → 遍历行: 复制单元格，Grid第0列填数量默认空，第1列填免打默认空
  → Close → Quit → Unassigned

保存流程 (SaveGridToExcel):
  CreateOleObject → Add Workbook
  → 写列名行
  → 遍历 Grid 行: 数量>0 的行写入 Excel
  → SaveAs → Close → Quit → Unassigned
```

#### JSON 配置读写

```pascal
// 读取 UTF-8 JSON (处理 BOM)
Stream.Position := 0;
if Stream.Size >= 3 then  // 检查并跳过 UTF-8 BOM
begin
  Read BOM 3 bytes;
  if not EF BB BF then Seek(0);
end;
// 读取剩余 bytes → TEncoding.UTF8.GetString → ParseJSONValue
```

## 3. 异常处理策略

| 异常类型 | 捕获位置 | 处理方式 |
|---------|---------|---------|
| Excel OLE 初始化失败 | try-except 包裹 CreateOleObject | ShowMessage + 中止操作 |
| 文件不存在 | FileExists 检查 | ShowMessage + 使用默认路径 |
| 规格ID列未找到 | 遍历列名后仍为 -1 | 静默跳过，后续操作防护 |
| JSON 解析失败 | try-except 包裹 ParseJSONValue | ShowMessage + 跳过加载 |
| 单元格读取异常 | 每个 Cell 读写单独 try-except | 该单元格填默认值继续 |

## 4. 扩展点设计

### 4.1 新增商品类型
1. 在 `goodlist` 和 `goodpylist` 常量数组追加元素
2. 在 goods.xlsx 添加对应配置行
3. 无需重新编译 Python 脚本部分

### 4.2 新增标签字段
1. goods.xlsx 新增列
2. UMain.pas 中 StringGrid 列数自动 +（不影响逻辑）
3. 打印模块对应位置读取新列

### 4.3 新增订单字段
1. config.json 的 `ggid_field` / `num_field` 数组追加候选字段名
2. 程序按顺序自动匹配，无需改代码

## 5. 已知限制与技术债务

| 编号 | 问题 | 影响 | 建议修复版本 |
|------|------|------|-------------|
| TD-001 | Excel 操作依赖 COM，需要本机安装 Excel | 无 Excel 的机器无法运行 | v2.0 改用 openpyxl (Python) 或 NativeExcel |
| TD-002 | 商品类型硬编码在 Pascal 常量数组 | 新增商品需重新编译 Delphi | v1.5 改为从 goods.xlsx 读取商品列表 |
| TD-003 | 单实例锁文件路径固定 | 多账号同机运行冲突 | v1.x 改用用户目录下路径 |
| TD-004 | StringGrid2 打印进度不持久化 | 重开程序丢失勾选 | v2.0 持久化到 ini/json |
