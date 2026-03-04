/**
 * 测试移动端页面加载和渲染
 */

const puppeteer = require('puppeteer');

async function testMobilePage() {
  console.log('开始测试移动端页面...');
  
  let browser;
  try {
    // 启动浏览器
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // 设置移动端视口
    await page.setViewport({
      width: 375,
      height: 667,
      isMobile: true,
      hasTouch: true,
      deviceScaleFactor: 2
    });
    
    // 设置用户代理为移动设备
    await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1');
    
    // 导航到移动端页面
    console.log('导航到 http://localhost:3000/m/beidan-filter ...');
    const response = await page.goto('http://localhost:3000/m/beidan-filter', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    
    console.log(`页面状态: ${response.status()}`);
    
    // 等待页面加载
    await page.waitForSelector('#app', { timeout: 10000 });
    console.log('应用容器加载完成');
    
    // 检查移动端布局元素
    const hasMobileLayout = await page.evaluate(() => {
      const wrapper = document.querySelector('.mobile-layout-wrapper');
      const mobileLayout = document.querySelector('.mobile-layout');
      const desktopLayout = document.querySelector('.desktop-layout');
      
      return {
        hasWrapper: !!wrapper,
        hasMobileLayout: !!mobileLayout,
        hasDesktopLayout: !!desktopLayout,
        wrapperClass: wrapper ? wrapper.className : '未找到',
        isMobileLayoutVisible: mobileLayout ? window.getComputedStyle(mobileLayout).display !== 'none' : false,
        isDesktopLayoutVisible: desktopLayout ? window.getComputedStyle(desktopLayout).display !== 'none' : false
      };
    });
    
    console.log('移动端布局检查结果:');
    console.log(`- 是否有移动端布局包装器: ${hasMobileLayout.hasWrapper}`);
    console.log(`- 是否有移动端布局元素: ${hasMobileLayout.hasMobileLayout}`);
    console.log(`- 是否有桌面端布局元素: ${hasMobileLayout.hasDesktopLayout}`);
    console.log(`- 包装器类名: ${hasMobileLayout.wrapperClass}`);
    console.log(`- 移动端布局是否可见: ${hasMobileLayout.isMobileLayoutVisible}`);
    console.log(`- 桌面端布局是否可见: ${hasMobileLayout.isDesktopLayoutVisible}`);
    
    // 检查控制台日志
    const consoleLogs = [];
    page.on('console', msg => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });
    
    // 检查页面标题
    const pageTitle = await page.title();
    console.log(`页面标题: ${pageTitle}`);
    
    // 检查是否有错误
    const errors = [];
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    // 等待一段时间让页面完全渲染
    await page.waitForTimeout(2000);
    
    // 检查移动端子组件
    const hasMobileComponents = await page.evaluate(() => {
      // 检查移动端子组件是否存在
      const components = [
        '.mobile-header',
        '.mobile-main',
        '.mobile-nav-bar',
        '.filter-section-mobile',
        '.results-section-mobile',
        '.strategy-section-mobile',
        '.stats-card-mobile',
        '.export-section-mobile'
      ];
      
      const results = {};
      components.forEach(selector => {
        results[selector] = !!document.querySelector(selector);
      });
      
      return results;
    });
    
    console.log('移动端子组件检查结果:');
    Object.entries(hasMobileComponents).forEach(([selector, exists]) => {
      console.log(`- ${selector}: ${exists ? '存在' : '不存在'}`);
    });
    
    // 输出控制台日志
    console.log('\n控制台日志:');
    consoleLogs.forEach(log => {
      console.log(`  [${log.type}] ${log.text}`);
    });
    
    // 输出错误
    if (errors.length > 0) {
      console.log('\n页面错误:');
      errors.forEach(error => console.log(`  ${error}`));
    }
    
    // 截图保存
    await page.screenshot({ path: 'mobile_page_test.png', fullPage: true });
    console.log('截图已保存为 mobile_page_test.png');
    
    // 评估测试结果
    const testPassed = hasMobileLayout.hasMobileLayout && hasMobileLayout.isMobileLayoutVisible;
    
    if (testPassed) {
      console.log('\n✅ 测试通过: 移动端布局正确渲染');
    } else {
      console.log('\n❌ 测试失败: 移动端布局未正确渲染');
      console.log('可能的原因:');
      console.log('1. MobileLayoutWrapper 组件未正确识别移动端模式');
      console.log('2. 设备检测逻辑有问题');
      console.log('3. 移动端子组件未正确导入或渲染');
    }
    
    return testPassed;
    
  } catch (error) {
    console.error('测试过程中发生错误:', error);
    return false;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// 运行测试
testMobilePage().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('测试执行失败:', error);
  process.exit(1);
});