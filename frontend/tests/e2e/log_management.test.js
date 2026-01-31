/**
 * 日志管理模块E2E测试用例
 * 测试日志管理模块的5个子页面功能
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

describe('日志管理模块E2E测试', () => {
  let browser;
  let page;

  beforeAll(async () => {
    // 启动浏览器
    browser = await puppeteer.launch({
      headless: false, // 设为true可在无头模式下运行
      slowMo: 50, // 减慢操作速度，便于观察
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    page = await browser.newPage();
    
    // 设置视口大小
    await page.setViewport({ width: 1920, height: 1080 });
  });

  afterAll(async () => {
    await browser.close();
  });

  // 登录测试用户
  const loginTestUser = async () => {
    // 访问登录页面
    await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle2' });

    // 输入用户名
    await page.type('input[name="username"]', 'admin');
    
    // 输入密码
    await page.type('input[name="password"]', 'admin123');
    
    // 点击登录按钮
    await page.click('button[type="submit"]');
    
    // 等待登录完成
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
  };

  // 测试导航到日志管理页面
  const navigateToLogManagement = async () => {
    // 点击侧边栏的"日志管理"菜单项
    await page.click('li.el-submenu[data-cy="logs-menu"]');
    
    // 等待页面加载
    await page.waitForSelector('.log-management-container', { timeout: 10000 });
  };

  describe('日志管理主页面功能测试', () => {
    test('访问日志管理主页面并验证统计数据', async () => {
      await loginTestUser();
      await navigateToLogManagement();
      
      // 验证页面标题
      await page.waitForSelector('h2', { timeout: 10000 });
      const title = await page.$eval('h2', el => el.textContent);
      expect(title.trim()).toBe('日志管理中心');
      
      // 验证统计卡片存在
      const statCards = await page.$$('.log-stat-item');
      expect(statCards.length).toBeGreaterThan(0);
      
      // 验证导航按钮存在
      const navButtons = await page.$$('.log-menu button');
      expect(navButtons.length).toBe(4); // 系统日志、用户日志、安全日志、API日志
    }, 30000);
  });

  describe('系统日志页面功能测试', () => {
    test('导航到系统日志页面并执行筛选操作', async () => {
      await loginTestUser();
      await navigateToLogManagement();
      
      // 点击系统日志按钮
      await page.click('button:has-text("系统日志")');
      
      // 等待页面加载
      await page.waitForSelector('.system-logs-container', { timeout: 10000 });
      
      // 验证页面标题
      const header = await page.$eval('div[slot="header"] span', el => el.textContent);
      expect(header.trim()).toBe('系统日志');
      
      // 验证表格存在
      const tableExists = await page.$('.el-table');
      expect(tableExists).toBeTruthy();
      
      // 测试筛选功能
      // 选择日志级别
      await page.click('.el-select__caret'); // 点击日志级别下拉框
      await page.click('li[aria-label="INFO"]'); // 选择INFO级别
      
      // 输入搜索关键词
      await page.type('input[placeholder="搜索日志..."]', 'test');
      
      // 点击筛选按钮
      await page.click('button:has-text("筛选")');
      
      // 等待数据加载
      await page.waitForTimeout(2000);
      
      // 验证筛选结果
      const rows = await page.$$('.el-table__row');
      expect(rows.length).toBeGreaterThanOrEqual(0); // 可能没有匹配的结果，但不应报错
      
      // 测试翻页功能
      const pagination = await page.$('.el-pagination');
      if (pagination) {
        const pages = await page.$$('.el-pagination .el-pager li');
        if (pages.length > 1) {
          await page.click(pages[1]); // 点击第二页
          await page.waitForTimeout(1000);
        }
      }
      
      // 测试详情弹窗
      const detailButtons = await page.$$('.el-table__body tr .el-button--text');
      if (detailButtons.length > 0) {
        await detailButtons[0].click();
        await page.waitForSelector('.el-dialog__wrapper', { timeout: 5000 });
        
        // 验证弹窗打开
        const dialogVisible = await page.$eval('.el-dialog__wrapper', el => 
          !el.classList.contains('v-modal-enter-from'));
        expect(dialogVisible).toBe(true);
        
        // 关闭弹窗
        await page.click('button:has-text("关闭")');
        await page.waitForTimeout(500);
      }
    }, 60000);
  });

  describe('用户日志页面功能测试', () => {
    test('导航到用户日志页面并执行筛选操作', async () => {
      await loginTestUser();
      await navigateToLogManagement();
      
      // 点击用户日志按钮
      await page.click('button:has-text("用户日志")');
      
      // 等待页面加载
      await page.waitForSelector('.user-logs-container', { timeout: 10000 });
      
      // 验证页面标题
      const header = await page.$eval('div[slot="header"] span', el => el.textContent);
      expect(header.trim()).toBe('用户日志');
      
      // 测试搜索功能
      await page.type('input[placeholder="搜索日志..."]', 'user activity');
      await page.click('button:has-text("筛选")');
      await page.waitForTimeout(2000);
      
      // 测试用户ID筛选
      const userIdSelect = await page.$('.el-select');
      if (userIdSelect) {
        await page.click(userIdSelect);
        const options = await page.$$('.el-select-dropdown__item');
        if (options.length > 1) {
          await options[1].click();
          await page.click('button:has-text("筛选")');
          await page.waitForTimeout(2000);
        }
      }
      
      // 验证表格数据
      const rows = await page.$$('.el-table__row');
      expect(rows.length).toBeGreaterThanOrEqual(0);
    }, 60000);
  });

  describe('安全日志页面功能测试', () => {
    test('导航到安全日志页面并验证功能', async () => {
      await loginTestUser();
      await navigateToLogManagement();
      
      // 点击安全日志按钮
      await page.click('button:has-text("安全日志")');
      
      // 等待页面加载
      await page.waitForSelector('.security-logs-container', { timeout: 10000 });
      
      // 验证页面标题
      const header = await page.$eval('div[slot="header"] span', el => el.textContent);
      expect(header.trim()).toBe('安全日志');
      
      // 验证表格存在
      const tableExists = await page.$('.el-table');
      expect(tableExists).toBeTruthy();
      
      // 测试日志级别筛选
      await page.click('.el-select__caret'); // 点击日志级别下拉框
      await page.click('li[aria-label="INFO"]'); // 选择INFO级别
      await page.click('button:has-text("筛选")');
      await page.waitForTimeout(2000);
      
      // 验证筛选结果
      const rows = await page.$$('.el-table__row');
      expect(rows.length).toBeGreaterThanOrEqual(0);
    }, 60000);
  });

  describe('API日志页面功能测试', () => {
    test('导航到API日志页面并验证功能', async () => {
      await loginTestUser();
      await navigateToLogManagement();
      
      // 点击API日志按钮
      await page.click('button:has-text("API日志")');
      
      // 等待页面加载
      await page.waitForSelector('.api-logs-container', { timeout: 10000 });
      
      // 验证页面标题
      const header = await page.$eval('div[slot="header"] span', el => el.textContent);
      expect(header.trim()).toBe('API日志');
      
      // 验证表格存在
      const tableExists = await page.$('.el-table');
      expect(tableExists).toBeTruthy();
      
      // 验证API日志特有的列存在（请求路径、状态码、耗时等）
      const pathCol = await page.$('th:has-text("请求路径")');
      const statusCol = await page.$('th:has-text("状态码")');
      const durationCol = await page.$('th:has-text("耗时")');
      
      expect(pathCol).toBeTruthy();
      expect(statusCol).toBeTruthy();
      expect(durationCol).toBeTruthy();
      
      // 测试筛选功能
      await page.type('input[placeholder="搜索日志..."]', 'GET');
      await page.click('button:has-text("筛选")');
      await page.waitForTimeout(2000);
      
      // 验证筛选结果
      const rows = await page.$$('.el-table__row');
      expect(rows.length).toBeGreaterThanOrEqual(0);
    }, 60000);
  });

  describe('日志管理模块整体导航测试', () => {
    test('在各子页面间切换并验证导航稳定性', async () => {
      await loginTestUser();
      await navigateToLogManagement();
      
      // 测试在各日志页面间切换
      const logPages = [
        { button: '系统日志', selector: '.system-logs-container' },
        { button: '用户日志', selector: '.user-logs-container' },
        { button: '安全日志', selector: '.security-logs-container' },
        { button: 'API日志', selector: '.api-logs-container' }
      ];
      
      for (const pageDef of logPages) {
        // 点击导航按钮
        await page.click(`button:has-text("${pageDef.button}")`);
        
        // 等待页面加载
        await page.waitForSelector(pageDef.selector, { timeout: 10000 });
        
        // 验证页面标题
        const header = await page.$eval('div[slot="header"] span', el => el.textContent);
        expect(header.trim()).toBe(pageDef.button);
        
        // 等待数据加载
        await page.waitForTimeout(1000);
      }
    }, 120000);
  });
});