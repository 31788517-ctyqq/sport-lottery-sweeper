# 前端调试指引 — 避免 ES Module 直接访问错误

## 常见问题
在浏览器中直接访问或引用含 `export` 的 JS 模块文件（如 `src/api/auth.js`）会导致：
```
Uncaught SyntaxError: Unexpected token 'export'
```
页面空白，无法正常加载。

## 原因
- Vite 项目中，`src/api/*.js` 等文件是 **ES Module**，只能通过 `import` 在代码中使用。
- 浏览器直接访问模块文件路径（如 `http://localhost:3000/src/api/auth.js`）会返回源码，并被当作普通脚本执行，从而报错。

## 正确使用方式
1. **在 Vue/JS 文件中引入**
   ```js
   import { authAPI } from '@/api/auth.js'
   ```
2. **不要直接在浏览器地址栏访问模块文件路径**
   - ❌ `http://localhost:3000/src/api/auth.js`
   - ✅ `http://localhost:3000/#/admin/login`
3. **不要在 HTML 中使用 `<script src="...auth.js">` 引入**

## 调试方法
- 如需在浏览器 Console 测试模块内容，使用动态导入：
  ```js
  import('@/api/auth.js').then(m => console.log(m.authAPI))
  ```
- 打开 **开发者工具 → Network**，确认没有以 `text/javascript` 加载 `auth.js` 等模块文件。

## 排查步骤
1. 检查地址栏是否误访问了模块文件路径。
2. 检查所有 HTML 模板，确保没有 `<script src="...auth.js">`。
3. 检查 Vue 单文件组件，确保没有在模板中用 `src` 加载 JS 模块。
4. 重启前端服务（`npm run dev` 或 `pnpm dev`）并访问正确路由。

## 备注
- 本指引适用于所有含 `export` 的 ES Module 文件（如 `src/api/*.js`、`src/composables/*.js` 等）。
- 保持前端路由访问方式统一为 `http://localhost:3000/#/xxx`，避免直接访问源码路径。

## 一键检查脚本（浏览器 Console 运行）
在浏览器开发者工具 **Console** 中粘贴以下代码并回车，可快速检测是否有 ES Module 文件被误加载：

```js
(function checkModuleMisload() {
  const modules = ['/src/api/auth.js'];
  const seen = [];
  if (!performance.getEntriesByType) {
    console.warn('当前浏览器不支持 performance.getEntriesByType，无法自动检测，请手动检查 Network 面板');
    return;
  }
  performance.getEntriesByType('resource').forEach(r => {
    modules.forEach(m => {
      if (r.name.endsWith(m)) {
        seen.push(r.name);
      }
    });
  });
  if (seen.length > 0) {
    console.error('❌ 检测到模块文件被直接加载：', seen);
    console.log('原因：这些 ES Module 文件被浏览器当作普通 JS 加载，导致 \"Unexpected token \\'export\\'\" 错误。');
    console.log('解决：不要直接访问这些路径，确保通过 import 在代码中使用。');
  } else {
    console.log('✅ 未检测到模块文件被直接加载，若仍报错请检查 Network 面板确认。');
  }
})();
```

**使用方法**：
1. 打开登录页或任意疑似报错的页面。
2. 按 `F12` 打开开发者工具，切换到 **Console**。
3. 粘贴上述代码并回车运行。
4. 根据提示判断是否存在误加载。
