# 前端依赖安装指南

## 自动化安装 (推荐)

### Windows 用户

**方法1: 使用项目根目录的批处理文件**
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper
install-npm-deps.bat
```

**方法2: 使用 scripts 目录的批处理文件**
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper\scripts
install-frontend-deps.bat
```

### Linux/Mac 用户

```bash
cd c:\Users\11581\Downloads\sport-lottery-sweeper\scripts
bash install-frontend-deps.sh
```

---

## 手动安装

### 步骤1: 打开命令行
- Windows: 按 `Win + R`,输入 `cmd`,回车
- 或右键点击项目文件夹,选择"在终端中打开"

### 步骤2: 进入前端目录
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
```

### 步骤3: 检查 package.json 是否存在
```cmd
dir package.json
```

### 步骤4: 安装依赖
```cmd
npm install --legacy-peer-deps
```

如果安装失败,尝试:
```cmd
npm install --force
```

### 步骤5: 验证安装
```cmd
dir node_modules
```

应该看到大量的文件夹。

### 步骤6: 启动前端
```cmd
npm run dev
```

---

## 常见问题

### Q1: npm命令不存在
**解决方案:**
1. 确认 Node.js 已安装: `node --version`
2. 重新安装 Node.js: https://nodejs.org/

### Q2: 网络错误
**解决方案:**
```cmd
npm config set registry https://registry.npmmirror.com
npm install --legacy-peer-deps
```

### Q3: 依赖冲突
**解决方案:**
```cmd
npm install --force
```

### Q4: 权限错误
**解决方案:**
以管理员身份运行 cmd,然后执行安装命令

---

## 安装后验证

### 检查点
- ✅ `frontend/node_modules` 目录存在
- ✅ `frontend/package-lock.json` 文件存在
- ✅ 前端可以正常启动

### 启动测试
```cmd
cd frontend
npm run dev
```

访问 http://localhost:3000 查看应用

---

## 安装时间估计

- 首次安装: 5-10 分钟
- 网络较慢: 15-20 分钟
- 重新安装: 2-3 分钟

---

## 完成后的下一步

1. **启动后端服务**
   ```cmd
   cd backend
   python main.py
   ```

2. **启动前端服务**
   ```cmd
   cd frontend
   npm run dev
   ```

3. **访问应用**
   - 前端: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

---

**更新时间**: 2026-01-18
