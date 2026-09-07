# 开发任务清单

## 版本路线图

### v1.0 - 当前版本 (已完成)
- [x] Delphi GUI 手动打单界面
- [x] goods.xlsx 商品配置加载/编辑
- [x] 订单 Excel 解析与标签生成
- [x] 组合商品子项展开
- [x] 标签排序
- [x] 免打数量配置持久化
- [x] 订单文件备份机制
- [x] 自定义打印日期支持

### v1.5 - 近期优化
- [ ] **商品类型动态化**: 从 goods.xlsx 读取商品列表，替代硬编码常量数组
  - 文件: `PrintTools/UMain.pas`
  - 涉及: `goodlist`, `goodpylist` 常量 → 动态 TStringList
  - 风险: 低，向后兼容

- [ ] **配置可视化界面**: 在 Delphi 窗体中增加「设置」Tab，可视化编辑 config.json
  - 新增配置编辑界面
  - 路径选择使用 TFileOpenDialog
  - 风险: 低，纯新增功能

- [ ] **打印预览**: 生成标签图像预览后可确认再打印
  - 风险: 中，需要 GDI+ 或图形库

### v2.0 - 架构升级
- [ ] **Excel 引擎替换**: 去掉 COM 依赖，使用 NativeExcel 或直接迁移 Python 数据处理层
  - 文件: `ddPrint.py`, `PrintTools/UMain.pas`
  - 好处: 无需安装 Excel，启动更快，更稳定
  - 风险: 中，涉及核心流程改动

- [ ] **打印进度持久化**: StringGrid2 勾选状态保存到本地
  - 新增: `print_progress.json`
  - 每次勾选自动保存
  - 风险: 低

- [ ] **日志系统**: 替换 ShowMessage，输出到滚动日志区 + 文件
  - 日志级别: INFO / WARN / ERROR
  - 文件: `logs/YYYY-MM-DD.log`
  - 风险: 低

## Bug 修复优先级

### P0 - 阻塞级
(当前无)

### P1 - 高优先级
(当前无)

### P2 - 中优先级
- [ ] `ClearFilterAndNum` 过程中创建了 Excel OLE 对象但未操作，直接 Quit，可简化为纯 VCL 操作
  - 文件: `UMain.pas#L452-L473`
  - 影响: 每次清空会启动 Excel 进程一次，性能浪费

- [ ] `Timer1Timer` 中 finally 块注释掉了 `Timer1.Enabled := True`，导致定时器触发一次后停止
  - 文件: `UMain.pas#L786-L827`
  - 影响: latest_print_file.xlsx 不会自动刷新
  - 注意: 确认是有意注释还是 Bug

## 维护任务

| 周期 | 任务 | 说明 |
|------|------|------|
| 每周 | 清理 bak 目录 | 超过 30 天的备份文件可归档或删除（按业务要求） |
| 每月 | 编译验证 | 打开 Delphi 重新编译，确认无 Warning |
| 每季度 | goods.xlsx 备份 | 将 goods.xlsx 另存一份带日期的副本 |
| 每半年 | 打印机校准 | 打印测试页，检查标签偏移情况 |
