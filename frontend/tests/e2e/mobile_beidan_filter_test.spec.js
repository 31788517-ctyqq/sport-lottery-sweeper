/**
 * 移动端北单三维筛选器端到端测试
 * 验证移动端专属路由 /m/beidan-filter 的布局、标签页切换和功能
 */

import { test, expect } from '@playwright/test';

test.describe('移动端北单三维筛选器功能验证', () => {
  test.beforeEach(async ({ page }) => {
    // 直接进入移动端专属路由
    await page.goto('/m/beidan-filter');
    
    // 等待页面加载完成
    await page.waitForLoadState('networkidle', { timeout: 15000 });
  });

  test('1. 移动端路由加载及布局检查', async ({ page }) => {
    console.log('验证移动端路由加载...');
    
    // 检查页面标题
    await expect(page.locator('text=北单三维筛选器').first()).toBeVisible({ timeout: 10000 });
    
    // 检查移动端布局包装器
    await expect(page.locator('.mobile-layout-wrapper.layout-mobile').first()).toBeVisible({ timeout: 10000 });
    
    // 检查顶部标题栏
    await expect(page.locator('.mobile-header').first()).toBeVisible({ timeout: 10000 });
    
    // 检查底部导航栏
    await expect(page.locator('.mobile-nav-bar').first()).toBeVisible({ timeout: 10000 });
    
    console.log('✓ 移动端路由加载及布局检查通过');
  });

  test('2. 底部导航栏标签页切换功能', async ({ page }) => {
    console.log('测试底部导航栏标签页切换...');
    
    // 检查底部导航栏存在
    const navBar = page.locator('.mobile-nav-bar');
    await expect(navBar).toBeVisible();
    
    // 检查五个导航标签是否存在
    const tabs = ['筛选', '结果', '统计', '策略', '导出'];
    for (const tabText of tabs) {
      const tab = navBar.locator(`button:has-text("${tabText}")`);
      await expect(tab).toBeVisible();
      await expect(tab).toBeEnabled();
    }
    
    // 测试默认激活"筛选"标签页
    const filterTab = navBar.locator('button:has-text("筛选")');
    await expect(filterTab).toHaveClass(/active/);
    
    // 验证"筛选"标签页对应的内容区域显示
    await expect(page.locator('.filter-section-mobile').first()).toBeVisible();
    
    // 切换到"结果"标签页
    const resultsTab = navBar.locator('button:has-text("结果")');
    await resultsTab.click();
    
    // 等待标签页切换动画
    await page.waitForTimeout(500);
    
    // 验证"结果"标签页激活
    await expect(resultsTab).toHaveClass(/active/);
    
    // 验证"结果"标签页对应的内容区域显示（可能为空，但组件应存在）
    // 注意：ResultsSectionMobile 组件可能在没有数据时显示空状态
    await expect(page.locator('.results-section-mobile').first()).toBeVisible();
    
    console.log('✓ 底部导航栏标签页切换功能通过');
  });

  test('3. 移动端筛选区域控件检查', async ({ page }) => {
    console.log('检查移动端筛选区域控件...');
    
    // 确保在"筛选"标签页
    const filterTab = page.locator('.mobile-nav-bar button:has-text("筛选")');
    await filterTab.click();
    await page.waitForTimeout(300);
    
    // 检查三维筛选标题
    await expect(page.locator('text=实力等级差 ΔP').first()).toBeVisible();
    await expect(page.locator('text=赢盘等级差 ΔWP').first()).toBeVisible();
    await expect(page.locator('text=一赔稳定性 P-Tier').first()).toBeVisible();
    
    // 检查选项按钮是否存在
    const strengthOptions = ['-3', '-2', '-1', '0', '+1', '+2', '+3'];
    for (const opt of strengthOptions) {
      const optionButton = page.locator(`.filter-section-mobile button:has-text("${opt}")`).first();
      await expect(optionButton).toBeVisible({ timeout: 5000 });
    }
    
    // 检查其它条件控件
    await expect(page.locator('label').filter({ hasText: '联赛筛选' }).first()).toBeVisible();
    
    console.log('✓ 移动端筛选区域控件检查通过');
  });

  test('4. 移动端结果卡片渲染检查', async ({ page }) => {
    console.log('检查移动端结果卡片渲染...');
    
    // 切换到"结果"标签页
    const resultsTab = page.locator('.mobile-nav-bar button:has-text("结果")');
    await resultsTab.click();
    await page.waitForTimeout(500);
    
    // 检查结果区域容器
    const resultsSection = page.locator('.results-section-mobile');
    await expect(resultsSection).toBeVisible();
    
    // 检查结果卡片（可能为空，但容器应存在）
    const resultCards = resultsSection.locator('.match-card');
    const cardCount = await resultCards.count();
    
    if (cardCount > 0) {
      console.log(`找到 ${cardCount} 个结果卡片`);
      // 验证第一个卡片的基本信息
      const firstCard = resultCards.first();
      await expect(firstCard.locator('.match-league')).toBeVisible();
      await expect(firstCard.locator('.match-teams')).toBeVisible();
    } else {
      console.log('结果区域为空，可能是没有筛选数据，但组件容器存在');
      // 验证空状态提示
      await expect(resultsSection.locator('text=暂无筛选结果').first()).toBeVisible();
    }
    
    console.log('✓ 移动端结果卡片渲染检查通过');
  });

  test('5. 移动端导出功能检查', async ({ page }) => {
    console.log('检查移动端导出功能...');
    
    // 切换到"导出"标签页
    const exportTab = page.locator('.mobile-nav-bar button:has-text("导出")');
    await exportTab.click();
    await page.waitForTimeout(500);
    
    // 检查导出区域容器
    const exportSection = page.locator('.export-section-mobile');
    await expect(exportSection).toBeVisible();
    
    // 检查三种导出格式按钮
    const exportFormats = ['CSV', 'JSON', 'Excel'];
    for (const format of exportFormats) {
      const exportButton = exportSection.locator(`button:has-text("${format}")`);
      await expect(exportButton).toBeVisible();
      await expect(exportButton).toBeEnabled();
    }
    
    // 检查导出说明文本
    await expect(exportSection.locator('text=选择导出格式').first()).toBeVisible();
    
    console.log('✓ 移动端导出功能检查通过');
  });

  test('6. 移动端策略管理区域检查', async ({ page }) => {
    console.log('检查移动端策略管理区域...');
    
    // 切换到"策略"标签页
    const strategyTab = page.locator('.mobile-nav-bar button:has-text("策略")');
    await strategyTab.click();
    await page.waitForTimeout(500);
    
    // 检查策略区域容器
    const strategySection = page.locator('.strategy-section-mobile');
    await expect(strategySection).toBeVisible();
    
    // 检查策略下拉选择器
    const strategySelect = strategySection.locator('.strategy-select');
    await expect(strategySelect).toBeVisible();
    
    // 检查策略操作按钮
    await expect(strategySection.locator('button:has-text("保存策略")').first()).toBeVisible();
    await expect(strategySection.locator('button:has-text("管理策略")').first()).toBeVisible();
    
    console.log('✓ 移动端策略管理区域检查通过');
  });

  test('7. 移动端统计卡片检查', async ({ page }) => {
    console.log('检查移动端统计卡片...');
    
    // 切换到"统计"标签页
    const statsTab = page.locator('.mobile-nav-bar button:has-text("统计")');
    await statsTab.click();
    await page.waitForTimeout(500);
    
    // 检查统计区域容器
    const statsSection = page.locator('.stats-card-mobile');
    await expect(statsSection).toBeVisible();
    
    // 检查统计信息显示（可能为空，但组件应存在）
    const statsCards = statsSection.locator('.stat-card');
    const cardCount = await statsCards.count();
    
    if (cardCount > 0) {
      console.log(`找到 ${cardCount} 个统计卡片`);
      // 验证第一个卡片的基本信息
      const firstCard = statsCards.first();
      await expect(firstCard.locator('.stat-number')).toBeVisible();
      await expect(firstCard.locator('.stat-label')).toBeVisible();
    } else {
      console.log('统计区域为空，可能是没有筛选数据，但组件容器存在');
      // 验证空状态提示
      await expect(statsSection.locator('text=暂无统计信息').first()).toBeVisible();
    }
    
    console.log('✓ 移动端统计卡片检查通过');
  });

  test('8. 移动端响应式布局适应性', async ({ page }) => {
    console.log('测试移动端响应式布局适应性...');
    
    // 获取当前视口尺寸
    const viewportSize = page.viewportSize();
    console.log(`当前视口尺寸: ${viewportSize.width}x${viewportSize.height}`);
    
    // 检查移动端布局类是否存在
    await expect(page.locator('.mobile-layout-wrapper.layout-mobile')).toBeVisible();
    
    // 检查安全区域适配类（如果支持）
    const supportsClass = await page.locator('.mobile-layout-wrapper.supports-safe-area').count();
    if (supportsClass > 0) {
      console.log('检测到安全区域适配支持');
    }
    
    console.log('✓ 移动端响应式布局适应性检查通过');
  });
});