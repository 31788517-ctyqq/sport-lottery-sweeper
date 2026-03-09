/**
 * 任务控制台页面端到端测试
 * 测试任务创建、显示、编辑和删除功能
 */

const { chromium } = require('playwright');

// 测试配置
const BASE_URL = 'http://localhost:3001';
const ADMIN_PATH = '/admin/data-source/task-console';
const BACKEND_BASE_URL = 'http://localhost:8001';

async function runCompleteTest() {
  console.log('开始任务控制台端到端测试...');
  
  // 启动浏览器
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // 测试1: 页面加载和基础功能验证
    console.log('\n1. 测试页面加载和基础功能...');
    await page.goto(`${BASE_URL}${ADMIN_PATH}`);
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题
    const title = await page.textContent('h2');
    console.assert(title.includes('任务控制台'), '页面标题应为"任务控制台"');
    console.log('✅ 页面加载成功');
    
    // 记录初始任务数量
    const initialTaskCount = await page.locator('.el-table__row').count();
    console.log(`   初始任务数量: ${initialTaskCount}`);
    
    // 测试2: 创建新任务
    console.log('\n2. 测试任务创建...');
    await page.click('button:has-text("新建任务")');
    await page.waitForSelector('text=新建任务', { state: 'visible' });
    
    // 生成唯一任务名称
    const taskName = `测试任务-${Date.now()}`;
    const sourceId = `TS${Date.now()}`;
    
    // 填写表单
    await page.fill('input[placeholder="请输入任务名称"]', taskName);
    await page.click('.el-select[placeholder="请选择任务类型"]');
    await page.click('text=数据采集');
    await page.fill('input[placeholder="请输入数据源源ID，如：DS001"]', sourceId);
    await page.fill('input[placeholder="请输入Cron表达式，例如：0 * * * *"]', '0 * * * *');
    
    // 提交表单
    await page.click('button:has-text("创建")');
    await page.waitForSelector('text=任务创建成功', { timeout: 10000 });
    
    // 关闭对话框
    await page.click('[aria-label="关闭"]');
    
    // 等待页面刷新
    await page.waitForTimeout(1000);
    
    // 验证任务是否出现在列表中（渲染层验证）
    const newTaskCount = await page.locator('.el-table__row').count();
    console.assert(newTaskCount === initialTaskCount + 1, '任务数量应增加1');
    console.log('✅ 任务创建成功');
    
    // 验证新任务的名称是否正确显示
    const taskCells = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
    const taskExists = taskCells.some(cell => cell.includes(taskName));
    console.assert(taskExists, `任务列表中应包含 "${taskName}"`);
    console.log(`✅ 新任务 "${taskName}" 在列表中显示正确`);
    
    // 测试3: 数据层验证 - 通过API验证任务是否真正保存
    console.log('\n3. 测试数据层验证...');
    
    // 通过API获取任务列表
    const apiResponse = await page.request.get(`${BACKEND_BASE_URL}/api/v1/admin/tasks?page=1&size=100`);
    const apiData = await apiResponse.json();
    
    // 检查API返回的数据中是否包含刚才创建的任务
    const apiTasks = Array.isArray(apiData.items) ? apiData.items : (Array.isArray(apiData.data?.items) ? apiData.data.items : []);
    const apiTaskExists = apiTasks.some(task => task.name === taskName);
    
    console.assert(apiTaskExists, `API返回的数据中应包含 "${taskName}"`);
    console.log('✅ 数据层验证通过，任务已保存到数据库');
    
    // 测试4: 网络层验证 - 检查API请求
    console.log('\n4. 测试网络层交互...');
    
    // 监听网络请求
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('/api/v1/admin/tasks')) {
        requests.push({
          method: request.method(),
          url: request.url(),
          postData: request.postData()
        });
      }
    });
    
    // 执行刷新操作
    await page.click('button:has-text("刷新")');
    await page.waitForTimeout(1000);
    
    // 检查是否有正确的API请求
    const hasGetRequest = requests.some(req => req.method === 'GET' && req.url.includes('/api/v1/admin/tasks'));
    console.assert(hasGetRequest, '应发起获取任务列表的GET请求');
    console.log('✅ 网络层交互正常');
    
    // 测试5: 编辑功能验证
    console.log('\n5. 测试任务编辑功能...');
    
    // 找到刚刚创建的任务并点击编辑
    const taskRows = await page.locator('.el-table__row').all();
    let targetRow = null;
    for (const row of taskRows) {
      const nameCell = await row.locator('td:nth-child(3)').textContent();
      if (nameCell.includes(taskName)) {
        targetRow = row;
        break;
      }
    }
    
    if (targetRow) {
      const editButton = targetRow.locator('button:has-text("编辑")');
      await editButton.waitFor({ state: 'attached' });
      await editButton.click();
      
      await page.waitForSelector('text=编辑任务', { state: 'visible' });
      
      // 修改任务名称
      const updatedTaskName = `已更新-${taskName}`;
      await page.fill('input[placeholder="请输入任务名称"]', updatedTaskName);
      
      // 提交修改
      await page.click('button:has-text("更新")');
      await page.waitForSelector('text=任务更新成功', { timeout: 10000 });
      
      // 关闭对话框
      await page.click('[aria-label="关闭"]');
      await page.waitForTimeout(1000);
      
      // 验证任务名称已更新
      const updatedTaskCells = await page.locator('.el-table__row td:nth-child(3)').allInnerTexts();
      const updatedTaskExists = updatedTaskCells.some(cell => cell.includes(updatedTaskName));
      console.assert(updatedTaskExists, `任务列表中应包含 "${updatedTaskName}"`);
      console.log(`✅ 任务已成功更新为 "${updatedTaskName}"`);
      
      // 验证API中任务也已更新
      const updatedApiResponse = await page.request.get(`${BACKEND_BASE_URL}/api/v1/admin/tasks?page=1&size=100`);
      const updatedApiData = await updatedApiResponse.json();
      const updatedApiTasks = Array.isArray(updatedApiData.items) ? updatedApiData.items : 
                               (Array.isArray(updatedApiData.data?.items) ? updatedApiData.data.items : []);
      const updatedApiTaskExists = updatedApiTasks.some(task => task.name === updatedTaskName);
      console.assert(updatedApiTaskExists, `API返回的数据中应包含 "${updatedTaskName}"`);
      console.log('✅ API数据层验证通过，任务已更新到数据库');
    }
    
    // 测试6: 删除功能验证
    console.log('\n6. 测试任务删除功能...');
    
    const beforeDeleteCount = await page.locator('.el-table__row').count();
    console.log(`   删除前任务数量: ${beforeDeleteCount}`);
    
    // 找到刚更新的任务并删除
    const deleteTaskRows = await page.locator('.el-table__row').all();
    let deleteTargetRow = null;
    for (const row of deleteTaskRows) {
      const nameCell = await row.locator('td:nth-child(3)').textContent();
      if (nameCell.includes('已更新')) {
        deleteTargetRow = row;
        break;
      }
    }
    
    if (deleteTargetRow) {
      const deleteButton = deleteTargetRow.locator('button:has-text("删除")');
      await deleteButton.waitFor({ state: 'attached' });
      await deleteButton.click();
      
      await page.waitForSelector('text=确定要删除', { timeout: 5000 });
      await page.click('button:has-text("确定")');
      
      await page.waitForSelector('text=任务删除成功', { timeout: 10000 });
      await page.waitForTimeout(1000);
      
      // 验证任务数量减少
      const afterDeleteCount = await page.locator('.el-table__row').count();
      console.assert(afterDeleteCount === beforeDeleteCount - 1, '任务数量应减少1');
      console.log('✅ 任务删除成功');
      
      // 验证API中任务也被删除
      const afterDeleteApiResponse = await page.request.get(`${BACKEND_BASE_URL}/api/v1/admin/tasks?page=1&size=100`);
      const afterDeleteApiData = await afterDeleteApiResponse.json();
      const afterDeleteApiTasks = Array.isArray(afterDeleteApiData.items) ? afterDeleteApiData.items : 
                                    (Array.isArray(afterDeleteApiData.data?.items) ? afterDeleteApiData.data.items : []);
      const stillExists = afterDeleteApiTasks.some(task => task.name.includes('已更新'));
      console.assert(!stillExists, 'API返回的数据中不应再包含已删除的任务');
      console.log('✅ 数据层验证通过，任务已从数据库删除');
    }
    
    // 测试7: 统计数据验证
    console.log('\n7. 测试统计数据准确性...');
    
    // 获取页面上的统计数字
    const totalTasksText = await page.textContent('.stat-card .el-statistic__content');
    const totalTasksMatch = totalTasksText ? totalTasksText.match(/\d+/) : null;
    const displayedTotal = totalTasksMatch ? parseInt(totalTasksMatch[0]) : 0;
    
    // 获取API中的统计数字
    const statsResponse = await page.request.get(`${BACKEND_BASE_URL}/api/v1/admin/tasks/statistics`);
    const statsData = await statsResponse.json();
    const apiTotal = statsData.data?.totalTasks || statsData.totalTasks || 0;
    
    console.assert(displayedTotal === apiTotal, `页面显示的总数(${displayedTotal})应与API返回的总数(${apiTotal})一致`);
    console.log(`✅ 统计数据显示正确，总数: ${displayedTotal}`);
    
    console.log('\n🎉 所有测试通过！');
    
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

// 执行测试
if (require.main === module) {
  runCompleteTest()
    .then(() => console.log('\n✅ 端到端测试完成'))
    .catch(error => {
      console.error('\n❌ 测试执行失败:', error);
      process.exit(1);
    });
}

module.exports = { runCompleteTest };