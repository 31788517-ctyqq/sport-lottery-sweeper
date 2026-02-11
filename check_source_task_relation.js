const axios = require('axios');

/**
 * 检查数据源和任务的关联关系
 */
async function checkSourceTaskRelation() {
  try {
    console.log('🔍 检查数据源和任务的关联关系...');
    
    // 获取数据源列表
    console.log('\n--- 获取数据源列表 ---');
    const sourcesResponse = await axios.get('http://localhost:8000/api/v1/admin/sources');
    
    if (sourcesResponse.data.success) {
      const sources = sourcesResponse.data.data.items;
      console.log(`总共找到 ${sources.length} 个数据源:`);
      
      // 查找我们创建的数据源
      const ourSource = sources.find(src => src.name.includes('100球网比赛数据'));
      if (ourSource) {
        console.log(`\n✅ 找到我们的数据源:`);
        console.log(`ID: ${ourSource.id}`);
        console.log(`名称: ${ourSource.name}`);
        console.log(`URL: ${ourSource.url}`);
        console.log(`源ID字段: ${ourSource.source_id || '无此字段'}`);
      } else {
        console.log('\n❌ 未找到包含"100球网比赛数据"的数据源');
      }
      
      // 显示所有数据源的基本信息
      console.log('\n📋 所有数据源概览:');
      sources.forEach(src => {
        console.log(`  ID: ${src.id}, 名称: ${src.name}, URL: ${src.url}`);
      });
    }
    
    // 获取任务列表
    console.log('\n--- 获取任务列表 ---');
    const tasksResponse = await axios.get('http://localhost:8000/api/v1/admin/tasks');
    
    if (tasksResponse.data.success) {
      const tasks = tasksResponse.data.data.items;
      console.log(`总共找到 ${tasks.length} 个任务:`);
      
      if (tasks.length > 0) {
        tasks.forEach(task => {
          console.log(`\n任务ID: ${task.id}`);
          console.log(`  名称: ${task.name}`);
          console.log(`  源ID: ${task.source_id}`);  // 这是关联的数据源ID
          console.log(`  状态: ${task.status}`);
          console.log(`  类型: ${task.task_type}`);
        });
        
        // 检查是否有关联到我们数据源的任务
        const relatedTask = tasks.find(task => task.source_id === 8); // 我们创建的数据源ID为8
        if (relatedTask) {
          console.log(`\n✅ 找到关联到数据源ID 8 的任务:`);
          console.log(`  任务名称: ${relatedTask.name}`);
          console.log(`  任务ID: ${relatedTask.id}`);
        } else {
          console.log(`\n❌ 未找到关联到数据源ID 8 的任务`);
        }
      } else {
        console.log('  没有任何任务');
      }
    }
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ 无法连接到后端服务，请确保后端服务(http://localhost:8000)正在运行');
    } else {
      console.log('❌ 检查失败:', error.message);
      if (error.response) {
        console.log('状态码:', error.response.status);
        console.log('响应数据:', error.response.data);
      }
    }
  }
}

// 运行检查脚本
checkSourceTaskRelation();