# AI_WORKING: coder1 @1769627946 - 创建多AI协同工作机制解决方案

# 多AI协同工作机制

## 症状描述
- 多AI同时修改同一文件导致冲突
- 文件内容被意外覆盖或损坏
- 代码注释不符合项目规范
- 修改记录不清晰，难以追踪

## 根本原因
未遵守项目强制执行的AI协同工作规则。

## 解决方案

### 1. 修改文件前必须执行锁检查流程
**标准流程**：
```bash
# 1. 检查锁状态
python .codebuddy/locks/check_lock.py check <文件名> <AI标识>

# 2. 创建锁（如果未锁定）
python .codebuddy/locks/check_lock.py create <文件名> <AI标识>

# 3. 进行代码修改
# 4. 释放锁
python .codebuddy/locks/check_lock.py release <文件名> <AI标识>
```

### 2. AI身份标识分配
| 标识 | 角色 | 职责 |
|------|------|------|
| `coder1` | 主要代码编写AI | 核心功能开发 |
| `coder2` | 辅助代码编写AI | 辅助开发、工具函数 |
| `tester1` | 测试AI | 编写测试用例 |
| `reviewer1` | 代码审查AI | 代码质量检查 |
| `analyzer1` | 分析AI | 性能分析、架构评估 |

### 3. 代码注释强制规范
修改代码时必须在相关段落添加：
```python
# AI_WORKING: [AI标识] @[时间戳] - 具体修改说明
# [修改的代码]
# AI_DONE: [AI标识] @[时间戳]
```

**示例**：
```python
# AI_WORKING: coder1 @1769627946 - 修复用户模型__repr__方法语法错误
def __repr__(self):
    return f"User(id={self.id}, username={self.username})"
# AI_DONE: coder1 @1769627946
```

### 4. 冲突处理规则
- **LOCKED状态**：必须停止修改，等待或联系协调
- **STALE状态**（>30分钟）：可清理过期锁后继续
- **无法解决冲突**：添加 `# AI_CONFLICT: 需要人工介入` 并停止

### 5. 原子化操作限制
- 单次只能修改1个文件的前3处变更
- 连续修改同一文件间隔≥5秒
- 复杂任务必须拆解成多个独立步骤

### 6. 验证机制
每次操作后必须：
1. 检查锁状态确认成功
2. 验证 `status.json` 已更新
3. 确认代码注释已添加

## 锁脚本位置
- `./codebuddy/locks/check_lock.py`
- `./codebuddy/status.json`（状态记录）

## 预防措施
- 严格遵守多AI协同工作规则
- 修改前务必检查锁状态
- 添加规范的AI工作注释
- 及时释放文件锁

## 相关文档
- [多AI协同工作规则](../../.codebuddy/rules/multi-ai-coordination.mdc)
- [AI协调文档](../../.codebuddy/coordination.md)

# AI_DONE: coder1 @1769627946