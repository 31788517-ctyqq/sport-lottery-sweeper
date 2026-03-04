const axios = require('axios');

/**
 * 测试爬虫任务API的脚本
 */
async function testTaskAPI() {
  try {
    console.log('🔍 测试爬虫任务API...');
    
    // 测试获取任务列表
    console.log('\n--- 测试获取任务列表 ---');
    const response = await axios.get('http://localhost:8000/api/v1/admin/tasks');
    
    console.log('✅ 成功连接到任务API');
    console.log('状态码:', response.status);
    console.log('响应数据:', JSON.stringify(response.data, null, 2));
    
    // 检查数据结构
    if (response.data && response.data.data && response.data.data.items) {
      console.log('\n📊 爬虫任务列表:');
      response.data.data.items.forEach((task, index) => {
        console.log(`${index + 1}. ID: ${task.id}, 名称: ${task.name}, 源ID: ${task.source_id}, 状态: ${task.status}`);
      });
      
      console.log(`\n📈 总共找到 ${response.data.data.items.length} 个任务`);
      console.log(`总记录数: ${response.data.data.total}`);
    } else {
      console.log('⚠️ 响应数据格式不符合预期');
    }
    
    // 测试获取统计信息
    console.log('\n--- 测试获取统计信息 ---');
    const statsResponse = await axios.get('http://localhost:8000/api/v1/admin/tasks/statistics');
    console.log('统计信息:', JSON.stringify(statsResponse.data, null, 2));
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ 无法连接到后端服务，请确保后端服务(http://localhost:8000)正在运行');
    } else {
      console.log('❌ API请求失败:', error.message);
      if (error.response) {
        console.log('状态码:', error.response.status);
        console.log('响应数据:', error.response.data);
      }
    }
  }
}

// 运行测试
testTaskAPI();