# 编码风格规则

## Delphi / Object Pascal 编码规范

### 命名约定

| 类型 | 前缀 | 示例 |
|------|------|------|
| 类 (Class) | T | `TForm1`, `TExcelHelper` |
| 字段 (Field) | F | `ForderExcelDirectory`, `FSpecIDColumn` |
| 常量 (Const) | 无或全大写 | `goodlist`, `MAX_RETRY_COUNT` |
| 过程 (Procedure) | 无 | `FormCreate`, `Button1Click` |
| 函数 (Function) | 无 | `FindPYValue`, `LoadExcelToGrid` |
| 控件 (Control) | 类型缩写 | `StringGrid1`, `Button1`, `pgc1`, `Timer1` |
| 局部变量 | 无 | `i`, `j`, `FilePath`, `ExcelApp` |
| 类型参数 | T | `TMyGeneric<T>` |

### 控件命名前缀标准

| 控件 | 前缀 | 示例 |
|------|------|------|
| TForm | frm | frmMain |
| TButton | btn | btnSave, Button1 |
| TStringGrid | sg | StringGrid1 |
| TPanel | pnl | Panel1, pnlHeader |
| TLabeledEdit | le | LabeledEdit1, leSearch |
| TPageControl | pgc | pgc1 |
| TTabSheet | ts | TabSheet1, tsManual |
| TTimer | tmr | Timer1, tmrAutoLoad |
| TCheckListBox | clb | CheckListBox1 |
| TEdit | edt | edtInput |
| TMemo | mmo | mmoLog |

### 代码格式

1. **缩进**: 使用 2 个空格（Delphi 默认风格）
2. **行宽**: 建议不超过 120 字符
3. **begin..end**:
   ```pascal
   if Condition then
   begin
     DoSomething;
   end
   else
   begin
     DoOtherThing;
   end;
   ```

4. **空行**:
   - 过程/函数之间空 2 行
   - 逻辑块之间空 1 行

### 注释规范

- 注释用于解释 **为什么** (Why)，而不是 **做什么** (What)
- 复杂算法必须加注释说明思路
- 临时修复或 hack 必须加注释标注原因

```pascal
// 转换路径中的斜杠为反斜杠（修复路径格式问题）
ForderExcelDirectory := StringReplace(ForderExcelDirectory, '/', '\', [rfReplaceAll]);
```

### 变量声明

- 变量声明在块的最开始（Delphi 要求）
- 循环变量使用 `i`, `j`, `k` 等简短名称
- 布尔变量以 `Is`, `Has`, `Can` 开头: `IsLoaded`, `HasData`
