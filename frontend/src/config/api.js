// API配置管理

// 基础API配置
export const API_CONFIG = {
  // 基础URL - 从环境变量获取
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  
  // WebSocket配置
  WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:3000',
  
  // 超时配置
  TIMEOUT: {
    DEFAULT: 15000,
    UPLOAD: 300000, // 文件上传5分钟
    DOWNLOAD: 300000, // 文件下载5分钟
    LONG_POLLING: 60000 // 长轮询1分钟
  },
  
  // 分页配置
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 20,
    PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
    MAX_PAGE_SIZE: 1000
  },
  
  // 文件上传配置
  UPLOAD: {
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv', // .csv
      'image/jpeg',
      'image/png',
      'image/gif'
    ]
  },
  
  // 导出配置
  EXPORT: {
    MAX_EXPORT_COUNT: 10000,
    SUPPORTED_FORMATS: ['xlsx', 'csv', 'pdf']
  },
  
  // 实时数据配置
  REALTIME: {
    RECONNECT_INTERVAL: 3000,
    MAX_RECONNECT_ATTEMPTS: 5,
    HEARTBEAT_INTERVAL: 30000
  }
}

// API端点配置
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
    PROFILE: '/api/v1/auth/me'
  },
  
  // 用户管理
  USERS: {
    LIST: '/api/v1/admin/users',
    CREATE: '/api/v1/admin/users',
    UPDATE: (id) => `/api/v1/admin/users/${id}`,
    DELETE: (id) => `/api/v1/admin/users/${id}`,
    BATCH_DELETE: '/api/v1/admin/users/batch-delete',
    ENABLE: (id) => `/api/v1/admin/users/${id}/enable`,
    DISABLE: (id) => `/api/v1/admin/users/${id}/disable`,
    RESET_PASSWORD: (id) => `/api/v1/admin/users/${id}/reset-password`,
    ASSIGN_ROLES: (id) => `/api/v1/admin/users/${id}/roles`,
    PERMISSIONS: (id) => `/api/v1/admin/users/${id}/permissions`
  },
  
  // 角色管理
  ROLES: {
    LIST: '/api/v1/admin/roles',
    CREATE: '/api/v1/admin/roles',
    UPDATE: (id) => `/api/v1/admin/roles/${id}`,
    DELETE: (id) => `/api/v1/admin/roles/${id}`,
    PERMISSIONS: (id) => `/api/v1/admin/roles/${id}/permissions`
  },
  
  // 权限管理
  PERMISSIONS: {
    LIST: '/api/v1/admin/permissions',
    TREE: '/api/v1/admin/permissions/tree'
  },
  
  // 部门管理
  DEPARTMENTS: {
    LIST: '/api/v1/admin/departments',
    CREATE: '/api/v1/admin/departments',
    UPDATE: (id) => `/api/v1/admin/departments/${id}`,
    DELETE: (id) => `/api/v1/admin/departments/${id}`,
    MEMBERS: (id) => `/api/v1/admin/departments/${id}/members`,
    ADD_MEMBERS: (id) => `/api/v1/admin/departments/${id}/members/add`,
    REMOVE_MEMBERS: (id) => `/api/v1/admin/departments/${id}/members/remove`
  },
  
  // 操作日志
  OPERATION_LOGS: {
    LIST: '/api/v1/admin/system/logs/db/user',
    STATISTICS: '/api/v1/admin/system/logs/db/statistics',
    EXPORT: '/api/v1/admin/system/logs/export'
  },
  
  // 系统监控
  SYSTEM: {
    HEALTH: '/api/v1/system/health',
    METRICS: '/api/v1/system/metrics',
    CONFIG: '/api/v1/system/config'
  }
}

// HTTP状态码映射
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
}

// 业务错误码映射
export const BUSINESS_CODES = {
  SUCCESS: 0,
  ERROR: -1,
  VALIDATION_ERROR: -2,
  UNAUTHORIZED: -3,
  FORBIDDEN: -4,
  NOT_FOUND: -5,
  DUPLICATE_ENTRY: -6,
  SYSTEM_ERROR: -999
}