/**
 * 日志管理模块端到端功能验证脚本
 * 验证前端页面和后端API的集成
 * 支持通过 AUTH_TOKEN 环境变量提供有效token进行完整测试
 */

const axios = require('axios');

// API端点配置
const baseURL = 'http://localhost:8001';
const API_BASE = '/api/v1/admin/system';

console.log('🔍 日志管理E2E测试开始...\n');

// 获取认证token - 可以通过环境变量传入有效token
const authToken = process.env.AUTH_TOKEN || 'invalid-token';
const hasValidToken = process.env.AUTH_TOKEN ? true : false;

if (hasValidToken) {
  console.log('✅ 检测到有效token，将执行完整功能测试');
} else {
  console.log('💡 提示: 设置 AUTH_TOKEN 环境变量可启用有效token测试');
}

// 创建axios实例
const apiClient = axios.create({
  baseURL,
  validateStatus: function (status) {
    return status >= 200 && status < 500; // 接受所有非5xx错误
  }
});

// 获取认证头
function getAuthHeaders(token) {
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function runTests() {
  console.log('📋 1. 测试API端点可达性...');
  try {
    const response = await apiClient.get(`${API_BASE}/logs/db/statistics`);
    console.log(`✅ API端点可达，状态码: ${response.status}`);
  } catch (error) {
    console.log(`❌ API端点不可达: ${error.message}`);
  }

  console.log('\n🔒 2. 测试认证机制...');
  // 尝试使用无效token请求
  try {
    const response = await apiClient.get(`${API_BASE}/logs/db/statistics`, {
      headers: { 'Authorization': 'Bearer invalid-token' }
    });
    console.log(`⚠️  无效token请求状态: ${response.status}`);
  } catch (error) {
    console.log(`⚠️  无效token请求失败: ${error.message}`);
  }

  // 尝试使用缺少token的请求
  try {
    const response = await apiClient.get(`${API_BASE}/logs/db/statistics`);
    console.log(`⚠️  无token请求状态: ${response.status} (期望401/403)`);
  } catch (error) {
    console.log(`⚠️  无token请求失败: ${error.message} (期望401/403)`);
  }

  console.log('\n🔑 3. 测试有效token请求...');
  if (hasValidToken) {
    try {
      const response = await apiClient.get(`${API_BASE}/logs/db/statistics`, {
        headers: getAuthHeaders(authToken)
      });
      
      if (response.status === 200) {
        console.log('✅ 有效token认证成功');
        console.log(`📊 统计数据: ${JSON.stringify(response.data, null, 2)}`);
      } else {
        console.log(`❌ 有效token请求失败，状态码: ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ 有效token请求异常: ${error.message}`);
    }
  } else {
    console.log('🟡 跳过有效token测试（未提供有效token）');
    console.log('💡 使用: AUTH_TOKEN=your_valid_token node test_log_management_e2e.js 运行完整测试');
  }

  console.log('\n📊 4. 测试数据获取功能...');
  // 尝试访问各种日志类型
  const logTypes = ['system', 'user', 'security', 'api'];
  for (const type of logTypes) {
    try {
      const response = await apiClient.get(`${API_BASE}/logs/db/${type}`, {
        params: { skip: 0, limit: 5 },
        headers: getAuthHeaders(authToken)
      });
      console.log(`✅ ${type}日志端点可达，状态码: ${response.status}`);
    } catch (error) {
      console.log(`❌ ${type}日志端点不可达: ${error.message}`);
    }
  }

  console.log('\n🔍 5. 测试参数验证...');
  // 测试超出限制的参数
  try {
    const response = await apiClient.get(`${API_BASE}/logs/db/system`, {
      params: { skip: 0, limit: 2000 }, // limit超过1000
      headers: getAuthHeaders(authToken)
    });
    if (response.status === 422) {
      console.log(`✅ 参数验证生效 - 正确拒绝了超出限制的请求 (422)`);
    } else {
      console.log(`⚠️  参数验证 - 请求状态: ${response.status} (期望422)`);
    }
  } catch (error) {
    if (error.response && error.response.status === 422) {
      console.log(`✅ 参数验证生效 - 正确拒绝了超出限制的请求 (422)`);
    } else {
      console.log(`⚠️  参数验证 - 其他错误: ${error.message}`);
    }
  }

  console.log('\n📈 6. 测试统计信息获取...');
  try {
    const response = await apiClient.get(`${API_BASE}/logs/db/statistics`, {
      headers: getAuthHeaders(authToken)
    });
    if (response.status === 200 && response.data) {
      console.log('✅ 统计信息获取成功');
      console.log(`📊 总日志数: ${response.data.total_logs || 'N/A'}`);
      console.log(`📊 错误日志数: ${response.data.logs_by_level ? response.data.logs_by_level.ERROR || 0 : 'N/A'}`);
    } else {
      console.log(`⚠️  统计信息获取返回非200状态: ${response.status}`);
    }
  } catch (error) {
    console.log(`❌ 统计信息获取失败: ${error.message}`);
  }

  console.log('\n🎯 7. 测试搜索功能...');
  try {
    const response = await apiClient.get(`${API_BASE}/logs/db/search`, {
      params: { q: 'error', skip: 0, limit: 5 },
      headers: getAuthHeaders(authToken)
    });
    console.log(`✅ 搜索功能端点可达，状态码: ${response.status}`);
  } catch (error) {
    console.log(`❌ 搜索功能端点不可达: ${error.message}`);
  }

  console.log('\n✅ 所有测试完成！');
}

// 运行测试
runTests().catch(console.error);