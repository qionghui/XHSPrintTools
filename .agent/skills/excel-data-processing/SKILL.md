---
name: excel-data-processing
description: Excel 订单数据读取、商品匹配、标签数据生成与排序。适用于处理 goods.xlsx 配置、订单导入、组合商品拆解等业务场景。
version: 1.0.0
author: XHSPrintTools Team
---

# Excel 数据处理技能

## 何时使用此技能

当遇到以下场景时激活本技能：
- 新增或修改 goods.xlsx 商品配置字段
- 订单文件格式变更（字段名调整、新增字段）
- 组合商品子项逻辑修改
- 标签排序规则调整
- Excel 数据导入/导出功能开发

## 数据流转概览

```
订单文件 (.xlsx)
      │
      ▼
  规格ID 匹配 ────────┐
      │               │
      ▼               ▼
  数量字段        goods.xlsx 配置
      │               │
      └───────┬───────┘
              ▼
       生成标签数据
              │
              ▼
  按 成分→规格→净重→等级 排序
              │
              ▼
       生成打印文件
```

## 核心数据结构

### goods.xlsx 列定义

| 列顺序 (示例) | 列名 | 必填 | 说明 |
|-------------|------|------|------|
| A | 成分 | ✅ | 格式: `成分：xxx` |
| B | 规格 | ✅ | 格式: `规格：xxx` |
| C | 净重 | ✅ | 格式: `净重：xxx克` |
| D | 保质期 | ✅ | 格式: `保质期：12个月` |
| E | 产地 | ✅ | 格式: `产地：xxx` |
| F | 等级 | ✅ | 格式: `等级：特级` |
| G | 规格ID | ✅ | 业务唯一主键 |
| H | 储存方式 | ✅ | 格式: `储存方式：xxx` |
| I | pingyin | ❌ | 拼音缩写，用于排序 |
| J | 子项 | ❌ | 组合商品配置 |

**注意**: 实际列顺序可变，程序通过列名自动定位 `规格ID` 列。

### 订单文件必需字段

在 `config.json` 中配置字段名映射：
```json
{
    "ggid_field": ["规格ID"],
    "num_field": ["SKU件数", "数量"]
}
```

程序按数组顺序依次查找，优先使用先找到的字段。

### 标签数据结构

程序内部标签数据应包含以下字段：
```
{
  "成分": "成分：新疆若羌红枣",
  "规格": "规格：散装称重",
  "净重": "净重：250克",
  "保质期": "保质期：12个月",
  "产地": "产地：新疆",
  "等级": "等级：特级",
  "包装日期": "包装日期：2026-08-10",
  "储存方式": "储存方式：密封冰箱冷藏",
  "数量": 2,
  "拼音": "hz"
}
```

## 组合商品处理算法

### 子项格式解析

```
输入:  子项配置字符串 = "A#1,B#2"
       订单数量 = 3

步骤 1: 按逗号分割
        ["A#1", "B#2"]

步骤 2: 每项按 # 分割
        A: ID="A", 单件数=1
        B: ID="B", 单件数=2

步骤 3: 乘以订单数量
        A 实际数量 = 1 × 3 = 3
        B 实际数量 = 2 × 3 = 6

输出:  展开为独立标签行
        [A × 3] + [B × 6]
```

### 伪代码实现

```pascal
procedure ExpandCombinedItem(SpecID: string; OrderQty: Integer);
var
  SubItemConfig, SubItems: string;
  Parts: TStringList;
  SubID, SubQtyStr: string;
  SubQty, ActualQty: Integer;
begin
  SubItemConfig := GetGoodsSubItem(SpecID);
  if SubItemConfig = '' then Exit;  // 非组合商品

  Parts := TStringList.Create;
  try
    Parts.Delimiter := ',';
    Parts.DelimitedText := SubItemConfig;

    for SubItems in Parts do
    begin
      SubID := Fetch(SubItems, '#');
      SubQtyStr := SubItems;
      SubQty := StrToIntDef(SubQtyStr, 0);
      if SubQty > 0 then
      begin
        ActualQty := SubQty * OrderQty;
        AddLabelForGoods(SubID, ActualQty);  // 递归展开
      end;
    end;
  finally
    Parts.Free;
  end;
end;
```

## 排序算法

### 四级排序优先级

```
优先级 1: 成分 (升序)
    │
    ▼
优先级 2: 规格 (升序)
    │
    ▼
优先级 3: 净重 (升序，尝试提取其中数字比较)
    │
    ▼
优先级 4: 等级 (升序)
```

### 净重数字提取示例

```
"净重：100克"   →  100
"净重：250克"   →  250
"净重：1千克"   →  1000  (注意单位换算!)
"净重：散装称重" →  -1    (非数字放最后)
```

## 验证检查清单

新增/修改数据处理逻辑后，逐项验证：

- [ ] 普通商品：订单 N 件，生成 N 张标签（或 N 合一张显示数量）
- [ ] 组合商品：子项展开数量正确（子项配置数 × 订单数）
- [ ] 规格ID 不匹配：给出明确错误提示（SKU 名称没有在 GoodsConfig 中找到）
- [ ] 空字段处理：缺失可选字段不影响正常流程
- [ ] 排序验证：相同成分的商品排在一起，净重从小到大
- [ ] 导出 Excel：只导出数量 > 0 的行
