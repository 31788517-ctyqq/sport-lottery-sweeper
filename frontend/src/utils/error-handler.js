/**
 * 错误处理工具类
 * 统一处理前端错误，包括API错误、JS运行时错误等
 */
import { isBenignBrowserError } from './benign-browser-errors';

/**
 * 错误类型枚举
 */
export const ErrorType = {
  API_ERROR: 'api_error',
  NETWORK_ERROR: 'network_error',
  VALIDATION_ERROR: 'validation_error',
  AUTH_ERROR: 'auth_error',
  PERMISSION_ERROR: 'permission_error',
  RUNTIME_ERROR: 'runtime_error',
  UNKNOWN_ERROR: 'unknown_error'
};

/**
 * 错误级别枚举
 */
export const ErrorLevel = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
};

/**
 * 自定义错误类
 */
export class AppError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = 'AppError';
    this.type = options.type || ErrorType.UNKNOWN_ERROR;
    this.level = options.level || ErrorLevel.ERROR;
    this.code = options.code || 0;
    this.details = options.details || {};
    this.timestamp = new Date().toISOString();
    
    // 保持原型链
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AppError);
    }
  }
  
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      type: this.type,
      level: this.level,
      code: this.code,
      details: this.details,
      timestamp: this.timestamp,
      stack: this.stack
    };
  }
}

/**
 * API错误类
 */
export class APIError extends AppError {
  constructor(message, options = {}) {
    super(message, {
      type: ErrorType.API_ERROR,
      ...options
    });
    this.name = 'APIError';
    this.status = options.status || 500;
    this.url = options.url || '';
    this.method = options.method || 'GET';
  }
}

/**
 * 验证错误类
 */
export class ValidationError extends AppError {
  constructor(message, errors = []) {
    super(message, {
      type: ErrorType.VALIDATION_ERROR,
      level: ErrorLevel.WARNING
    });
    this.name = 'ValidationError';
    this.errors = errors;
  }
}

/**
 * 权限错误类
 */
export class PermissionError extends AppError {
  constructor(message, options = {}) {
    super(message, {
      type: ErrorType.PERMISSION_ERROR,
      level: ErrorLevel.WARNING,
      ...options
    });
    this.name = 'PermissionError';
    this.requiredPermission = options.requiredPermission;
    this.userPermissions = options.userPermissions;
  }
}

/**
 * 错误处理器配置
 */
export class ErrorHandlerConfig {
  constructor(options = {}) {
    this.enableConsoleLog = options.enableConsoleLog !== false;
    this.enableToast = options.enableToast !== false;
    this.enableSentry = options.enableSentry || false;
    this.toastDuration = options.toastDuration || 3000;
    this.ignoredErrors = options.ignoredErrors ?? [
      /ResizeObserver loop completed with undelivered notifications/i,
      /ResizeObserver loop limit exceeded/i
    ];
  }
}

/**
 * 全局错误处理器
 */
export class GlobalErrorHandler {
  constructor(config = new ErrorHandlerConfig()) {
    this.config = config;
    this.errorListeners = [];
    this.isInitialized = false;
  }
  
  /**
   * 初始化全局错误处理器
   */
  init() {
    if (this.isInitialized) return;
    
    // 捕获未处理的Promise错误
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason || 'Unhandled promise rejection', {
        type: ErrorType.RUNTIME_ERROR,
        level: ErrorLevel.ERROR
      });
    });
    
    // 捕获全局JS错误
    window.addEventListener('error', (event) => {
      this.handleError(event.error || event.message, {
        type: ErrorType.RUNTIME_ERROR,
        level: ErrorLevel.ERROR,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      });
    });
    
    this.isInitialized = true;
  }
  
  /**
   * 注册错误监听器
   */
  addErrorListener(listener) {
    if (typeof listener === 'function') {
      this.errorListeners.push(listener);
    }
  }
  
  /**
   * 移除错误监听器
   */
  removeErrorListener(listener) {
    const index = this.errorListeners.indexOf(listener);
    if (index > -1) {
      this.errorListeners.splice(index, 1);
    }
  }
  
  /**
   * 处理错误
   */
  handleError(error, options = {}) {
    // 规范化错误对象
    const normalizedError = this.normalizeError(error, options);
    
    // 检查是否为忽略的错误
    if (this.shouldIgnoreError(normalizedError)) {
      return;
    }
    
    // 调用监听器
    this.errorListeners.forEach(listener => {
      try {
        listener(normalizedError);
      } catch (err) {
        console.error('Error listener failed:', err);
      }
    });
    
    // 控制台输出
    if (this.config.enableConsoleLog) {
      this.logToConsole(normalizedError);
    }
    
    // 显示Toast通知
    if (this.config.enableToast && normalizedError.level !== ErrorLevel.INFO) {
      this.showToast(normalizedError);
    }
    
    // 发送到Sentry
    if (this.config.enableSentry && window.Sentry) {
      this.sendToSentry(normalizedError);
    }
    
    return normalizedError;
  }
  
  /**
   * 规范化错误对象
   */
  normalizeError(error, options = {}) {
    if (error instanceof AppError) {
      return error;
    }
    
    let normalizedError;
    
    if (error instanceof Error) {
      normalizedError = new AppError(error.message, {
        type: options.type || ErrorType.RUNTIME_ERROR,
        level: options.level || ErrorLevel.ERROR,
        details: {
          originalError: error.toString(),
          stack: error.stack,
          ...options
        }
      });
    } else {
      normalizedError = new AppError(String(error), {
        type: options.type || ErrorType.UNKNOWN_ERROR,
        level: options.level || ErrorLevel.ERROR,
        details: options
      });
    }
    
    return normalizedError;
  }
  
  /**
   * 检查是否应该忽略此错误
   */
  shouldIgnoreError(error) {
    if (isBenignBrowserError(error?.message)) {
      return true;
    }

    return this.config.ignoredErrors.some(ignored => {
      if (typeof ignored === 'string') {
        return error.message.includes(ignored);
      }
      if (ignored instanceof RegExp) {
        return ignored.test(error.message);
      }
      return false;
    });
  }
  
  /**
   * 控制台输出
   */
  logToConsole(error) {
    const styles = {
      [ErrorLevel.INFO]: 'color: #1890ff; font-weight: bold;',
      [ErrorLevel.WARNING]: 'color: #faad14; font-weight: bold;',
      [ErrorLevel.ERROR]: 'color: #f5222d; font-weight: bold;',
      [ErrorLevel.CRITICAL]: 'color: #cf1322; font-weight: bold; background: #fff1f0;'
    };
    
    const style = styles[error.level] || styles[ErrorLevel.ERROR];
    
    console.group(`🚨 ${error.name} - ${error.level.toUpperCase()}`);
    console.log(`%c${error.message}`, style);
    console.log('Type:', error.type);
    console.log('Timestamp:', error.timestamp);
    
    if (error.details && Object.keys(error.details).length > 0) {
      console.log('Details:', error.details);
    }
    
    if (error.stack) {
      console.log('Stack:', error.stack);
    }
    
    console.groupEnd();
  }
  
  /**
   * 显示Toast通知
   */
  showToast(error) {
    // 这里需要根据项目使用的UI框架来调整
    // 假设使用Element Plus的ElMessage
    if (window.ElMessage) {
      const typeMap = {
        [ErrorLevel.INFO]: 'info',
        [ErrorLevel.WARNING]: 'warning',
        [ErrorLevel.ERROR]: 'error',
        [ErrorLevel.CRITICAL]: 'error'
      };
      
      window.ElMessage({
        message: error.message,
        type: typeMap[error.level],
        duration: this.config.toastDuration,
        showClose: true
      });
    } else if (window.$message) {
      // 假设使用Ant Design Vue的message
      window.$message[error.level](error.message);
    } else {
      // 降级方案：使用alert
      alert(`错误：${error.message}`);
    }
  }
  
  /**
   * 发送到Sentry
   */
  sendToSentry(error) {
    try {
      if (window.Sentry.captureException) {
        window.Sentry.captureException(error);
      }
    } catch (sentryError) {
      console.error('Failed to send error to Sentry:', sentryError);
    }
  }
  
  /**
   * 创建API错误处理函数
   */
  createAPIErrorHandler() {
    return (error) => {
      let apiError;
      
      if (error.response) {
        // 服务器返回了错误响应
        const { status, data, config } = error.response;
        const message = data?.message || `HTTP ${status}`;
        
        apiError = new APIError(message, {
          status,
          url: config?.url,
          method: config?.method,
          details: data
        });
        
        // 根据HTTP状态码设置错误类型
        if (status === 401) {
          apiError.type = ErrorType.AUTH_ERROR;
          apiError.level = ErrorLevel.WARNING;
        } else if (status === 403) {
          apiError.type = ErrorType.PERMISSION_ERROR;
          apiError.level = ErrorLevel.WARNING;
        } else if (status === 422) {
          apiError.type = ErrorType.VALIDATION_ERROR;
          apiError.level = ErrorLevel.WARNING;
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        apiError = new APIError('网络错误，请检查网络连接', {
          type: ErrorType.NETWORK_ERROR,
          level: ErrorLevel.ERROR
        });
      } else {
        // 请求配置错误
        apiError = new APIError(error.message || '请求配置错误', {
          type: ErrorType.API_ERROR,
          level: ErrorLevel.ERROR
        });
      }
      
      return this.handleError(apiError);
    };
  }
  
  /**
   * 创建Vue错误处理器
   */
  createVueErrorHandler() {
    return (err, vm, info) => {
      const vueError = new AppError(err.message || 'Vue组件错误', {
        type: ErrorType.RUNTIME_ERROR,
        level: ErrorLevel.ERROR,
        details: {
          component: vm?.$options?.name,
          info,
          vm
        }
      });
      
      return this.handleError(vueError);
    };
  }
  
  /**
   * 创建React错误边界处理器
   */
  createReactErrorHandler() {
    return (error, errorInfo) => {
      const reactError = new AppError(error.message || 'React组件错误', {
        type: ErrorType.RUNTIME_ERROR,
        level: ErrorLevel.ERROR,
        details: {
          componentStack: errorInfo.componentStack
        }
      });
      
      return this.handleError(reactError);
    };
  }
}

/**
 * 全局错误处理器实例
 */
export const errorHandler = new GlobalErrorHandler();

/**
 * 错误处理工具函数
 */
export const errorUtils = {
  /**
   * 安全执行函数，捕获所有错误
   */
  safeExecute(func, ...args) {
    try {
      return func(...args);
    } catch (error) {
      errorHandler.handleError(error);
      return null;
    }
  },
  
  /**
   * 安全执行异步函数
   */
  async safeExecuteAsync(func, ...args) {
    try {
      return await func(...args);
    } catch (error) {
      errorHandler.handleError(error);
      return null;
    }
  },
  
  /**
   * 包装函数，自动捕获错误
   */
  withErrorHandling(func, options = {}) {
    return function(...args) {
      try {
        const result = func.apply(this, args);
        
        // 如果是Promise，捕获异步错误
        if (result && typeof result.then === 'function') {
          return result.catch(error => {
            errorHandler.handleError(error, options);
            throw error;
          });
        }
        
        return result;
      } catch (error) {
        errorHandler.handleError(error, options);
        throw error;
      }
    };
  },
  
  /**
   * 创建重试机制
   */
  createRetry(func, maxRetries = 3, delay = 1000) {
    return async function(...args) {
      let lastError;
      
      for (let i = 0; i < maxRetries; i++) {
        try {
          return await func(...args);
        } catch (error) {
          lastError = error;
          
          if (i < maxRetries - 1) {
            await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
          }
        }
      }
      
      throw lastError;
    };
  },
  
  /**
   * 错误消息映射
   */
  getErrorMessage(error, defaultMessage = '操作失败，请重试') {
    if (!error) return defaultMessage;
    
    // 如果是自定义错误，直接返回消息
    if (error instanceof AppError) {
      return error.message;
    }
    
    // 处理常见的错误消息
    if (error.message) {
      const message = error.message.toLowerCase();
      
      if (message.includes('network')) {
        return '网络连接失败，请检查网络设置';
      }
      
      if (message.includes('timeout')) {
        return '请求超时，请稍后重试';
      }
      
      if (message.includes('auth') || message.includes('unauthorized')) {
        return '登录已过期，请重新登录';
      }
      
      if (message.includes('permission') || message.includes('forbidden')) {
        return '权限不足，无法执行此操作';
      }
      
      return error.message;
    }
    
    return defaultMessage;
  }
};

// 导出默认实例和工具函数
export default {
  ErrorType,
  ErrorLevel,
  AppError,
  APIError,
  ValidationError,
  PermissionError,
  ErrorHandlerConfig,
  GlobalErrorHandler,
  errorHandler,
  ...errorUtils
};
