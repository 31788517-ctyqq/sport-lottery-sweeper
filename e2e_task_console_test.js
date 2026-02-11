/**
 * 任务控制台页面端到端测试
 * 测试任务创建、显示、编辑和删除功能
 */

const { chromium } = require('playwright');

// 测试配置
const BASE_URL = 'http://localhost:3001';
const ADMIN_PATH = '/admin/data-source/task-console';
const BACKEND_BASE_URL = 'http://localhost:8001';

describe('任务控制台页面端到端测试', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await chromium.launch({ headless: false });
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  beforeEach(async () => {
    // 确保页面加载完成
    await page.goto(`${BASE_URL}${ADMIN_PATH}`);
    await page.waitForLoadState('networkidle');
  });

  test('任务创建和显示测试', async () => {
    // 网络层测试：确保页面能正常加载
    const response = await page.goto(`${BASE_URL}${ADMIN_PATH}`);
    expect(response.status()).toBeLessThan(400);

    // 检查页面标题
    await expect(page.locator('h2')).toContainText('任务控制台');

    // 记录初始任务数量
    const initialTaskCount = await page.locator('.el-table__row').count();

    // 点击新建任务按钮
    await page.click('button:has-text("新建任务")');
    
    // 等待对话框出现
    await page.waitForSelector('text=新建任务', { state: 'visible' });

    // 填写表单
    const taskName = `测试任务-${Date.now()}`;
    await page.fill('input[placeholder="请输入任务名称"]', taskName);
    
    // 选择任务类型
    await page.click('.el-select[placeholder="请选择任务类型"]');
    await page.click('text=数据采集');
    
    // 填写源ID
    await page.fill('input[placeholder="请输入数据源源ID，如：DS001"]', `DS${Date.now()}`);
    
    // 填写Cron表达式
    await page.fill('input[placeholder="请输入Cron表达式，例如：0 * * * *"]', '0 * * * *');
    
    // 提交表单
    await page.click('button:has-text("创建")');
    
    // 等待创建成功消息
    await page.waitForSelector('text=任务创建成功', { timeout: 10000 });
    
    // 关闭对话框
    await page.click('[aria-label="关闭"]');
    
    // 等待页面刷新
    await page.waitForTimeout(1000);
    
    // 检查任务是否出现在列表中（渲染层验证）
    const newTaskCount = await page.locator('.el-table__row').count();
    expect(newTaskCount).toBe(initialTaskCount + 1);
    
    // 验证新任务的名称是否正确显示
    const taskCells = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
    expect(taskCells.some(cell => cell.includes(taskName))).toBeTruthy();
  });

  test('数据层验证 - 通过API验证任务创建', async () => {
    // 创建一个测试任务
    const taskName = `API验证任务-${Date.now()}`;
    const sourceId = `DS${Date.now()}`;
    
    // 准备任务数据
    const taskData = {
      name: taskName,
      source_id: sourceId,
      task_type: 'DATA_COLLECTION',
      cron_expression: '0 * * * *',
      is_active: true,
      config: '{}'
    };
    
    // 通过API创建任务
    const response = await page.request.post(`${BACKEND_BASE_URL}/api/v1/admin/tasks`, {
      data: taskData
    });
    
    expect(response.status()).toBe(200);
    
    // 刷新页面以显示新任务
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 验证任务是否显示在前端
    const taskCells = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
    expect(taskCells.some(cell => cell.includes(taskName))).toBeTruthy();
    
    // 验证源ID是否正确显示
    const sourceIdCells = await page.locator('.el-table__row td:nth-child(5)').allInnerTexts();
    expect(sourceIdCells.some(cell => cell.includes(sourceId))).toBeTruthy();
  });

  test('任务编辑功能测试', async () => {
    // 找到第一个任务并点击编辑
    const firstRow = page.locator('.el-table__row').first();
    await expect(firstRow).toBeVisible();
    
    // 点击第一行的编辑按钮
    const editButton = firstRow.locator('button:has-text("编辑")').first();
    await expect(editButton).toBeEnabled();
    await editButton.click();
    
    // 等待编辑对话框出现
    await page.waitForSelector('text=编辑任务', { state: 'visible' });
    
    // 修改任务名称
    const newName = `修改后的任务-${Date.now()}`;
    await page.fill('input[placeholder="请输入任务名称"]', newName);
    
    // 提交修改
    await page.click('button:has-text("更新")');
    
    // 等待更新成功消息
    await page.waitForSelector('text=任务更新成功', { timeout: 10000 });
    
    // 关闭对话框
    await page.click('[aria-label="关闭"]');
    
    // 等待页面刷新
    await page.waitForTimeout(1000);
    
    // 验证任务名称已更新
    const taskCells = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
    expect(taskCells.some(cell => cell.includes(newName))).toBeTruthy();
  });

  test('任务删除功能测试', async () => {
    // 记录删除前的任务数量
    const beforeDeleteCount = await page.locator('.el-table__row').count();
    
    if (beforeDeleteCount > 0) {
      // 选择第一行任务
      const firstRow = page.locator('.el-table__row').first();
      await expect(firstRow).toBeVisible();
      
      // 点击第一行的删除按钮
      const deleteButton = firstRow.locator('button:has-text("删除")').first();
      await expect(deleteButton).toBeEnabled();
      await deleteButton.click();
      
      // 等待确认对话框出现并确认删除
      await page.waitForSelector('text=确定要删除', { timeout: 5000 });
      await page.click('button:has-text("确定")');
      
      // 等待删除成功消息
      await page.waitForSelector('text=任务删除成功', { timeout: 10000 });
      
      // 等待页面刷新
      await page.waitForTimeout(1000);
      
      // 验证任务数量减少了1
      const afterDeleteCount = await page.locator('.el-table__row').count();
      expect(afterDeleteCount).toBe(beforeDeleteCount - 1);
    }
  });

  test('批量删除功能测试', async () => {
    // 先创建几个测试任务
    const testTasks = [];
    for (let i = 0; i < 3; i++) {
      const taskName = `批量删除测试-${Date.now()}-${i}`;
      const sourceId = `BDS${Date.now()}-${i}`;
      
      const taskData = {
        name: taskName,
        source_id: sourceId,
        task_type: 'DATA_COLLECTION',
        cron_expression: '0 * * * *',
        is_active: true,
        config: '{}'
      };
      
      const response = await page.request.post(`${BACKEND_BASE_URL}/api/v1/admin/tasks`, {
        data: taskData
      });
      
      expect(response.status()).toBe(200);
      testTasks.push(taskName);
    }
    
    // 刷新页面以显示新创建的任务
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 验证所有测试任务都已显示
    for (const taskName of testTasks) {
      const taskCells = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
      expect(taskCells.some(cell => cell.includes(taskName))).toBeTruthy();
    }
    
    // 记录删除前的任务数量
    const beforeBatchDeleteCount = await page.locator('.el-table__row').count();
    
    // 选择前三个任务（如果有足够多的话）
    const checkboxes = page.locator('.el-checkbox__original').nth(0).click();  // 全选
    // 或者逐个选择前三个任务
    const rows = page.locator('.el-table__row');
    const rowCount = await rows.count();
    
    for (let i = 0; i < Math.min(3, rowCount); i++) {
      const checkbox = page.locator('.el-table__row').nth(i).locator('.el-checkbox__original').first();
      await checkbox.click();
    }
    
    // 点击批量删除按钮
    await page.click('button:has-text("批量删除")');
    
    // 确认删除
    await page.waitForSelector('text=确定要删除', { timeout: 5000 });
    await page.click('button:has-text("确定")');
    
    // 等待批量删除成功消息
    await page.waitForSelector('text=批量删除成功', { timeout: 10000 });
    
    // 等待页面刷新
    await page.waitForTimeout(1000);
    
    // 验证任务数量减少了3个
    const afterBatchDeleteCount = await page.locator('.el-table__row').count();
    expect(afterBatchDeleteCount).toBe(beforeBatchDeleteCount - 3);
  });

  test('筛选功能测试', async () => {
    // 创建一个具有特定名称的任务用于测试筛选
    const uniqueTaskName = `筛选测试任务-${Date.now()}`;
    const uniqueSourceId = `ST${Date.now()}`;
    
    const taskData = {
      name: uniqueTaskName,
      source_id: uniqueSourceId,
      task_type: 'DATA_COLLECTION',
      cron_expression: '0 * * * *',
      is_active: true,
      config: '{}'
    };
    
    const response = await page.request.post(`${BACKEND_BASE_URL}/api/v1/admin/tasks`, {
      data: taskData
    });
    
    expect(response.status()).toBe(200);
    
    // 刷新页面
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 在筛选框中输入任务名称
    await page.fill('input[placeholder="请输入任务名称"]', uniqueTaskName);
    
    // 点击查询按钮
    await page.click('button:has-text("查询")');
    
    // 等待筛选结果加载
    await page.waitForTimeout(1000);
    
    // 验证筛选结果只包含匹配的任务
    const taskNames = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
    expect(taskNames.length).toBeGreaterThan(0);
    expect(taskNames.every(name => name.includes(uniqueTaskName))).toBeTruthy();
    
    // 重置筛选条件
    await page.click('button:has-text("重置")');
    await page.waitForTimeout(500);
  });
});

// 如果直接运行此文件，执行测试
if (require.main === module) {
  (async () => {
    try {
      // 检查服务是否可用
      console.log('正在检查前端服务...');
      const { spawn } = require('child_process');
      
      // 启动测试
      console.log('开始执行任务控制台端到端测试...');
      // 这里可以加入实际的Playwright测试执行逻辑
    } catch (error) {
      console.error('测试执行出错:', error);
    }
  })();
}