// 快速测试 SP API 连通性的脚本
const axios = require('axios');

const BASE_URL = 'http://localhost:8001';
const APIS_TO_TEST = [
  '/admin/sp/data-sources',
  '/admin/sp/matches', 
  '/admin/sp/records',
  '/admin/sp/analysis/distribution'
];

async function testApiConnectivity() {
  console.log('🔍 测试 SP 管理模块 API 连通性...\n');
  
  for (const endpoint of APIS_TO_TEST) {
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`, { timeout: 5000 });
      console.log(`✅ ${endpoint} - 状态码: ${response.status}`);
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.log(`❌ ${endpoint} - 连接被拒绝，后端服务未启动`);
      } else if (error.response) {
        console.log(`⚠️  ${endpoint} - 状态码: ${error.response.status} (接口存在但可能无权限)`);
      } else {
        console.log(`❌ ${endpoint} - 错误: ${error.message}`);
      }
    }
  }
  
  console.log('\n📋 测试完成。如果所有接口都返回状态码 200 或 401/403，说明前后端连通正常。');
}

// 如果没有安装 axios，先运行: npm install axios
// 然后运行: node test_sp_api_connectivity.js
testApiConnectivity();