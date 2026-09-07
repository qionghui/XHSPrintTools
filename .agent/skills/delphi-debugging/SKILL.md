---
name: delphi-debugging
description: Delphi VCL 项目的调试、编译和错误排查。适用于编译错误、运行时异常、OLE 对象释放、窗体事件调试等场景。
version: 1.0.0
author: XHSPrintTools Team
---

# Delphi 调试技能

## 何时使用此技能

当遇到以下场景时激活本技能：
- Delphi 编译错误或警告
- 运行时异常（AV 访问违规、类型转换错误等）
- Excel OLE 操作相关问题
- 窗体事件不触发或顺序异常
- StringGrid 显示或数据问题
- 内存泄漏或 Excel 进程残留

## 编译问题排查

### 步骤 1：确认错误类型

先编译获取完整错误信息，分类处理：

| 错误类型 | 常见原因 | 处理方式 |
|---------|---------|---------|
| `Undeclared identifier` | 缺少 uses 引用 | 在 uses 子句添加单元 |
| `Missing operator or semicolon` | 语法错误 | 检查上一行末尾分号 |
| `Incompatible types` | 类型不匹配 | 显式类型转换 |
| `Constant expression required` | 数组大小非编译期常量 | 改用动态数组 |
| `File not found` | 单元路径未配置 | 检查 Project Options → Search Path |

### 步骤 2：uses 引用原则

```pascal
uses
  // Win API 层（最先）
  Winapi.Windows, Winapi.Messages,
  // System 层
  System.SysUtils, System.Variants, System.Classes, System.JSON,
  // VCL 层
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  // 控件层
  Vcl.Grids, Vcl.ExtCtrls, Vcl.StdCtrls, Vcl.Mask, Vcl.ComCtrls,
  // COM 层（最后）
  ComObj;
```

## 运行时异常处理

### 访问违规 (Access Violation)

**特征**: `Access violation at address XXXXXXXX in module 'XXXX'. Read of address 00000000.`

**排查步骤**:
1. 检查 nil 指针引用
```pascal
// ✅ 访问前检查
if Assigned(StringGrid1) and (StringGrid1.RowCount > 1) then
begin
  // 安全访问
end;
```

2. 检查窗体创建顺序
```pascal
// FormShow 中避免立即访问控件，使用 PostMessage 延迟
procedure TForm1.FormShow(Sender: TObject);
begin
  PostMessage(Self.Handle, WM_USER + 1, 0, 0);  // 延迟到消息循环
end;
```

### Excel OLE 异常

**常见问题 1**: 操作 Excel 时出现 `Could not convert variant of type (Dispatch) into type (String)`

**解决**: 使用 `.Text` 而非 `.Value`
```pascal
// ✅ 正确
CellValue := Sheet.Cells[Row, Col].Text;

// ❌ 错误
CellValue := Sheet.Cells[Row, Col];
```

**常见问题 2**: 任务管理器中有大量 EXCEL.EXE 进程

**解决**: 确保 try-finally 正确嵌套，检查是否有遗漏的 `Quit` 调用
```pascal
ExcelApp := CreateOleObject('Excel.Application');
try
  // ...
  try
    // 打开工作簿
  finally
    Workbook.Close(False);
  end;
finally
  ExcelApp.Quit;          // 必须调用
  ExcelApp := Unassigned; // 必须释放
end;
```

## StringGrid 常见问题

### 行高为 0 导致数据不显示

排查 `ApplyFilter` 或类似设置 `RowHeights` 的逻辑：
```pascal
// 显示行
StringGrid1.RowHeights[i] := FRowHeights;  // 使用保存的默认高度

// 隐藏行
StringGrid1.RowHeights[i] := 0;
```

### 单元格编辑问题

确保 `goEditing` 选项已启用：
```pascal
StringGrid1.Options := StringGrid1.Options + [goEditing];
```

## 事件调试技巧

### 添加临时日志

```pascal
procedure TForm1.Button1Click(Sender: TObject);
begin
  OutputDebugString('Button1Click 触发');  // 使用 DebugView 查看
  ShowMessage('点击了按钮');               // 简单弹窗确认
  
  // ... 原有逻辑
end;
```

### 自定义消息处理

```pascal
// 声明
private
  procedure WMDelayedEnableTimers(var Message: TMessage); message WM_USER + 1;

// 实现
procedure TForm1.WMDelayedEnableTimers(var Message: TMessage);
begin
  Timer1.Enabled := True;  // 延迟启用定时器
end;
```

## 调试检查清单

- [ ] 所有 `CreateOleObject` 是否有对应的 `Quit` 和 `Unassigned`
- [ ] 所有 `try` 是否有匹配的 `finally` 或 `except`
- [ ] 访问控件前是否检查 `Assigned()`
- [ ] `StringGrid` 访问是否跳过标题行 (从 Row=1 开始)
- [ ] Excel 行列索引是否从 1 开始
- [ ] 路径是否使用 `IncludeTrailingPathDelimiter` 规范化
