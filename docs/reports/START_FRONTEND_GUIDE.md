# 🚀 前端启动完整指南

## 问题原因

错误信息: `ERR_PNPM_NO_IMPORTER_MANIFEST_FOUND`

**原因**: pnpm命令在错误的目录执行(项目根目录,而不是frontend子目录)

---

## ✅ 解决方案(3选1)

### 方案1: 快速启动脚本 (最简单) ⭐

**步骤:**
1. 双击文件: `quick-start.bat`
2. 等待服务启动
3. 浏览器访问: http://localhost:3000

**优点:**
- 一键启动,无需手动输入命令
- 自动检查环境
- 显示详细错误信息

---

### 方案2: 修复版批处理脚本

**步骤:**
1. 双击文件: `start-frontend-fixed.bat`
2. 脚本会自动切换到frontend目录
3. 等待服务启动

**特点:**
- 更详细的错误检查
- 显示Node.js和pnpm版本
- 自动安装缺失的依赖

---

### 方案3: PowerShell脚本

**步骤:**
1. 右键点击 `start-frontend-powershell.ps1`
2. 选择"使用PowerShell运行"
3. 或在PowerShell中执行:
   ```powershell
   .\start-frontend-powershell.ps1
   ```

**注意:** 可能需要先运行 `Set-ExecutionPolicy RemoteSigned`

---

### 方案4: 手动命令行 (最可靠)

#### Windows CMD:
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
pnpm run dev
```

#### Windows PowerShell:
```powershell
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
pnpm run dev
```

#### VS Code终端:
1. 打开VS Code
2. 按 `Ctrl + ~` 打开终端
3. 输入:
   ```cmd
   cd frontend
   pnpm run dev
   ```

---

## ✅ 成功启动的标志

终端应显示:
```
VITE v5.4.21  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://0.0.0.0:3000/
```

---

## 🎯 验证步骤

### 1. 检查服务是否运行
浏览器访问: http://localhost:3000

### 2. 检查控制台
- 按 `F12` 打开开发者工具
- 切换到 `Console` 标签
- 应该没有红色错误

### 3. 检查网络
- 切换到 `Network` 标签
- 刷新页面
- 检查API请求是否成功

---

## ❌ 常见错误及解决

### 错误1: `ERR_PNPM_NO_IMPORTER_MANIFEST_FOUND`

**原因**: 在错误的目录执行pnpm

**解决**:
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
pnpm run dev
```

---

### 错误2: `'pnpm' 不是内部或外部命令`

**原因**: pnpm未安装或不在PATH中

**解决**:
```cmd
npm install -g pnpm
```

---

### 错误3: `port 3000 is already in use`

**原因**: 3000端口已被占用

**解决**:
```cmd
# 查找占用端口的进程
netstat -ano | findstr :3000

# 结束该进程(可选)
taskkill /PID <进程ID> /F
```

---

### 错误4: `Cannot find module 'xxx'`

**原因**: 依赖未完整安装

**解决**:
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper\frontend
pnpm install
```

---

## 📊 启动后完整流程

### 1. 启动后端服务

打开新的终端窗口:
```cmd
cd c:\Users\11581\Downloads\sport-lottery-sweeper\backend
python main.py
```

### 2. 访问应用

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 3. 停止服务

在各自的终端窗口按 `Ctrl + C`

---

## 🛠️ 故障排查清单

- [ ] Node.js已安装(运行 `node --version`)
- [ ] pnpm已安装(运行 `pnpm --version`)
- [ ] 在frontend目录下运行(运行 `dir package.json`)
- [ ] node_modules目录存在
- [ ] 3000端口未被占用
- [ ] 后端服务已启动
- [ ] 浏览器控制台无错误

---

## 📁 项目脚本说明

| 文件名 | 说明 | 推荐度 |
|--------|------|--------|
| `quick-start.bat` | 一键快速启动 | ⭐⭐⭐ |
| `start-frontend-fixed.bat` | 修复版启动脚本 | ⭐⭐⭐ |
| `start-frontend-powershell.ps1` | PowerShell脚本 | ⭐⭐ |
| `start-frontend.bat` | 原始启动脚本 | ⭐ |

---

## 🎉 推荐启动方式

**最简单的方法:**
1. 找到项目根目录: `c:\Users\11581\Downloads\sport-lottery-sweeper`
2. 双击 `quick-start.bat`
3. 等待启动完成
4. 浏览器访问 http://localhost:3000

---

**更新时间**: 2026-01-18
**适用版本**: v1.0
