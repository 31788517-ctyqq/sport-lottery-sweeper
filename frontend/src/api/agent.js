import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建axios实例用于智能体管理API
const agentApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
});

// 请求拦截器
agentApi.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('admin_token') || localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
agentApi.interceptors.response.use(
  (response) => {
    // 检查响应结构是否符合预期
    if (response.status === 200 || response.status === 201) {
      return response.data;
    } else {
      const errorMessage = response.data?.message || response.data?.detail || '请求失败';
      ElMessage.error(errorMessage);
      return Promise.reject(new Error(errorMessage));
    }
  },
  (error) => {
    console.error('智能体API请求错误:', error);
    
    // 检查是否是认证错误
    if (error.response?.status === 401) {
      // 清除本地token
      localStorage.removeItem('admin_token');
      localStorage.removeItem('auth_token');
      // 重定向到登录页（如果在浏览器环境中）
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.detail || 
                        error.message || 
                        '网络请求失败';
    ElMessage.error(errorMessage);
    return Promise.reject(error);
  }
);

// 智能体模板API
const agentTemplateApi = {
  // 获取模板列表
  getTemplates(params) {
    return agentApi.get('/agents/templates', { params });
  },
  
  // 获取模板详情
  getTemplateById(id) {
    return agentApi.get(`/agents/templates/${id}`);
  },
  
  // 创建模板
  createTemplate(data) {
    return agentApi.post('/agents/templates', data);
  },
  
  // 更新模板
  updateTemplate(id, data) {
    return agentApi.put(`/agents/templates/${id}`, data);
  },
  
  // 删除模板
  deleteTemplate(id) {
    return agentApi.delete(`/agents/templates/${id}`);
  },
  
  // 发布模板
  publishTemplate(id) {
    return agentApi.post(`/agents/templates/${id}/publish`);
  },
  
  // 取消发布模板
  unpublishTemplate(id) {
    return agentApi.post(`/agents/templates/${id}/unpublish`);
  },
  
  // 批量操作
  bulkControl(data) {
    return agentApi.post('/agents/bulk-control', data);
  },
  
  bulkUpdate(data) {
    return agentApi.post('/agents/bulk-update', data);
  },
  
  bulkDelete(data) {
    return agentApi.post('/agents/bulk-delete', data);
  },
  
  bulkExport(data) {
    return agentApi.post('/agents/bulk-export', data);
  },
  
  bulkImport(data) {
    return agentApi.post('/agents/bulk-import', data);
  }
};

// 智能体管理API
const agentManagementApi = {
  // 获取智能体列表
  getAgents(params) {
    return agentApi.get('/agents', { params });
  },
  
  // 获取智能体详情
  getAgentById(id) {
    return agentApi.get(`/agents/${id}`);
  },
  
  // 创建智能体
  createAgent(data) {
    return agentApi.post('/agents', data);
  },
  
  // 更新智能体
  updateAgent(id, data) {
    return agentApi.put(`/agents/${id}`, data);
  },
  
  // 删除智能体
  deleteAgent(id) {
    return agentApi.delete(`/agents/${id}`);
  },
  
  // 控制智能体
  controlAgent(id, data) {
    return agentApi.post(`/agents/${id}/control`, data);
  },
  
  // 执行智能体任务
  executeAgentTask(id, data) {
    return agentApi.post(`/agents/${id}/execute`, data);
  },
  
  // 获取智能体指标
  getAgentMetrics(id, params) {
    return agentApi.get(`/agents/${id}/metrics`, { params });
  },
  
  // 获取智能体执行日志
  getAgentLogs(id, params) {
    return agentApi.get(`/agents/${id}/logs`, { params });
  }
};

// LangChain相关API
const langChainApi = {
  // 运行LangChain链
  runChain(data) {
    return agentApi.post('/agents/langchain/run', data);
  },
  
  // 获取LangChain统计信息
  getStats() {
    return agentApi.get('/agents/langchain/stats');
  }
};

// 智能体协作API
const agentCollaborationApi = {
  // 运行协作分析
  analyzeCollaboration(data) {
    return agentApi.post('/agents/collaboration/analyze', data);
  }
};

export default {
  agentTemplate: agentTemplateApi,
  agentManagement: agentManagementApi,
  langChain: langChainApi,
  collaboration: agentCollaborationApi
};