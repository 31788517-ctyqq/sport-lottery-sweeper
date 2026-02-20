/**
 * 移动端北单三维筛选器功能测试
 * 验证移动端专属路由、布局、标签页切换等功能
 */

import { test, expect } from '@playwright/test';

test.describe('移动端北单三维筛选器功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问移动端专属路由
    await page.goto('/m/beidan-filter');
    
    // 等待页面基本加载完成
    await page.waitForLoadState('networkidle', { timeout: 30000 });
    
    // 等待移动端布局包装器出现
    await page.waitForSelector('.mobile-layout-wrapper', { timeout: 15000 });
  });

  test('1. 移动端路由加载和基本布局检查', async ({ page }) => {
    console.log('测试移动端路由加载和布局...');
    
    // 检查页面标题 - 使用更宽松的选择器
    await expect(page.locator('h1, .header-title').filter({ hasText: '北单三维筛选器' }).first()).toBeVisible({ timeout: 15000 });
    
    // 检查顶部标题栏是否存在
    await expect(page.locator('.mobile-header').first()).toBeVisible({ timeout: 10000 });
    
    // 检查底部导航栏是否存在
    await expect(page.locator('.mobile-nav-bar').first()).toBeVisible({ timeout: 10000 });
    
    // 检查移动端布局包装器类
    await expect(page.locator('.mobile-layout-wrapper').first()).toHaveClass(/layout-mobile/, { timeout: 10000 });
    
    console.log('✓ 移动端路由加载和基本布局检查通过');
  });

  test('2. 底部导航栏功能检查', async ({ page }) => {
    console.log('测试底部导航栏功能...');
    
    // 检查所有导航项是否存在
    const navItems = ['筛选', '结果', '统计', '策略', '导出'];
    
    for (const item of navItems) {
      const navLocator = page.locator(`.nav-item:has-text("${item}")`).first();
      await expect(navLocator).toBeVisible({ timeout: 10000 });
    }
    
    // 验证默认激活的标签页是"筛选"
    const activeNav = page.locator('.nav-item.active').first();
    await expect(activeNav).toHaveText('筛选', { timeout: 10000 });
    
    console.log('✓ 底部导航栏功能检查通过');
  });

  test('3. 标签页切换功能测试', async ({ page }) => {
    console.log('测试标签页切换功能...');
    
    // 定义导航项及其对应的预期内容
    const navTests = [
      { label: '结果', expectedContent: '.results-section-mobile' },
      { label: '统计', expectedContent: '.stats-card-mobile' },
      { label: '策略', expectedContent: '.strategy-section-mobile' },
      { label: '导出', expectedContent: '.export-section-mobile' },
      { label: '筛选', expectedContent: '.filter-section-mobile' }, // 切回筛选
    ];
    
    for (const testItem of navTests) {
      console.log(`  切换到 "${testItem.label}" 标签页...`);
      
      // 点击导航项
      const navItem = page.locator(`.nav-item:has-text("${testItem.label}")`).first();
      await navItem.click();
      
      // 等待切换动画
      await page.waitForTimeout(500);
      
      // 验证对应的内容区域显示
      if (testItem.expectedContent) {
        await page.waitForSelector(testItem.expectedContent, { timeout: 10000 });
        await expect(page.locator(testItem.expectedContent).first()).toBeVisible({ timeout: 10000 });
      }
      
      // 验证导航项激活状态
      await expect(navItem).toHaveClass(/active/, { timeout: 5000 });
      
      console.log(`    ✓ "${testItem.label}" 标签页切换成功`);
    }
    
    console.log('✓ 标签页切换功能测试通过');
  });

  test('4. 筛选页面功能验证', async ({ page }) => {
    console.log('测试移动端筛选页面功能...');
    
    // 确保当前在筛选标签页
    const filterNav = page.locator('.nav-item:has-text("筛选")').first();
    await filterNav.click();
    await page.waitForTimeout(500);
    
    // 检查三维筛选表单是否存在
    await page.waitForSelector('.filter-section-mobile', { timeout: 10000 });
    await expect(page.locator('.filter-section-mobile').first()).toBeVisible({ timeout: 10000 });
    
    // 检查实力等级差选项
    await expect(page.locator('text=实力等级差 ΔP').first()).toBeVisible({ timeout: 10000 });
    
    // 检查赢盘等级差选项
    await expect(page.locator('text=赢盘等级差 ΔWP').first()).toBeVisible({ timeout: 10000 });
    
    // 检查一赔稳定性选项
    await expect(page.locator('text=一赔稳定性 P-Tier').first()).toBeVisible({ timeout: 10000 });
    
    // 检查联赛筛选控件
    await expect(page.locator('label').filter({ hasText: '联赛筛选' }).first()).toBeVisible({ timeout: 10000 });
    
    console.log('✓ 筛选页面功能验证通过');
  });

  test('5. 结果页面功能验证', async ({ page }) => {
    console.log('测试移动端结果页面功能...');
    
    // 切换到结果标签页
    const resultsNav = page.locator('.nav-item:has-text("结果")').first();
    await resultsNav.click();
    await page.waitForTimeout(500);
    
    // 检查结果区域是否存在
    await page.waitForSelector('.results-section-mobile', { timeout: 10000 });
    await expect(page.locator('.results-section-mobile').first()).toBeVisible({ timeout: 10000 });
    
    // 如果有数据，检查结果卡片是否存在
    // 如果没有数据，检查空状态提示
    await page.waitForTimeout(1000); // 等待数据加载
    const hasResults = await page.locator('.match-card').count();
    
    if (hasResults > 0) {
      await expect(page.locator('.match-card').first()).toBeVisible({ timeout: 10000 });
    } else {
      await expect(page.locator('text=暂无筛选结果').first()).toBeVisible({ timeout: 10000 });
    }
    
    console.log('✓ 结果页面功能验证通过');
  });

  test('6. 统计页面功能验证', async ({ page }) => {
    console.log('测试移动端统计页面功能...');
    
    // 切换到统计标签页
    const statsNav = page.locator('.nav-item:has-text("统计")').first();
    await statsNav.click();
    await page.waitForTimeout(500);
    
    // 检查统计区域是否存在
    await page.waitForSelector('.stats-card-mobile', { timeout: 10000 });
    await expect(page.locator('.stats-card-mobile').first()).toBeVisible({ timeout: 10000 });
    
    // 检查至少有一个统计卡片
    await expect(page.locator('.stat-item-mobile').first()).toBeVisible({ timeout: 10000 });
    
    console.log('✓ 统计页面功能验证通过');
  });

  test('7. 策略页面功能验证', async ({ page }) => {
    console.log('测试移动端策略页面功能...');
    
    // 切换到策略标签页
    const strategyNav = page.locator('.nav-item:has-text("策略")').first();
    await strategyNav.click();
    await page.waitForTimeout(500);
    
    // 检查策略区域是否存在
    await page.waitForSelector('.strategy-section-mobile', { timeout: 10000 });
    await expect(page.locator('.strategy-section-mobile').first()).toBeVisible({ timeout: 10000 });
    
    // 检查策略选择控件
    await expect(page.locator('.strategy-select-mobile').first()).toBeVisible({ timeout: 10000 });
    
    console.log('✓ 策略页面功能验证通过');
  });

  test('8. 导出页面功能验证', async ({ page }) => {
    console.log('测试移动端导出页面功能...');
    
    // 切换到导出标签页
    const exportNav = page.locator('.nav-item:has-text("导出")').first();
    await exportNav.click();
    await page.waitForTimeout(500);
    
    // 检查导出区域是否存在
    await page.waitForSelector('.export-section-mobile', { timeout: 10000 });
    await expect(page.locator('.export-section-mobile').first()).toBeVisible({ timeout: 10000 });
    
    // 检查导出格式选项
    await expect(page.locator('text=CSV格式').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=JSON格式').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Excel格式').first()).toBeVisible({ timeout: 10000 });
    
    console.log('✓ 导出页面功能验证通过');
  });

  test('9. 移动端响应式布局测试', async ({ page }) => {
    console.log('测试移动端响应式布局...');
    
    // 测试不同屏幕尺寸下的布局
    const viewports = [
      { width: 375, height: 667, name: 'iPhone SE' },
      { width: 414, height: 896, name: 'iPhone XR' },
      { width: 768, height: 1024, name: 'iPad Mini' },
    ];
    
    for (const viewport of viewports) {
      console.log(`  测试 ${viewport.name} (${viewport.width}x${viewport.height})...`);
      
      // 设置视口大小
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      
      // 重新加载页面以适应新视口
      await page.reload();
      await page.waitForLoadState('networkidle', { timeout: 15000 });
      
      // 等待移动端布局包装器
      await page.waitForSelector('.mobile-layout-wrapper', { timeout: 10000 });
      
      // 验证关键元素仍然可见
      await expect(page.locator('.mobile-layout-wrapper').first()).toBeVisible({ timeout: 10000 });
      
      // 验证导航栏仍然可见
      await expect(page.locator('.mobile-nav-bar').first()).toBeVisible({ timeout: 10000 });
      
      console.log(`    ✓ ${viewport.name} 响应式布局正常`);
    }
    
    console.log('✓ 移动端响应式布局测试通过');
  });

  test('10. 触摸交互优化检查', async ({ page }) => {
    console.log('测试移动端触摸交互优化...');
    
    // 等待页面稳定
    await page.waitForTimeout(1000);
    
    // 检查按钮最小触摸尺寸 - 只检查可见按钮
    const testButtons = await page.locator('button:visible').all();
    
    for (const button of testButtons) {
      const box = await button.boundingBox();
      if (box) {
        // 验证触摸目标尺寸 >= 44x44px
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
    
    // 检查输入框字体防缩放
    const inputs = await page.locator('input:visible, textarea:visible').all();
    for (const input of inputs) {
      const fontSize = await input.evaluate(el => {
        return parseFloat(window.getComputedStyle(el).fontSize);
      });
      expect(fontSize).toBeGreaterThanOrEqual(16); // iOS防缩放要求
    }
    
    console.log('✓ 移动端触摸交互优化检查通过');
  });
});