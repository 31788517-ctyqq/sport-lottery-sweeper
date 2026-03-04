const axios = require('axios');

/**
 * 创建一个新的数据源
 */
async function createNewDataSource() {
  try {
    console.log('🔍 创建一个新的数据源...');
    
    // 准备数据源创建数据 - 使用不同的名称以避免冲突
    const dataSourceData = {
      name: '100球网比赛数据-新',
      type: 'api',
      url: 'https://m.100qiu.com/api/dcListBasic?dateTime=26011',
      config: {
        method: 'GET',
        timeout: 30,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)'
        },
        description: '100球网足球比赛数据API',
        category: 'match_data',
        auto_crawl: true,
        crawl_interval: 300, // 5分钟抓取一次
        priority: 'medium'
      },
      status: true  // 启用状态
    };
    
    console.log('📋 准备创建数据源数据:');
    console.log(JSON.stringify(dataSourceData, null, 2));
    
    // 发送POST请求创建数据源
    console.log('\n--- 正在创建数据源 ---');
    const response = await axios.post('http://localhost:8000/api/v1/admin/sources', dataSourceData);
    
    console.log('✅ 数据源创建成功!');
    console.log('状态码:', response.status);
    console.log('响应数据:', JSON.stringify(response.data, null, 2));
    
    // 验证创建结果
    if (response.data.success) {
      console.log('\n🎉 数据源创建成功！');
      console.log(`ID: ${response.data.data.id}`);
      console.log(`名称: ${response.data.data.name}`);
      console.log(`URL: ${response.data.data.url}`);
      
      // 再次获取数据源列表，确认新创建的数据源已存在
      console.log('\n--- 验证数据源是否已添加 ---');
      const listResponse = await axios.get('http://localhost:8000/api/v1/admin/sources');
      if (listResponse.data.success) {
        const sources = listResponse.data.data.items;
        const newSource = sources.find(src => src.id === response.data.data.id);
        if (newSource) {
          console.log(`✅ 新数据源已成功添加到列表中: ${newSource.name}`);
        } else {
          console.log('⚠️ 新数据源未在列表中找到');
        }
      }
    } else {
      console.log('❌ 数据源创建失败');
    }
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ 无法连接到后端服务，请确保后端服务(http://localhost:8000)正在运行');
    } else {
      console.log('❌ 创建数据源失败:', error.message);
      if (error.response) {
        console.log('状态码:', error.response.status);
        console.log('响应数据:', error.response.data);
      }
    }
  }
}

// 运行创建脚本
createNewDataSource();