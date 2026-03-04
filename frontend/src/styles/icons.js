import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// Icon categories for organization
export const ICON_CATEGORIES = {
  NAVIGATION: 'navigation',
  ACTION: 'action',
  DATA: 'data',
  UI: 'ui',
  BUSINESS: 'business',
  SPORTS: 'sports',
  SYSTEM: 'system'
}

// Navigation Icons
export const NAVIGATION_ICONS = {
  // Basic navigation
  HOME: 'House',
  DASHBOARD: 'TrendCharts',
  MENU: 'Menu',
  BACK: 'ArrowLeft',
  FORWARD: 'ArrowRight',
  UP: 'ArrowUp',
  DOWN: 'ArrowDown',
  REFRESH: 'Refresh',
  EXPAND: 'Expand',
  FOLD: 'Fold',
  
  // Layout
  GRID: 'Grid',
  LIST: 'List',
  TABLE: 'Tickets',
  TREE: 'Sort',
  
  // External links
  EXTERNAL_LINK: 'Link',
  OPEN: 'TopRight',
  FULL_SCREEN: 'FullScreen',
  EXIT_FULL_SCREEN: 'CloseBold'
}

// Action Icons
export const ACTION_ICONS = {
  // CRUD operations
  ADD: 'Plus',
  CREATE: 'Plus',
  EDIT: 'Edit',
  UPDATE: 'Edit',
  DELETE: 'Delete',
  REMOVE: 'Remove',
  SAVE: 'DocumentChecked',
  CANCEL: 'Close',
  CLEAR: 'CircleClose',
  CONFIRM: 'SuccessFilled',
  APPROVE: 'CircleCheckFilled',
  REJECT: 'CircleCloseFilled',
  
  // File operations
  UPLOAD: 'UploadFilled',
  DOWNLOAD: 'Download',
  IMPORT: 'Upload',
  EXPORT: 'Download',
  ATTACHMENT: 'Paperclip',
  
  // Data operations
  SEARCH: 'Search',
  FILTER: 'Filter',
  SORT: 'Sort',
  VIEW: 'View',
  PREVIEW: 'View',
  HIDE: 'Hide',
  SHOW: 'View',
  COPY: 'CopyDocument',
  PASTE: 'DocumentCopy',
  PRINT: 'Printer',
  SHARE: 'Share',
  
  // State changes
  ENABLE: 'CircleCheck',
  DISABLE: 'CircleClose',
  ACTIVATE: 'SuccessFilled',
  DEACTIVATE: 'CircleCloseFilled',
  LOCK: 'Lock',
  UNLOCK: 'Unlock',
  STAR: 'Star',
  FAVORITE: 'StarFilled'
}

// Data & Analytics Icons
export const DATA_ICONS = {
  // Charts and graphs
  CHART: 'TrendCharts',
  LINE_CHART: 'TrendCharts',
  BAR_CHART: 'Histogram',
  PIE_CHART: 'PieChart',
  AREA_CHART: 'DataLine',
  SCATTER_CHART: 'LocationInformation',
  
  // Data types
  DATABASE: 'DataBase',
  TABLE: 'Grid',
  FORM: 'EditPen',
  CALENDAR: 'Calendar',
  TIMELINE: 'Clock',
  
  // Analytics
  ANALYZE: 'DataAnalysis',
  STATISTICS: 'Histogram',
  METRICS: 'Odometer',
  REPORT: 'Document',
  INSIGHT: 'View',
  TREND: 'TrendCharts',
  COMPARE: 'Operation',
  
  // Data quality
  VALIDATE: 'SuccessFilled',
  CHECK: 'CircleCheck',
  WARNING: 'WarningFilled',
  ERROR: 'CircleCloseFilled',
  INFO: 'InfoFilled',
  QUESTION: 'QuestionFilled'
}

// UI Component Icons
export const UI_ICONS = {
  // Feedback
  SUCCESS: 'SuccessFilled',
  WARNING: 'WarningFilled',
  ERROR: 'CircleCloseFilled',
  INFO: 'InfoFilled',
  HELP: 'QuestionFilled',
  
  // User interface
  USER: 'User',
  USERS: 'UserFilled',
  AVATAR: 'Avatar',
  SETTING: 'Setting',
  CONFIGURATION: 'Tools',
  THEME: 'Brush',
  LANGUAGE: 'ChatLineRound',
  
  // Display
  IMAGE: 'PictureFilled',
  VIDEO: 'VideoCameraFilled',
  AUDIO: 'Microphone',
  ICON: 'PictureRounded',
  COLOR: 'Brush',
  
  // Layout
  WINDOW: 'Crop',
  DIALOG: 'ChatSquare',
  MODAL: 'ChatLineRound',
  DRAWER: 'FolderOpened',
  COLLAPSE: 'Fold',
  EXPAND: 'Expand',
  
  // Progress
  LOADING: 'Loading',
  PROGRESS: 'Loading',
  COMPLETE: 'CircleCheckFilled',
  IN_PROGRESS: 'Loading',
  PENDING: 'Clock'
}

// Business Domain Icons
export const BUSINESS_ICONS = {
  // Finance
  MONEY: 'Money',
  CURRENCY: 'Money',
  PRICE: 'PriceTag',
  COST: 'Wallet',
  REVENUE: 'TrendCharts',
  PROFIT: 'TopRight',
  LOSS: 'BottomRight',
  BUDGET: 'WalletFilled',
  
  // E-commerce
  SHOPPING: 'ShoppingCart',
  ORDER: 'Document',
  CART: 'ShoppingCart',
  PAYMENT: 'CreditCard',
  INVOICE: 'DocumentChecked',
  DELIVERY: 'Van',
  
  // HR & Organization
  TEAM: 'UserFilled',
  ORGANIZATION: 'OfficeBuilding',
  DEPARTMENT: 'School',
  POSITION: 'Location',
  ROLE: 'UserFilled',
  PERMISSION: 'Key',
  
  // Project Management
  PROJECT: 'Folder',
  TASK: 'Memo',
  TODO: 'List',
  SCHEDULE: 'Calendar',
  MILESTONE: 'Flag',
  DEADLINE: 'AlarmClock',
  
  // Communication
  MESSAGE: 'ChatDotRound',
  NOTIFICATION: 'Bell',
  EMAIL: 'Message',
  CALL: 'Phone',
  MEETING: 'VideoCamera',
  CHAT: 'ChatLineRound'
}

// Sports-specific Icons
export const SPORTS_ICONS = {
  // General sports
  SPORTS: 'Trophy',
  GAME: 'Trophy',
  COMPETITION: 'Medal',
  TOURNAMENT: 'TrophyBase',
  MATCH: 'Connection',
  EVENT: 'Calendar',
  
  // Team sports
  TEAM: 'UserFilled',
  PLAYER: 'User',
  COACH: 'UserFilled',
  STADIUM: 'House',
  FIELD: 'Location',
  
  // Individual sports
  RACE: 'Timer',
  RUNNING: 'Position',
  SWIMMING: 'WaterFlash',
  CYCLING: 'Bicycle',
  
  // Ball sports
  BALL: 'Football',
  GOAL: 'TopRight',
  SCORE: 'TrendCharts',
  POINTS: 'StarFilled',
  
  // Analysis
  ANALYZE: 'DataAnalysis',
  PREDICTION: 'MagicStick',
  STRATEGY: 'Operation',
  STATISTICS: 'Histogram',
  PERFORMANCE: 'TrendCharts',
  
  // Betting/Lottery
  LOTTERY: 'Ticket',
  BET: 'Coin',
  ODDS: 'Percent',
  WIN: 'CircleCheckFilled',
  LOSE: 'CircleCloseFilled',
  JACKPOT: 'Trophy'
}

// System Icons
export const SYSTEM_ICONS = {
  // System status
  POWER: 'SwitchButton',
  RESTART: 'RefreshRight',
  SHUTDOWN: 'SwitchButton',
  HEALTH: 'CircleCheck',
  MONITOR: 'Monitor',
  
  // Security
  SECURITY: 'Lock',
  PROTECT: 'Shield',
  FIREWALL: 'Lock',
  ENCRYPT: 'Key',
  DECRYPT: 'Unlock',
  
  // Network
  NETWORK: 'Connection',
  SERVER: 'Service',
  CLOUD: 'Cloudy',
  API: 'Link',
  ROUTER: 'Share',
  
  // Storage
  STORAGE: 'FolderOpened',
  BACKUP: 'Download',
  ARCHIVE: 'Folder',
  CACHE: 'Refresh',
  
  // Monitoring
  LOG: 'Document',
  TRACKING: 'Position',
  DEBUG: 'Tools',
  ALERT: 'Bell',
  MONITORING: 'View'
}

// Icon registry - maps string names to actual components
class IconRegistry {
  constructor() {
    this.registry = new Map()
    this.initializeRegistry()
  }

  initializeRegistry() {
    // Register all Element Plus icons
    Object.entries(ElementPlusIconsVue).forEach(([name, component]) => {
      this.registry.set(name, component)
    })
  }

  // Get icon component by name
  getIcon(iconName) {
    if (!iconName) return null
    
    // Support both string and object notation
    const name = typeof iconName === 'string' ? iconName : iconName.name
    return this.registry.get(name) || null
  }

  // Check if icon exists
  hasIcon(iconName) {
    return this.registry.has(typeof iconName === 'string' ? iconName : iconName.name)
  }

  // Get all registered icons
  getAllIcons() {
    return Array.from(this.registry.keys())
  }

  // Get icons by category
  getIconsByCategory(category) {
    const categoryMap = {
      [ICON_CATEGORIES.NAVIGATION]: NAVIGATION_ICONS,
      [ICON_CATEGORIES.ACTION]: ACTION_ICONS,
      [ICON_CATEGORIES.DATA]: DATA_ICONS,
      [ICON_CATEGORIES.UI]: UI_ICONS,
      [ICON_CATEGORIES.BUSINESS]: BUSINESS_ICONS,
      [ICON_CATEGORIES.SPORTS]: SPORTS_ICONS,
      [ICON_CATEGORIES.SYSTEM]: SYSTEM_ICONS
    }

    return categoryMap[category] || {}
  }

  // Search icons by keyword
  searchIcons(keyword) {
    const results = []
    const lowerKeyword = keyword.toLowerCase()

    this.registry.forEach((component, name) => {
      if (name.toLowerCase().includes(lowerKeyword)) {
        results.push({ name, component })
      }
    })

    return results
  }

  // Create icon component with props
  createIconComponent(iconName, props = {}) {
    const IconComponent = this.getIcon(iconName)
    if (!IconComponent) {
      console.warn(`Icon "${iconName}" not found in registry`)
      return null
    }

    return {
      render() {
        return h(IconComponent, props)
      }
    }
  }
}

// Create singleton instance
const iconRegistry = new IconRegistry()

// Helper functions
export const getIconComponent = (iconName, props = {}) => {
  return iconRegistry.createIconComponent(iconName, props)
}

export const hasIcon = (iconName) => {
  return iconRegistry.hasIcon(iconName)
}

export const searchIcons = (keyword) => {
  return iconRegistry.searchIcons(keyword)
}

// Icon selector component helper
export const createIconSelector = (options = {}) => {
  const {
    category = null,
    searchable = true,
    placeholder = '选择图标',
    multiple = false,
    maxSelection = null
  } = options

  return {
    category,
    searchable,
    placeholder,
    multiple,
    maxSelection,
    registry: iconRegistry
  }
}

// Pre-defined icon sets for common use cases
export const COMMON_ICON_SETS = {
  // For forms
  FORM_ACTIONS: [ACTION_ICONS.SAVE, ACTION_ICONS.CANCEL, ACTION_ICONS.RESET],
  
  // For tables
  TABLE_ACTIONS: [ACTION_ICONS.VIEW, ACTION_ICONS.EDIT, ACTION_ICONS.DELETE],
  
  // For navigation menus
  MENU_ITEMS: [NAVIGATION_ICONS.HOME, NAVIGATION_ICONS.DASHBOARD, DATA_ICONS.CHART],
  
  // For sports analysis
  SPORTS_ANALYSIS: [SPORTS_ICONS.ANALYZE, SPORTS_ICONS.PREDICTION, SPORTS_ICONS.STATISTICS],
  
  // For lottery/betting
  LOTTERY_ACTIONS: [SPORTS_ICONS.LOTTERY, SPORTS_ICONS.BET, SPORTS_ICONS.ODDS, SPORTS_ICONS.WIN]
}

// Default export with all exports
export default {
  // Categories
  ICON_CATEGORIES,
  
  // Icon collections
  NAVIGATION_ICONS,
  ACTION_ICONS,
  DATA_ICONS,
  UI_ICONS,
  BUSINESS_ICONS,
  SPORTS_ICONS,
  SYSTEM_ICONS,
  
  // Registry and helpers
  iconRegistry,
  getIconComponent,
  hasIcon,
  searchIcons,
  createIconSelector,
  
  // Common sets
  COMMON_ICON_SETS,
  
  // Direct access to Element Plus icons (for backward compatibility)
  ...ElementPlusIconsVue
}