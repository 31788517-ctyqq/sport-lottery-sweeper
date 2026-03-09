# 多AI协同工作机制

## 1. 文件锁机制
### 创建锁文件
```bash
# 格式: filename.ai_name.timestamp.lock
echo "working" > .codebuddy/locks/{filename}.{ai_name}.{timestamp}.lock
```

### 检查锁状态
```bash
# 检查文件是否被锁定
ls .codebuddy/locks/ | grep {filename}
```

### 释放锁
```bash
rm .codebuddy/locks/{filename}.{ai_name}.{timestamp}.lock
```

## 2. AI标识规范
- `coder1`, `coder2`: 代码编写AI
- `tester1`, `tester2`: 测试AI  
- `reviewer1`: 代码审查AI
- `analyzer1`: 分析AI

## 3. 工作区隔离
使用Git分支模拟:
- `ai-coder-1/feature/*`
- `ai-tester-1/test/*`
- `ai-reviewer-1/review/*`

## 4. 通信协议
### 状态广播
修改 `.codebuddy/status.json`:
```json
{
  "active_ais": ["coder1", "tester1"],
  "current_tasks": {
    "coder1": "修改backend/models/user.py",
    "tester1": "测试API endpoints"
  },
  "file_locks": [
    "backend/models/user.py.coder1.1706151234.lock"
  ],
  "last_updated": "2026-01-25T00:00:00Z"
}
```

### 代码注释标记
在修改的代码段添加:
```python
# AI_WORKING: coder1 @2026-01-25T00:00:00Z - 修复user.py语法错误
# AI_DONE: coder1 @2026-01-25T00:05:00Z
```

## 5. 冲突解决优先级
1. **人工开发者** (最高)
2. **reviewer** 
3. **coder**
4. **tester**
5. **analyzer** (最低)

## 6. 原子化操作规则
- 单次只能修改1个文件的前3处变更
- 连续修改间隔≥5秒
- 复杂任务拆解示例:
  ```
  任务: 修复user.py
  → 步骤1: 修复语法错误 (锁user.py)
  → 等待5秒
  → 步骤2: 修复导入路径 (锁user.py) 
  → 等待5秒
  → 步骤3: 添加日志 (锁user.py)
  ```

## 7. 应急处理
### 强制解锁
```bash
# 清理超过30分钟的锁
find .codebuddy/locks/ -name "*.lock" -mmin +30 -delete
```

### 冲突上报
在代码中添加:
```python
# AI_CONFLICT: coder1 vs tester1 @timestamp - 需要人工介入
```