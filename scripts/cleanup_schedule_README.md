# 备份文件定期清理机制

## 概述

为防止备份文件占用过多磁盘空间，系统建立了自动化的备份文件清理机制，定期删除超过保留期限的旧备份文件。

## 清理策略

### 保留期限
- **每日临时清理**: 删除7天前的临时文件
- **每周备份清理**: 删除30天前的备份文件  
- **每月深度清理**: 删除90天前的旧备份文件

### 保护机制
- 重要数据库文件（如 `sport_lottery.db`）不会被误删
- 最近7天内的日志文件会被保留
- 大于100MB的文件会先移至回收站而不是直接删除

## 使用方法

### Windows系统

#### 手动执行清理
```batch
# 试运行（不实际删除文件）
scripts\cleanup_backups.bat --dry-run --verbose

# 实际执行清理（保留30天）
scripts\cleanup_backups.bat --days 30

# 自定义保留期限
scripts\cleanup_backups.bat --days 15
```

#### 设置定时任务
```batch
# 以管理员身份运行
scripts\setup_backup_cleanup_schedule.bat
```

这将创建三个定时任务：
- 每周日凌晨2点：常规备份清理
- 每月1号凌晨3点：深度清理
- 每天凌晨1点：临时文件清理

### Linux/Mac系统

#### 手动执行清理
```bash
# 给脚本执行权限
chmod +x scripts/cleanup_schedule_cron.sh

# 试运行
./scripts/cleanup_schedule_cron.sh --run-now --dry-run

# 实际执行
./scripts/cleanup_schedule_cron.sh --run-now --days 30
```

#### 设置定时任务
```bash
# 安装定时任务
./scripts/cleanup_schedule_cron.sh --install

# 查看状态
./scripts/cleanup_schedule_cron.sh --status

# 卸载定时任务
./scripts/cleanup_schedule_cron.sh --uninstall
```

## 日志和监控

### 日志文件
- 位置：`logs/backup_cleanup.log`
- 记录所有清理操作的详细信息
- 包括删除的文件、释放的空间、错误信息等

### 查看清理历史
```bash
# 查看最近清理记录
tail -f logs/backup_cleanup.log

# 查看清理统计
grep "清理统计" logs/backup_cleanup.log

# 查看错误记录
grep "ERROR" logs/backup_cleanup.log
```

## 配置自定义

### 修改保留期限
编辑清理脚本或命令行参数：
- Windows: 修改 `cleanup_backups.bat` 中的 `RETENTION_DAYS`
- Linux: 修改 `cleanup_schedule_cron.sh` 中的cron配置

### 添加自定义目录
在 `BackupCleanup` 类的 `__init__` 方法中修改 `backup_dirs` 列表：

```python
self.backup_dirs = [
    self.project_root / 'backup_failed_tests',
    self.project_root / 'custom_backup_dir',
    # 添加更多目录...
]
```

### 自定义文件保护规则
在 `should_delete_file` 方法中添加自定义保护逻辑：

```python
def should_delete_file(self, file_path):
    # 添加自定义保护规则
    if file_path.name.startswith('important_'):
        return False
    # ... 其他逻辑
```

## 故障排除

### 权限问题
- **Windows**: 确保以管理员身份运行计划任务设置脚本
- **Linux**: 确保用户对目标目录有写权限

### Python环境问题
- 确保Python 3.7+已安装并添加到PATH
- 检查依赖包：`pip install -r requirements.txt`

### 磁盘空间不足
- 清理脚本会自动处理大文件（移至回收站）
- 可手动清理回收站目录：`backup_failed_tests/recycle_bin/`

## 最佳实践

1. **定期检查日志**: 每周查看 `backup_cleanup.log` 确保清理正常运行
2. **监控磁盘空间**: 设置磁盘空间告警，及时清理
3. **测试新配置**: 使用 `--dry-run` 参数测试新的清理策略
4. **备份重要数据**: 在执行大规模清理前手动备份重要数据
5. **版本控制**: 将清理脚本纳入版本控制，便于追踪变更

## 注意事项

- 清理操作不可逆，请确保备份策略合理
- 生产环境建议先在测试环境验证清理策略
- 定期检查回收站目录，避免积累过多文件
- 重要业务时段避免执行大规模清理操作