# AI文件锁目录

## 用途
防止多AI同时修改同一文件造成冲突

## 锁文件格式
`{filename}.{ai_name}.{timestamp}.lock`

## 使用规则
1. AI修改文件前必须创建对应锁文件
2. 修改完成后必须删除锁文件
3. 发现 stale lock (>30分钟) 可手动清理

## 示例
- `backend/models/user.py.coder1.1706151234.lock`
- `frontend/src/components/LoginModal.vue.tester1.1706151250.lock`