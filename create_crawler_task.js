const axios = require('axios');

/**
 * 为新数据源创建爬虫任务
 */
async function createCrawlerTask() {
  try {
    console.log('🔍 为数据源ID 8创建爬虫任务...');
    
    // 准备爬虫任务数据
    const taskData = {
      name: '100球网比赛数据抓取任务',
      source_id: 8,  // 使用新创建的数据源ID
      task_type: 'crawl',
      cron_expression: '0 */1 * * *',  // 每小时执行一次
      config: JSON.stringify({
        timeout: 30,
        retry_count: 3,
        batch_size: 50,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; DataCrawler/1.0)'
        }
      }),
      is_active: true
    };
    
    console.log('📋 准备创建爬虫任务数据:');
    console.log(JSON.stringify(taskData, null, 2));
    
    // 发送POST请求创建爬虫任务
    console.log('\n--- 正在创建爬虫任务 ---');
    const response = await axios.post('http://localhost:8000/api/v1/admin/tasks', taskData);
    
    console.log('✅ 爬虫任务创建成功!');
    console.log('状态码:', response.status);
    console.log('响应数据:', JSON.stringify(response.data, null, 2));
    
    // 验证创建结果
    if (response.data.success) {
      console.log('\n🎉 爬虫任务创建成功！');
      console.log(`ID: ${response.data.data.id}`);
      console.log(`名称: ${response.data.data.name}`);
      console.log(`源ID: ${response.data.data.source_id}`);
      console.log(`类型: ${response.data.data.task_type}`);
      console.log(`Cron表达式: ${response.data.data.cron_expression}`);
      console.log(`状态: ${response.data.data.status}`);
      
      // 获取任务列表，确认新创建的任务已存在
      console.log('\n--- 验证任务是否已添加到列表 ---');
      const listResponse = await axios.get('http://localhost:8000/api/v1/admin/tasks');
      if (listResponse.data.success) {
        const tasks = listResponse.data.data.items;
        const newTask = tasks.find(t => t.id === response.data.data.id);
        if (newTask) {
          console.log(`✅ 新任务已成功添加到列表中: ${newTask.name}`);
          console.log(`源ID: ${newTask.source_id} (应为8)`);
        } else {
          console.log('⚠️ 新任务未在列表中找到');
        }
      }
    } else {
      console.log('❌ 爬虫任务创建失败');
    }
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ 无法连接到后端服务，请确保后端服务(http://localhost:8000)正在运行');
    } else {
      console.log('❌ 创建爬虫任务失败:', error.message);
      if (error.response) {
        console.log('状态码:', error.response.status);
        console.log('响应数据:', error.response.data);
      }
    }
  }
}

// 运行创建任务脚本
createCrawlerTask();