# 安全与配置规则

## 数据安全

### 🚫 严禁

1. **严禁将以下信息提交到代码仓库**:
   - 数据库连接密码
   - API 密钥或 Token
   - 私人手机号、地址等个人信息
   - 内部服务器 IP 地址（除非是开发环境）

2. **严禁修改以下目录和文件**:
   - `bak/` 目录下的备份文件（历史凭证）
   - `application.lock` 文件（程序锁）
   - `goods.xlsx` 中的 `规格ID` 列（业务主键）

3. **严禁在代码中硬编码**:
   - 本地绝对路径（使用配置文件）
   - 用户个人信息
   - 密码或密钥

## 配置文件规范

### config.json

**位置**: 可执行文件同目录

```json
{
    "orderExcelDirectory": "E:\\xunlei",
    "orderExcelBackupDirectory": "C:\\Users\\51755\\Documents\\WeidaPrint\\Bill\\bak",
    "printExcelDirectory": "C:\\Users\\51755\\Documents\\WeidaPrint\\Print",
    "ggid_field": ["规格ID"],
    "num_field": ["SKU件数", "数量"]
}
```

**字段说明**:

| 字段 | 说明 |
|------|------|
| `orderExcelDirectory` | 等待处理的订单 Excel 目录 |
| `orderExcelBackupDirectory` | 订单备份目录（bak 目录） |
| `printExcelDirectory` | 打印文件输出目录 |
| `ggid_field` | 规格ID字段名列表（按优先级匹配） |
| `num_field` | 数量字段名列表（按优先级匹配） |

**注意事项**:
- 路径使用双反斜杠 `\\`
- 修改前先备份原文件
- 确保配置的目录实际存在

### exempt_config.json

**位置**: 可执行文件同目录

自动生成，无需手动编辑。存储各商品的免打数量:
```json
{
    "6710cce9edb7ca0001035123": 5,
    "6710cce9edb7ca0001035124": 3
}
```

**格式说明**:
- Key: 规格ID
- Value: 免打数量（整数，> 0）

### goods.xlsx

**位置**: 可执行文件同目录

**必填列**:
- 规格ID（业务主键，不可修改）
- 成分
- 规格
- 净重
- 保质期
- 产地
- 等级
- 储存方式

**可选列**:
- pingyin（拼音缩写，用于排序）
- 子项（组合商品配置）

## 文件操作安全

1. **写文件前检查**:
   - 文件是否被其他进程占用
   - 磁盘空间是否足够
   - 目录是否存在，不存在则创建

2. **删除文件前**:
   - 确认已备份到 bak 目录
   - 确认文件已成功处理

3. **路径处理**:
   ```pascal
   // ✅ 正确
   FilePath := IncludeTrailingPathDelimiter(Dir) + FileName;
   
   // ⚠️ 避免手动拼接
   FilePath := Dir + '\' + FileName;  // 可能缺少反斜杠
   ```
