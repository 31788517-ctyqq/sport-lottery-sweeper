// Global Configuration File
// Centralized configuration management for the Sports Lottery Sweeper System

// Environment detection - Vite way of handling environment variables
const isDevelopment = import.meta.env.MODE === 'development'
const isProduction = import.meta.env.MODE === 'production'
const isStaging = import.meta.env.MODE === 'staging'

// =============================================================================
// API Configuration
// =============================================================================
export const API_CONFIG = {
  // Base URLs
  BASE_URL: import.meta.env.VITE_API_BASE_URL || (isDevelopment ? 'http://localhost:3000/api' : 
              isStaging ? 'https://staging-api.sportsweeper.com/api' : 
              'https://api.sportsweeper.com/api'),
  
  // Version
  VERSION: 'v1',
  
  // Timeout settings
  TIMEOUT: {
    DEFAULT: 10000,
    UPLOAD: 300000,
    DOWNLOAD: 60000,
    LONG_POLLING: 120000
  },

  // Retry configuration
  RETRY: {
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000,
    BACKOFF_MULTIPLIER: 2
  },

  // Rate limiting
  RATE_LIMIT: {
    WINDOW_MS: 15 * 60 * 1000, // 15 minutes
    MAX_REQUESTS: 1000
  },

  // Headers
  HEADERS: {
    CONTENT_TYPE: 'application/json',
    ACCEPT: 'application/json',
    AUTHORIZATION: 'Bearer'
  }
}

// =============================================================================
// Route Configuration
// =============================================================================
export const ROUTE_CONFIG = {
  // Public routes (no authentication required)
  PUBLIC_ROUTES: [
    '/login',
    '/register',
    '/forgot-password',
    '/reset-password',
    '/404',
    '/health'
  ],

  // Admin routes (require admin role)
  ADMIN_ROUTES: [
    '/admin/users',
    '/admin/settings',
    '/admin/system'
  ],

  // Intelligence routes (specific permissions may apply)
  INTELLIGENCE_ROUTES: [
    '/admin/intelligence/collection',
    '/admin/intelligence/model',
    '/admin/intelligence/weight',
    '/admin/intelligence/graph'
  ],

  // Routes that require authentication
  PROTECTED_ROUTES: [
    '/admin',
    '/dashboard',
    '/profile',
    '/settings'
  ],

  // Redirect paths
  REDIRECT_PATHS: {
    LOGIN_SUCCESS: '/admin/dashboard',
    LOGOUT_REDIRECT: '/login',
    ACCESS_DENIED: '/403',
    NOT_FOUND: '/404',
    SERVER_ERROR: '/500'
  }
}

// =============================================================================
// Feature Flags
// =============================================================================
export const FEATURE_FLAGS = {
  // Core features
  ENABLE_INTELLIGENCE_MODULE: true,
  ENABLE_USER_MANAGEMENT: true,
  ENABLE_SYSTEM_SETTINGS: true,
  ENABLE_DATA_EXPORT: true,
  ENABLE_REAL_TIME_UPDATES: true,

  // Intelligence features
  ENABLE_DATA_COLLECTION: true,
  ENABLE_MODEL_MANAGEMENT: true,
  ENABLE_WEIGHT_MANAGEMENT: true,
  ENABLE_GRAPH_MANAGEMENT: true,
  ENABLE_PREDICTION_ENGINE: true,

  // UI features
  ENABLE_DARK_MODE: true,
  ENABLE_THEME_SWITCHER: true,
  ENABLE_ANIMATIONS: true,
  ENABLE_TOOLTIPS: true,
  ENABLE_BREADCRUMBS: true,

  // Advanced features
  ENABLE_ADVANCED_ANALYTICS: false, // Beta feature
  ENABLE_MACHINE_LEARNING: false,  // Enterprise feature
  ENABLE_API_ACCESS: false,         // Enterprise feature
  ENABLE_WEBHOOKS: false,           // Enterprise feature
  ENABLE_MULTI_TENANCY: false       // Enterprise feature
}

// =============================================================================
// Application Constants
// =============================================================================
export const APP_CONSTANTS = {
  // App metadata
  APP_NAME: '体育彩票扫盘系统',
  APP_NAME_EN: 'Sports Lottery Sweeper',
  APP_VERSION: '1.0.0',
  APP_DESCRIPTION: '智能体育彩票分析平台',
  
  // Session management
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  REFRESH_TOKEN_THRESHOLD: 5 * 60 * 1000, // 5 minutes before expiry
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  MAX_PAGE_SIZE: 1000,

  // File upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'text/csv'
  ],
  UPLOAD_PATH: '/uploads/',

  // Data limits
  MAX_TEXT_LENGTH: 5000,
  MAX_TITLE_LENGTH: 200,
  MAX_DESCRIPTION_LENGTH: 1000,

  // Cache settings
  CACHE_TTL: {
    USER_DATA: 5 * 60 * 1000,      // 5 minutes
    CONFIG_DATA: 30 * 60 * 1000,   // 30 minutes
    STATIC_DATA: 24 * 60 * 60 * 1000, // 24 hours
    REAL_TIME_DATA: 30 * 1000      // 30 seconds
  },

  // Validation rules
  VALIDATION: {
    PASSWORD_MIN_LENGTH: 6,
    PASSWORD_MAX_LENGTH: 20,
    USERNAME_MIN_LENGTH: 3,
    USERNAME_MAX_LENGTH: 20,
    EMAIL_REGEX: /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/,
    PHONE_REGEX: /^1[3-9]\d{9}$/,
    URL_REGEX: /^https?:\/\/.+/,
    COLOR_REGEX: /^#[0-9A-F]{6}$/i
  }
}

// =============================================================================
// UI Configuration
// =============================================================================
export const UI_CONFIG = {
  // Layout
  SIDEBAR_WIDTH: {
    EXPANDED: 240,
    COLLAPSED: 64
  },
  HEADER_HEIGHT: 64,
  TAB_HEIGHT: 40,

  // Breakpoints (matching Element Plus)
  BREAKPOINTS: {
    XS: 0,
    SM: 768,
    MD: 992,
    LG: 1200,
    XL: 1920
  },

  // Z-index layers
  Z_INDEX: {
    DROPDOWN: 1000,
    STICKY: 1010,
    FIXED: 1020,
    MODAL_BACKDROP: 1030,
    MODAL: 1040,
    POPOVER: 1050,
    TOOLTIP: 1060
  },

  // Animation durations
  ANIMATION: {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500
  },

  // Toast notifications
  TOAST: {
    DURATION: {
      SUCCESS: 3000,
      WARNING: 4000,
      ERROR: 5000,
      INFO: 3000
    },
    POSITION: 'top-right'
  },

  // Loading states
  LOADING: {
    DELAY: 300,
    TEXT_DEFAULT: '加载中...',
    TEXT_UPLOAD: '上传中...',
    TEXT_DOWNLOAD: '下载中...',
    TEXT_SAVE: '保存中...',
    TEXT_DELETE: '删除中...'
  }
}

// =============================================================================
// Chart Configuration
// =============================================================================
export const CHART_CONFIG = {
  // Default chart settings
  DEFAULT_OPTIONS: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false
      }
    }
  },

  // Color schemes
  COLOR_SCHEMES: {
    PRIMARY: [
      '#409eff', '#67c23a', '#e6a23c', '#f56c6c',
      '#909399', '#c069af', '#06b6d4', '#f97316'
    ],
    SPORTS: [
      '#409eff', '#67c23a', '#e6a23c', '#f56c6c',
      '#8b5cf6', '#06b6d4', '#f59e0b', '#10b981'
    ],
    FINANCIAL: [
      '#10b981', '#f59e0b', '#ef4444', '#3b82f6',
      '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'
    ]
  },

  // Chart types for different data
  CHART_TYPES: {
    LINE: 'line',
    BAR: 'bar',
    PIE: 'pie',
    DOUGHNUT: 'doughnut',
    RADAR: 'radar',
    SCATTER: 'scatter',
    BUBBLE: 'bubble'
  },

  // Animation settings
  ANIMATION: {
    DURATION: 1000,
    EASING: 'easeInOutQuart'
  }
}

// =============================================================================
// Sports-specific Configuration
// =============================================================================
export const SPORTS_CONFIG = {
  // Supported sports
  SUPPORTED_SPORTS: [
    { key: 'football', name: '足球', icon: 'Football', color: '#22c55e' },
    { key: 'basketball', name: '篮球', icon: 'Basketball', color: '#f59e0b' },
    { key: 'tennis', name: '网球', icon: 'Tennis', color: '#3b82f6' },
    { key: 'baseball', name: '棒球', icon: 'Baseball', color: '#ef4444' },
    { key: 'volleyball', name: '排球', icon: 'Volleyball', color: '#8b5cf6' },
    { key: 'table_tennis', name: '乒乓球', icon: 'TableTennis', color: '#06b6d4' }
  ],

  // Lottery types
  LOTTERY_TYPES: [
    { key: 'ssq', name: '双色球', code: 'SSQ' },
    { key: 'dlt', name: '大乐透', code: 'DLT' },
    { key: 'pl3', name: '排列三', code: 'PL3' },
    { key: 'pl5', name: '排列五', code: 'PL5' },
    { key: 'qxc', name: '七星彩', code: 'QXC' },
    { key: 'kl8', name: '快乐8', code: 'KL8' }
  ],

  // Analysis algorithms
  ALGORITHMS: [
    { key: 'statistical', name: '统计分析', description: '基于历史数据的统计分析' },
    { key: 'trend', name: '趋势分析', description: '识别号码走势和规律' },
    { key: 'probability', name: '概率模型', description: '基于概率论的数学模型' },
    { key: 'machine_learning', name: '机器学习', description: 'AI驱动的智能预测' },
    { key: 'hybrid', name: '混合算法', description: '多算法综合预测' }
  ],

  // Data sources
  DATA_SOURCES: [
    { key: 'official', name: '官方开奖', reliability: 100 },
    { key: 'third_party', name: '第三方数据', reliability: 85 },
    { key: 'historical', name: '历史数据', reliability: 95 },
    { key: 'real_time', name: '实时数据', reliability: 90 }
  ],

  // Confidence levels
  CONFIDENCE_LEVELS: [
    { level: 90, label: '高信心', color: '#22c55e', description: '非常可信的预测' },
    { level: 70, label: '中信心', color: '#f59e0b', description: '较为可信的预测' },
    { level: 50, label: '低信心', color: '#ef4444', description: '参考性预测' },
    { level: 30, label: '极低信心', color: '#6b7280', description: '仅供娱乐参考' }
  ]
}

// =============================================================================
// External Services Configuration
// =============================================================================
export const EXTERNAL_SERVICES = {
  // Third-party APIs
  WEATHER_API: {
    KEY: import.meta.env.VUE_APP_WEATHER_API_KEY,
    BASE_URL: 'https://api.weatherapi.com/v1',
    ENABLED: !!import.meta.env.VUE_APP_WEATHER_API_KEY
  },

  MAP_SERVICE: {
    KEY: import.meta.env.VUE_APP_MAP_API_KEY,
    BASE_URL: 'https://restapi.amap.com/v3',
    ENABLED: !!import.meta.env.VUE_APP_MAP_API_KEY
  },

  SMS_SERVICE: {
    ENDPOINT: import.meta.env.VUE_APP_SMS_ENDPOINT,
    ENABLED: !!import.meta.env.VUE_APP_SMS_ENDPOINT
  },

  EMAIL_SERVICE: {
    ENDPOINT: import.meta.env.VUE_APP_EMAIL_ENDPOINT,
    ENABLED: !!import.meta.env.VUE_APP_EMAIL_ENDPOINT
  },

  // CDN configuration
  CDN: {
    BASE_URL: import.meta.env.VUE_APP_CDN_URL || '',
    BUCKET: import.meta.env.VUE_APP_CDN_BUCKET || 'sportsweeper-assets'
  },

  // Analytics
  ANALYTICS: {
    GOOGLE_ANALYTICS_ID: import.meta.env.VUE_APP_GA_ID,
    ENABLED: !!import.meta.env.VUE_APP_GA_ID,
    SENTRY_DSN: import.meta.env.VUE_APP_SENTRY_DSN,
    BUGSNAG_KEY: import.meta.env.VUE_APP_BUGSNAG_KEY
  }
}

// =============================================================================
// Development & Debug Configuration
// =============================================================================
export const DEVELOPMENT_CONFIG = {
  // Debug settings
  DEBUG: {
    ENABLED: isDevelopment,
    VERBOSE_LOGGING: isDevelopment,
    API_MOCKING: isDevelopment,
    SHOW_PERFORMANCE_MONITOR: isDevelopment,
    ENABLE_VUE_DEVTOOLS: isDevelopment
  },

  // Mock data
  MOCK: {
    ENABLED: isDevelopment,
    DELAY: 500, // ms
    FAILURE_RATE: 0.05 // 5% failure rate for testing
  },

  // Hot reload
  HOT_RELOAD: {
    ENABLED: isDevelopment,
    PORT: 8080
  },

  // API simulation
  API_SIMULATION: {
    ENABLED: isDevelopment,
    BASE_URL: 'http://localhost:3001/mock'
  }
}

// =============================================================================
// Environment Detection Helpers
// =============================================================================
export const ENV_HELPERS = {
  isDevelopment: () => isDevelopment,
  isProduction: () => isProduction,
  isStaging: () => isStaging,
  isTest: () => import.meta.env.MODE === 'test',
  
  getEnvironment: () => {
    if (isDevelopment) return 'development'
    if (isStaging) return 'staging'
    if (isProduction) return 'production'
    return 'unknown'
  },

  isFeatureEnabled: (featureName) => {
    return FEATURE_FLAGS[featureName] === true
  },

  getApiUrl: (endpoint = '') => {
    return `${API_CONFIG.BASE_URL}/${API_CONFIG.VERSION}${endpoint}`
  },

  getAssetUrl: (assetPath) => {
    if (EXTERNAL_SERVICES.CDN.BASE_URL) {
      return `${EXTERNAL_SERVICES.CDN.BASE_URL}/${EXTERNAL_SERVICES.CDN.BUCKET}${assetPath}`
    }
    return assetPath
  }
}

// =============================================================================
// Configuration Validation
// =============================================================================
export const validateConfig = () => {
  const errors = []
  
  // Validate required configurations
  if (!API_CONFIG.BASE_URL) {
    errors.push('API_BASE_URL is required')
  }
  
  if (!APP_CONSTANTS.APP_NAME) {
    errors.push('APP_NAME is required')
  }
  
  // Validate URLs
  if (API_CONFIG.BASE_URL && API_CONFIG.HEADERS && API_CONFIG.HEADERS.URL_REGEX && typeof API_CONFIG.HEADERS.URL_REGEX.test === 'function') {
    if (!API_CONFIG.HEADERS.URL_REGEX.test(API_CONFIG.BASE_URL)) {
      errors.push('Invalid API_BASE_URL format')
    }
  }
  
  // Log warnings for development
  if (isDevelopment && errors.length > 0) {
    console.warn('Configuration validation warnings:', errors)
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

// Run validation on import
validateConfig()

// Default export with all configurations
export default {
  // Environment
  isDevelopment,
  isProduction,
  isStaging,
  
  // Main configuration sections
  API_CONFIG,
  ROUTE_CONFIG,
  FEATURE_FLAGS,
  APP_CONSTANTS,
  UI_CONFIG,
  CHART_CONFIG,
  SPORTS_CONFIG,
  EXTERNAL_SERVICES,
  DEVELOPMENT_CONFIG,
  
  // Helpers
  ENV_HELPERS,
  
  // Validation
  validateConfig
}