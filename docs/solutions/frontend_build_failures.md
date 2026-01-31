# AI_WORKING: coder1 @1769627946 - 创建前端构建失败解决方案

# 前端构建失败

## 症状描述
- `npm run dev` 或 `npm run build` 命令失败
- 依赖包安装错误：`Cannot find module 'xxx'`
- Sass/SCSS 编译警告或错误
- TypeScript 类型检查失败
- Vite 开发服务器无法启动

## 根本原因
- Node.js 版本不兼容
- 依赖包版本冲突
- 缺少必要的全局依赖
- 配置文件错误或损坏

## 解决方案

### 1. 清理并重新安装依赖
```bash
# 进入前端目录
cd frontend

# 删除 node_modules 和 lock 文件
rm -rf node_modules package-lock.json pnpm-lock.yaml

# 清除 npm 缓存
npm cache clean --force

# 重新安装依赖
npm install
```

### 2. 检查 Node.js 版本
```bash
# 查看当前 Node.js 版本
node --version

# 项目要求 Node.js ≥ 16.0.0
# 如果版本过低，升级 Node.js
```

### 3. 使用正确的包管理器
项目支持多种包管理器：
```bash
# 使用 npm（默认）
npm install

# 使用 pnpm（推荐）
pnpm install

# 使用 yarn
yarn install
```

### 4. 修复 Sass 警告
常见 Sass 警告：`@use rule is loading members using mixin-like syntax`

**解决方案**：
1. 更新 `frontend/vite.config.js` 中的 Sass 配置：
```javascript
css: {
  preprocessorOptions: {
    scss: {
      additionalData: `@use "@/styles/variables.scss" as *;`
    }
  }
}
```

2. 确保所有 SCSS 文件使用正确的 `@use` 语法

### 5. 修复 TypeScript 错误
```bash
# 运行 TypeScript 检查
npx tsc --noEmit

# 根据错误信息修复类型定义
```

### 6. 检查配置文件
验证以下配置文件：
- `frontend/vite.config.js` - Vite 配置
- `frontend/tsconfig.json` - TypeScript 配置
- `frontend/.env` - 环境变量

### 7. 使用备用启动方式
如果标准方式失败：
```bash
# 使用开发服务器（无热重载）
cd frontend
npx vite --host 0.0.0.0 --port 5173

# 或使用简化脚本
start-frontend.bat
```

## 标准前端环境
- **Node.js**: ≥ 16.0.0
- **npm**: ≥ 8.0.0
- **Vite**: 5.x.x
- **Vue**: 3.x.x
- **TypeScript**: 5.x.x

## 预防措施
- 使用项目提供的 `package.json` 固定依赖版本
- 定期更新依赖包，但注意兼容性
- 编写前端代码时遵循 TypeScript 类型规范
- 使用 ESLint 和 Prettier 保持代码质量

## 相关文档
- [前端集成指南](../../FRONTEND_INTEGRATION_GUIDE.md)
- [Sass 警告修复总结](../../SASS_WARNINGS_FIX_SUMMARY.md)
- [前端故障排查](../../docs/frontend/FRONTEND_TROUBLESHOOTING.md)

# AI_DONE: coder1 @1769627946