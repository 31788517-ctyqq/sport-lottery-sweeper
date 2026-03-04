# E2E 测试说明

## 北单过滤面板测试

本目录包含北单过滤面板的端到端测试用例。

## 测试文件

- `test-beidan-filter.spec.js` - Playwright测试规范文件
- `run-beidan-filter-test.js` - 手动运行测试的脚本

## 运行测试

### 使用npm命令

```bash
# 运行所有e2e测试
npm run test:e2e

# 运行测试并在浏览器中显示UI
npm run test:e2e:headed

# 运行测试并进入调试模式
npm run test:e2e:debug
```

### 直接运行测试脚本

```bash
node e2e/run-beidan-filter-test.js
```

## 测试覆盖范围

- 页面访问和基本组件验证
- 获取实时数据功能
- 实力等级差筛选功能
- 赢盘等级差筛选功能
- 一赔稳定性筛选功能
- 高级筛选功能
- 快捷组合功能
- 重置功能
- 排序功能
- 导出功能
- 分页功能

## 前提条件

- 后端服务需要运行在 `http://localhost:8000`
- 前端服务需要运行在 `http://localhost:3000`
- 管理员账户凭据需要有效 (用户名: admin, 密码: admin123)
- 北单过滤API需要正确配置并可访问

## 注意事项

- 确保在运行测试前启动了后端和前端服务
- 测试过程中会使用管理员账户登录，请确保凭据有效
- 某些测试可能依赖于后端数据的可用性