# Excel 操作规范

## 核心原则

Excel 操作必须使用 **try-finally** 结构，确保 Excel 进程被正确关闭，避免残留 Excel 进程占用内存。

## 标准模板

```pascal
var
  ExcelApp, Workbook, Sheet: Variant;
begin
  ExcelApp := CreateOleObject('Excel.Application');
  try
    ExcelApp.Visible := False;          // 必须隐藏
    ExcelApp.DisplayAlerts := False;    // 禁用提示框

    // 打开或创建工作簿
    Workbook := ExcelApp.Workbooks.Open(FileName);
    // 或: Workbook := ExcelApp.Workbooks.Add;
    try
      Sheet := Workbook.Sheets[1];      // 第一个工作表

      // ========= 业务操作开始 =========

      // 读取单元格
      CellValue := Sheet.Cells[Row, Col].Text;

      // 写入单元格
      Sheet.Cells[Row, Col] := Value;

      // 获取行/列数
      RowCount := Sheet.UsedRange.Rows.Count;
      ColCount := Sheet.UsedRange.Columns.Count;

      // ========= 业务操作结束 =========

    finally
      Workbook.Close(False);  // False = 不保存更改
    end;
  finally
    ExcelApp.Quit;
    ExcelApp := Unassigned;   // 释放 COM 对象
  end;
end;
```

## 注意事项

### 1. 单元格值读取

优先使用 `.Text` 属性而非 `.Value`，避免类型转换问题:
```pascal
// ✅ 推荐：获取显示文本
CellValue := Sheet.Cells[i, j].Text;

// ⚠️ 谨慎：获取原始值
CellValue := Sheet.Cells[i, j].Value;
```

### 2. 空值检查

```pascal
if not VarIsNull(CellValue) and not VarIsEmpty(CellValue) then
begin
  // 处理非空值
end;
```

### 3. 行列索引

Excel 的行和列从 **1** 开始，不是从 0 开始！

```pascal
// 读取 A1 单元格 (第1行，第1列)
Sheet.Cells[1, 1].Text;
```

### 4. StringGrid 与 Excel 映射

本项目中:
- `StringGrid.Cells[Col, Row]` → **列在前，行在后**
- `Sheet.Cells[Row, Col]` → **行在前，列在后**

注意转换顺序！

### 5. 异常处理

对每个单元格操作使用 try-except 保护:
```pascal
try
  CellValue := Sheet.Cells[i, j].Text;
  if not VarIsNull(CellValue) and not VarIsEmpty(CellValue) then
    StringGrid.Cells[j, i] := CellValue
  else
    StringGrid.Cells[j, i] := '';
except
  StringGrid.Cells[j, i] := '';
end;
```

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| 内存中有多个 EXCEL.EXE 进程 | 未调用 Quit 或 Unassigned | 确保 try-finally 正确嵌套 |
| 保存时弹出提示框 | DisplayAlerts 未设为 False | 设置 `ExcelApp.DisplayAlerts := False` |
| 单元格值为乱码 | 编码问题 | 使用 `.Text` 并检查文件编码 |
| 打开文件时卡住 | 文件被其他进程占用 | 检查文件是否已被打开 |
