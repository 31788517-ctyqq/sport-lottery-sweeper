const axios = require('axios');

/**
 * 测试数据源API的脚本
 */
async function testDataSourceAPI() {
  try {
    // 测试后端API
    const response = await axios.get('http://localhost:8000/api/v1/admin/sources');
    
    console.log('✅ 成功连接到数据源API');
    console.log('状态码:', response.status);
    console.log('响应数据:', JSON.stringify(response.data, null, 2));
    
    // 检查数据结构
    if (response.data && response.data.data && response.data.data.items) {
      console.log('\n📊 数据源列表:');
      response.data.data.items.forEach((source, index) => {
        console.log(`${index + 1}. ID: ${source.id}, 名称: ${source.name}, URL: ${source.url}`);
      });
      
      console.log(`\n📈 总共找到 ${response.data.data.items.length} 个数据源`);
      console.log(`总记录数: ${response.data.data.total}`);
    } else {
      console.log('⚠️ 响应数据格式不符合预期');
    }
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
testDataSourceAPI();