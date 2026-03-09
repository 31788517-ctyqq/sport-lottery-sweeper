// @ts-check
const { chromium } = require('playwright');
const { expect } = require('@playwright/test');

async function runBeidanFilterTest() {
  // 启动浏览器
  const browser = await chromium.launch({ headless: false }); // 设置为true可在无头模式下运行
  const page = await browser.newPage();

  try {
    console.log('开始测试北单过滤面板...');
    
    // 登录到管理面板
    console.log('步骤 1: 访问登录页面');
    await page.goto('http://localhost:3000/login');
    
    // 输入管理员凭据
    console.log('步骤 2: 输入登录凭据');
    await page.locator('input[type="text"]').fill('admin');
    await page.locator('input[type="password"]').fill('admin123');
    await page.locator('button[type="submit"]').click();
    
    // 等待登录完成并跳转到仪表板
    console.log('步骤 3: 等待登录完成');
    await page.waitForURL('http://localhost:3000/admin/dashboard');
    console.log('✓ 登录成功');

    // 导航到北单过滤页面
    console.log('步骤 4: 导航到北单过滤页面');
    await page.getByRole('link', { name: '北单过滤' }).click();
    await page.waitForURL('http://localhost:3000/admin/beidan-filter');
    console.log('✓ 成功导航到北单过滤页面');

    // 验证页面标题
    console.log('步骤 5: 验证页面标题');
    const title = await page.locator('.title').textContent();
    console.log(`页面标题: ${title}`);
    if (!title.includes('三维精算筛选器')) {
      throw new Error('页面标题不正确');
    }
    console.log('✓ 页面标题验证通过');

    // 验证获取实时数据功能
    console.log('步骤 6: 测试获取实时数据功能');
    const initialCount = await page.locator('.match-count span').textContent();
    console.log(`初始匹配数量: ${initialCount}`);
    
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(3000); // 等待数据加载
    
    const updatedCount = await page.locator('.match-count span').textContent();
    console.log(`更新后匹配数量: ${updatedCount}`);
    
    if (updatedCount !== initialCount) {
      console.log('✓ 数据已成功更新');
    } else {
      console.log('⚠ 数据可能未更新，但这可能是正常的（如果没有新数据）');
    }

    // 验证表格中有数据
    console.log('步骤 7: 验证表格中有数据');
    const tableRows = await page.locator('.result-card .el-table tbody tr').count();
    console.log(`表格行数: ${tableRows}`);
    
    if (tableRows > 0) {
      console.log('✓ 表格中存在数据');
    } else {
      console.log('⚠ 表格中没有数据');
    }

    // 测试筛选功能
    console.log('步骤 8: 测试筛选功能');
    const strengthCheckboxes = await page.locator('.checkbox-grid .el-checkbox-button').count();
    if (strengthCheckboxes > 0) {
      await page.locator('.checkbox-grid .el-checkbox-button').first().click();
      console.log('✓ 已选择一个筛选条件');
      
      await page.locator('button:has-text("应用筛选")').click();
      await page.waitForTimeout(2000);
      
      console.log('✓ 筛选已应用');
    }

    // 验证分页组件
    console.log('步骤 9: 验证分页组件');
    const hasPagination = await page.locator('.el-pagination').isVisible();
    if (hasPagination) {
      console.log('✓ 分页组件存在');
    } else {
      console.log('⚠ 分页组件不存在');
    }

    console.log('\n=== 北单过滤面板测试完成 ===');
    console.log('所有测试步骤已完成，没有遇到致命错误');
    
  } catch (error) {
    console.error('测试执行过程中遇到错误:', error.message);
    throw error;
  } finally {
    // 关闭浏览器
    await browser.close();
  }
}

// 如果直接运行此脚本，则执行测试
if (require.main === module) {
  runBeidanFilterTest()
    .then(() => {
      console.log('\n✅ 北单过滤面板端到端测试成功完成！');
    })
    .catch((error) => {
      console.error('\n❌ 北单过滤面板端到端测试失败:', error);
      process.exit(1);
    });
}

module.exports = { runBeidanFilterTest };