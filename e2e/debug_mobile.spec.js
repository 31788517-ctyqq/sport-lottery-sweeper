import { test, expect } from '@playwright/test';

test('调试移动端页面', async ({ page }) => {
  // 捕获控制台日志
  page.on('console', msg => {
    console.log(`[浏览器控制台] ${msg.type()}: ${msg.text()}`);
  });
  page.on('pageerror', error => {
    console.log(`[页面错误] ${error.message}`);
  });
  
  console.log('访问移动端路由...');
  await page.goto('/m/beidan-filter');
  
  // 等待网络空闲
  await page.waitForLoadState('networkidle', { timeout: 30000 });
  
  // 截图
  await page.screenshot({ path: 'debug-mobile.png', fullPage: true });
  console.log('截图已保存: debug-mobile.png');
  
  // 获取页面HTML
  const html = await page.content();
  console.log('页面HTML长度:', html.length);
  
  // 检查关键元素
  const selectors = [
    '.mobile-layout-wrapper',
    '.mobile-layout',
    '.mobile-header',
    '.mobile-nav-bar',
    '.nav-item',
    '.filter-section-mobile',
    '.results-section-mobile',
    '.stats-card-mobile',
    '.strategy-section-mobile',
    '.export-section-mobile'
  ];
  
  for (const selector of selectors) {
    const count = await page.locator(selector).count();
    console.log(`选择器 "${selector}": ${count} 个元素`);
    if (count > 0) {
      const first = page.locator(selector).first();
      const isVisible = await first.isVisible();
      console.log(`  可见: ${isVisible}`);
      const className = await first.getAttribute('class');
      console.log(`  类名: ${className}`);
    }
  }
  
  // 检查布局模式
  const layoutWrapper = page.locator('.mobile-layout-wrapper');
  const hasMobileClass = await layoutWrapper.evaluate(el => el.classList.contains('layout-mobile'));
  const hasDesktopClass = await layoutWrapper.evaluate(el => el.classList.contains('layout-desktop'));
  console.log(`布局类: layout-mobile=${hasMobileClass}, layout-desktop=${hasDesktopClass}`);
  
  // 检查设备信息
  const deviceInfo = await page.evaluate(() => {
    return {
      userAgent: navigator.userAgent,
      screenWidth: window.innerWidth,
      screenHeight: window.innerHeight,
      touchSupport: 'ontouchstart' in window,
    };
  });
  console.log('设备信息:', deviceInfo);
  
  // 检查Vue组件props
  const vueApp = await page.evaluate(() => {
    // 尝试访问Vue组件实例
    const app = document.querySelector('#app');
    return app ? app.__vue_app__ : null;
  });
  console.log('Vue应用:', vueApp ? '存在' : '不存在');
  
  // 检查是否有错误
  const errors = await page.evaluate(() => {
    return window.console.errors || [];
  });
  console.log('控制台错误数量:', errors.length);
});