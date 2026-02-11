/**
 * 统一日志响应数据处理器
 * 处理不同格式的API响应，返回标准化的数据结构
 * AI_WORKING: coder1 @2026-02-10
 */
export const processLogResponse = (response) => {
  if (!response) {
    return { items: [], total: 0 };
  }
  
  // 情况1: response 直接包含 items 和 total (request.js 已处理)
  if (response.items !== undefined) {
    return {
      items: Array.isArray(response.items) ? response.items : [],
      total: typeof response.total === 'number' ? response.total : 0
    };
  }
  
  // 情况2: response 是数组 (直接返回的日志列表)
  if (Array.isArray(response)) {
    return {
      items: response,
      total: response.length
    };
  }
  
  // 情况3: response 包含 data 字段 (未经过 request.js 处理)
  if (response.data && response.data.items !== undefined) {
    return {
      items: Array.isArray(response.data.items) ? response.data.items : [],
      total: typeof response.data.total === 'number' ? response.data.total : 0
    };
  }
  
  // 默认情况
  return { items: [], total: 0 };
};

/**
 * 安全日志加载函数
 */
export const safeLoadLogs = async (apiCall, errorHandler = null) => {
  try {
    const response = await apiCall();
    return processLogResponse(response);
  } catch (error) {
    console.error('加载日志失败:', error);
    if (errorHandler) {
      errorHandler(error);
    }
    return { items: [], total: 0 };
  }
};