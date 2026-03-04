# 端到端测试说明

## 测试文件结构

- `data-source-management.spec.js` - 主要测试文件，测试足球SP管理的数据源管理页面
- `fixtures/data-sources.json` - 模拟数据源数据

## 测试场景覆盖

测试用例模拟真实用户操作，覆盖以下场景：

1. **页面加载** - 验证页面元素正常显示
2. **搜索功能** - 测试按名称搜索数据源
3. **新增数据源** - 测试创建新的数据源
4. **编辑数据源** - 测试修改现有数据源
5. **测试连接** - 测试数据源连接功能
6. **状态切换** - 测试启用/停用数据源
7. **批量选择** - 测试批量操作功能
8. **分页浏览** - 测试分页功能
9. **重置搜索** - 测试重置搜索条件

## 运行测试

### 前置条件

1. 确保前端开发服务器正在运行：
   ```bash
   npm run dev
   ```

   或者让 Playwright 自动启动（默认配置已支持）。

2. 确保 Playwright 浏览器已安装：
   ```bash
   npx playwright install chromium
   ```

### 运行所有端到端测试

```bash
npm run test:e2e
```

### 运行特定测试文件

```bash
npx playwright test tests/e2e/data-source-management.spec.js
```

### 以可视模式运行测试（可查看浏览器）

```bash
npx playwright test tests/e2e/data-source-management.spec.js --headed
```

## 测试模拟策略

测试使用以下模拟策略：

1. **API请求拦截** - 所有后端API请求都被拦截并返回模拟数据
2. **Mock认证** - 使用项目已有的Mock认证系统
3. **静态数据** - 使用预定义的模拟数据，确保测试可重复性

## 测试数据

模拟数据源包括：

1. 500彩票网API - 启用状态，错误率2.5%
2. 本地比赛数据 - 启用状态，错误率0%
3. 测试数据源 - 停用状态，错误率15%

## 注意事项

1. 测试需要浏览器环境，确保系统已安装 Chrome/Chromium
2. 测试运行时请勿操作浏览器，以免干扰测试
3. 如果测试失败，检查：
   - 前端开发服务器是否正常运行
   - 网络连接是否正常
   - 浏览器是否被其他进程占用
4. 测试使用模拟数据，不依赖真实后端服务

## 扩展测试

要添加新的端到端测试：

1. 在 `tests/e2e/` 目录下创建新的 `*.spec.js` 文件
2. 参考现有测试的模式编写测试用例
3. 添加必要的模拟数据到 `fixtures/` 目录
4. 更新 `playwright.config.js` 如果需要新的配置

## 故障排除

### 常见问题

**Q: 测试运行时浏览器不显示内容**
A: 可能是前端服务器未启动。手动运行 `npm run dev` 或检查 `playwright.config.js` 中的 `webServer` 配置。

**Q: 测试报错 "Cannot find module '@playwright/test'"**
A: 请运行 `npm install` 安装依赖。

**Q: 测试无法通过，但页面手动访问正常**
A: 检查测试中的选择器是否正确，页面结构是否有变化。

**Q: 测试运行缓慢**
A: 考虑禁用截图和视频录制（在 `playwright.config.js` 中设置 `video: 'off'`, `screenshot: 'off'`）。

### 调试模式

在测试中使用 `test.setTimeout(60000)` 增加超时时间，或使用 `--debug` 标志：

```bash
npx playwright test tests/e2e/data-source-management.spec.js --debug
```