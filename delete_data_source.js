const axios = require('axios');

/**
 * 删除指定的数据源
 */
async function deleteDataSource() {
  try {
    console.log('🔍 查找并删除"100球网比赛数据"数据源...');
    
    // 首先获取数据源列表
    console.log('\n--- 获取数据源列表 ---');
    const listResponse = await axios.get('http://localhost:8000/api/v1/admin/sources');
    
    if (listResponse.data.success) {
      const sources = listResponse.data.data.items;
      const targetSource = sources.find(src => src.name === '100球网比赛数据');
      
      if (targetSource) {
        console.log(`✅ 找到目标数据源: ID ${targetSource.id}, 名称: ${targetSource.name}`);
        
        // 删除数据源
        console.log(`\n--- 正在删除数据源 ID: ${targetSource.id} ---`);
        const deleteResponse = await axios.delete(`http://localhost:8000/api/v1/admin/sources/${targetSource.id}`);
        
        if (deleteResponse.data.success) {
          console.log('✅ 数据源删除成功!');
          console.log('响应数据:', JSON.stringify(deleteResponse.data, null, 2));
          
          // 验证数据源是否真的被删除
          console.log('\n--- 验证数据源是否已删除 ---');
          const verifyResponse = await axios.get('http://localhost:8000/api/v1/admin/sources');
          if (verifyResponse.data.success) {
            const remainingSources = verifyResponse.data.data.items;
            const stillExists = remainingSources.some(src => src.id === targetSource.id);
            
            if (!stillExists) {
              console.log(`✅ 数据源 ID ${targetSource.id} 已从列表中移除，验证成功！`);
            } else {
              console.log(`⚠️ 数据源 ID ${targetSource.id} 仍存在于列表中`);
            }
          }
        } else {
          console.log('❌ 数据源删除失败');
          console.log('响应数据:', JSON.stringify(deleteResponse.data, null, 2));
        }
      } else {
        console.log('⚠️ 未找到名为"100球网比赛数据"的数据源');
        
        // 显示所有数据源供参考
        console.log('\n📋 当前所有数据源:');
        sources.forEach(src => {
          console.log(`  ID: ${src.id}, 名称: ${src.name}`);
        });
      }
    } else {
      console.log('❌ 获取数据源列表失败');
    }
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ 无法连接到后端服务，请确保后端服务(http://localhost:8000)正在运行');
    } else {
      console.log('❌ 操作失败:', error.message);
      if (error.response) {
        console.log('状态码:', error.response.status);
        console.log('响应数据:', error.response.data);
      }
    }
  }
}

// 运行删除脚本
deleteDataSource();