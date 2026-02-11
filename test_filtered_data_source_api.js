const axios = require('axios');

/**
 * 测试带筛选参数的数据源API
 */
async function testFilteredDataSourceAPI() {
  console.log('🔍 测试不同参数下的数据源API响应');

  // 测试1: 不带任何筛选参数
  console.log('\n--- 测试1: 不带筛选参数 ---');
  try {
    const response = await axios.get('http://localhost:8000/api/v1/admin/sources?page=1&size=20');
    console.log('状态码:', response.status);
    console.log('返回数据源数量:', response.data.data?.items?.length || 0);
  } catch (error) {
    console.log('❌ 请求失败:', error.message);
  }

  // 测试2: 带category参数（这可能是前端实际发送的）
  console.log('\n--- 测试2: 带category参数 (category=match_data) ---');
  try {
    const response = await axios.get('http://localhost:8000/api/v1/admin/sources?page=1&size=20&type=match_data');
    console.log('状态码:', response.status);
    console.log('返回数据源数量:', response.data.data?.items?.length || 0);
  } catch (error) {
    console.log('❌ 请求失败:', error.message);
  }

  // 测试3: 带status参数
  console.log('\n--- 测试3: 带status参数 (status=online) ---');
  try {
    const response = await axios.get('http://localhost:8000/api/v1/admin/sources?page=1&size=20&status=online');
    console.log('状态码:', response.status);
    console.log('返回数据源数量:', response.data.data?.items?.length || 0);
  } catch (error) {
    console.log('❌ 请求失败:', error.message);
  }

  // 测试4: 模拟前端发送的完整参数
  console.log('\n--- 测试4: 模拟前端完整参数 ---');
  try {
    const params = new URLSearchParams({
      page: 1,
      size: 20,
      type: '', // 前端映射的category，可能为空字符串
      search: '', // 前端映射的name，可能为空字符串
      status: '' // 前端的status，可能为空字符串
    }).toString();
    
    const response = await axios.get(`http://localhost:8000/api/v1/admin/sources?${params}`);
    console.log('状态码:', response.status);
    console.log('返回数据源数量:', response.data.data?.items?.length || 0);
  } catch (error) {
    console.log('❌ 请求失败:', error.message);
  }

  console.log('\n💡 提示：如果带参数的请求返回0个数据源，可能是因为后端对空字符串参数进行了错误处理');
}

// 运行测试
testFilteredDataSourceAPI();