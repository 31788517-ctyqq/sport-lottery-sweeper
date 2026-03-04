/**
 * API错误处理工具
 * 提供统一的错误处理机制，改善用户体验
 */

/**
 * 提取错误信息
 * @param {Error|Object} error - 错误对象或响应对象
 * @param {string} defaultMessage - 默认错误消息
 * @returns {string} 格式化的错误消息
 */
export const getErrorMessage = (error, defaultMessage = '操作失败') => {
  if (!error) return defaultMessage;
  
  // Axios错误响应
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.detail || data.message || '请求参数错误';
      case 401:
        return '登录已过期，请重新登录';
      case 403:
        return '没有权限执行此操作';
      case 404:
        return '请求的资源不存在';
      case 422:
        return data.detail ? formatValidationErrors(data.detail) : '数据验证失败';
      case 500:
        return '服务器内部错误，请稍后重试';
      case 502:
      case 503:
      case 504:
        return '服务暂时不可用，请稍后重试';
      default:
        return data.message || data.detail || defaultMessage;
    }
  }
  
  // 网络错误
  if (error.request) {
    return '网络连接失败，请检查网络设置';
  }
  
  // 业务错误（后端返回的success: false）
  if (error.success === false) {
    return error.message || defaultMessage;
  }
  
  // 普通Error对象
  if (error.message) {
    return error.message;
  }
  
  return defaultMessage;
};

/**
 * 格式化验证错误
 * @param {Array|Object} errors - 验证错误
 * @returns {string} 格式化后的错误消息
 */
const formatValidationErrors = (errors) => {
  if (Array.isArray(errors)) {
    return errors.map(err => `${err.loc?.join('.') || ''}: ${err.msg}`).join('; ');
  }
  
  if (typeof errors === 'object') {
    return Object.values(errors).flat().join('; ');
  }
  
  return String(errors);
};

/**
 * 统一API错误处理
 * @param {Function} apiCall - API调用函数
 * @param {string} operation - 操作名称
 * @param {Object} options - 选项
 * @param {boolean} options.showSuccess - 是否显示成功消息
 * @param {string} options.successMessage - 成功消息
 * @param {Function} options.onSuccess - 成功回调
 * @param {Function} options.onError - 错误回调
 * @returns {Promise} API调用结果
 */
export const handleApiCall = async (apiCall, operation, options = {}) => {
  const {
    showSuccess = false,
    successMessage = `${operation}成功`,
    onSuccess,
    onError
  } = options;
  
  try {
    const response = await apiCall();
    
    if (showSuccess) {
      ElMessage.success(successMessage);
    }
    
    onSuccess?.(response);
    return response;
    
  } catch (error) {
    const message = getErrorMessage(error, `${operation}失败`);
    ElMessage.error(message);
    
    // 特殊处理401错误 - 跳转登录
    if (error.response?.status === 401) {
      // 开发环境下只显示提示，避免页面刷新循环
      if (import.meta.env.MODE === 'development') {
        console.warn('🔧 开发模式：跳过401页面跳转')
        ElMessage.warning('开发模式：模拟登录过期状态')
      } else {
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      }
    }
    
    onError?.(error);
    throw error;
  }
};

/**
 * 检查并刷新Token
 * @returns {Promise<string|null>} 有效的token
 */
export const ensureValidToken = async () => {
  let token = localStorage.getItem('access_token') || localStorage.getItem('token');
  
  if (!token) {
    return null;
  }
  
  // TODO: 实现token过期检查和刷新逻辑
  // 这里可以调用刷新token的API
  
  return token;
};

/**
 * 带认证的API调用
 * @param {Function} apiCall - API调用函数
 * @param {string} operation - 操作名称
 * @param {Object} options - 选项
 * @returns {Promise} API调用结果
 */
export const handleAuthenticatedApiCall = async (apiCall, operation, options = {}) => {
  const token = await ensureValidToken();
  
  if (!token) {
    ElMessage.error('请先登录');
    // 开发环境下跳过强制跳转
    if (import.meta.env.MODE !== 'development') {
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
    }
    throw new Error('No valid token');
  }
  
  return handleApiCall(apiCall, operation, options);
};