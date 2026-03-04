# 多AI协同机制快速开始

## 立即使用方法

### 1. 检查文件锁
```bash
python .codebuddy/locks/check_lock.py check backend/models/user.py
```

### 2. 创建锁(修改前必做)
```bash
python .codebuddy/locks/check_lock.py create backend/models/user.py coder1
```

### 3. 释放锁(修改后必做)
```bash
python .codebuddy/locks/check_lock.py release backend/models/user.py coder1
```

### 4. 查看状态
```bash
cat .codebuddy/status.json
```

## AI标识分配建议
- **coder1**: 主要代码修改AI
- **coder2**: 辅助代码修改AI  
- **tester1**: 测试AI
- **reviewer1**: 代码审查AI

## 工作流程示例
```bash
# 1. 检查user.py是否可修改
python .codebuddy/locks/check_lock.py check backend/models/user.py

# 2. 创建锁开始修改
python .codebuddy/locks/check_lock.py create backend/models/user.py coder1

# 3. 进行代码修改...
# [在此处修改文件]

# 4. 释放锁
python .codebuddy/locks/check_lock.py release backend/models/user.py coder1
```

## 冲突处理
- 如果提示LOCKED: 等待其他AI完成或联系协调
- 如果提示STALE: 可手动删除过期锁文件
- 紧急情况下运行: `python .codebuddy/locks/check_lock.py clean`

## 代码注释规范
修改时在代码段添加:
```python
# AI_WORKING: coder1 @$(date) - 具体修改说明
# 修改内容...
# AI_DONE: coder1 @$(date)
```

机制已就绪，可以开始多AI协同工作！