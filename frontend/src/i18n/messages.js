/**
 * 国际化消息配置文件
 * 包含所有语言的具体翻译内容
 */

/**
 * 中文（简体）翻译
 */
const zhCN = {
  // 通用
  common: {
    appName: '竞彩足球扫盘系统',
    loading: '加载中...',
    saving: '保存中...',
    submitting: '提交中...',
    cancel: '取消',
    confirm: '确认',
    save: '保存',
    edit: '编辑',
    delete: '删除',
    search: '搜索',
    filter: '筛选',
    clear: '清空',
    reset: '重置',
    refresh: '刷新',
    back: '返回',
    next: '下一步',
    previous: '上一步',
    close: '关闭',
    open: '打开',
    expand: '展开',
    collapse: '收起',
    more: '更多',
    less: '更少',
    all: '全部',
    none: '无',
    selectAll: '全选',
    deselectAll: '取消全选',
    actions: '操作',
    status: '状态',
    description: '描述',
    remarks: '备注',
    notes: '说明',
    tips: '提示',
    warning: '警告',
    error: '错误',
    success: '成功',
    info: '信息',
    yes: '是',
    no: '否',
    ok: '确定',
    apply: '应用',
    submit: '提交',
    upload: '上传',
    download: '下载',
    preview: '预览',
    print: '打印',
    export: '导出',
    import: '导入',
    copy: '复制',
    paste: '粘贴',
    cut: '剪切',
    undo: '撤销',
    redo: '重做',
    help: '帮助',
    settings: '设置',
    profile: '个人资料',
    logout: '退出登录',
    login: '登录',
    register: '注册',
    forgotPassword: '忘记密码',
    changePassword: '修改密码',
    rememberMe: '记住我',
    terms: '服务条款',
    privacy: '隐私政策',
    copyright: '版权声明',
    version: '版本',
    language: '语言',
    theme: '主题',
    darkMode: '深色模式',
    lightMode: '浅色模式',
    systemMode: '跟随系统'
  },
  
  // 导航
  navigation: {
    home: '首页',
    matches: '比赛',
    intelligence: '情报',
    analysis: '分析',
    comparison: '对比',
    favorites: '收藏',
    history: '历史',
    notifications: '通知',
    search: '搜索',
    settings: '设置',
    admin: '管理后台',
    dashboard: '仪表板',
    users: '用户管理',
    roles: '角色管理',
    permissions: '权限管理',
    dataSources: '数据源管理',
    matchManagement: '比赛管理',
    intelligenceManagement: '情报管理',
    dataQuality: '数据质量',
    systemConfig: '系统配置',
    monitoring: '监控运维',
    apiManagement: 'API管理',
    logs: '日志管理',
    backup: '备份恢复'
  },
  
  // 比赛相关
  matches: {
    title: '比赛',
    upcoming: '即将开始',
    live: '进行中',
    finished: '已结束',
    postponed: '延期',
    cancelled: '取消',
    allMatches: '所有比赛',
    matchDetails: '比赛详情',
    matchAnalysis: '比赛分析',
    matchPrediction: '比赛预测',
    matchComparison: '比赛对比',
    
    // 比赛状态
    status: {
      not_started: '未开始',
      in_progress: '进行中',
      finished: '已结束',
      postponed: '延期',
      cancelled: '取消',
      suspended: '中断',
      abandoned: '放弃'
    },
    
    // 比赛信息
    homeTeam: '主队',
    awayTeam: '客队',
    venue: '比赛场地',
    referee: '裁判',
    attendance: '观众人数',
    weather: '天气',
    temperature: '温度',
    humidity: '湿度',
    windSpeed: '风速',
    precipitation: '降水概率',
    
    // 比赛结果
    result: '结果',
    score: '比分',
    halftimeScore: '半场比分',
    fulltimeScore: '全场比分',
    extraTimeScore: '加时赛比分',
    penaltyScore: '点球比分',
    winner: '胜方',
    draw: '平局',
    
    // 比赛统计
    statistics: '统计',
    possession: '控球率',
    shots: '射门',
    shotsOnTarget: '射正',
    corners: '角球',
    fouls: '犯规',
    offsides: '越位',
    yellowCards: '黄牌',
    redCards: '红牌',
    passes: '传球',
    passAccuracy: '传球成功率',
    tackles: '抢断',
    interceptions: '拦截',
    clearances: '解围',
    saves: '扑救'
  },
  
  // 情报相关
  intelligence: {
    title: '情报',
    latest: '最新情报',
    important: '重要情报',
    verified: '已验证',
    unverified: '未验证',
    source: '来源',
    confidence: '置信度',
    weight: '权重',
    impact: '影响',
    
    // 情报类型
    types: {
      injury: '伤病',
      suspension: '停赛',
      lineup: '阵容',
      tactics: '战术',
      motivation: '战意',
      weather: '天气',
      referee: '裁判',
      venue: '场地',
      odds: '赔率',
      transfer: '转会',
      coach: '教练',
      historical: '历史数据',
      form: '状态',
      fatigue: '疲劳度',
      travel: '行程',
      other: '其他'
    },
    
    // 伤病信息
    injury: {
      player: '球员',
      position: '位置',
      type: '伤病类型',
      severity: '严重程度',
      expectedReturn: '预计回归',
      confirmed: '已确认',
      doubtful: '疑似',
      out: '缺席'
    },
    
    // 赔率信息
    odds: {
      title: '赔率',
      initial: '初盘',
      current: '即时',
      change: '变化',
      trend: '趋势',
      probability: '概率',
      value: '价值',
      overUnder: '大小球',
      asianHandicap: '亚洲让球',
      european: '欧洲赔率',
      homeWin: '主胜',
      draw: '平局',
      awayWin: '客胜'
    }
  },
  
  // 联赛
  leagues: {
    all: '全部联赛',
    premier_league: '英超',
    la_liga: '西甲',
    serie_a: '意甲',
    bundesliga: '德甲',
    ligue_1: '法甲',
    champions_league: '欧冠',
    europa_league: '欧联',
    world_cup: '世界杯',
    euro_cup: '欧洲杯',
    copa_america: '美洲杯',
    afc_asian_cup: '亚洲杯',
    african_cup: '非洲杯',
    mls: '美职联',
    j_league: '日职联',
    k_league: '韩职联',
    csl: '中超'
  },
  
  // 球队（示例）
  teams: {
    // 英超球队
    man_united: '曼联',
    man_city: '曼城',
    liverpool: '利物浦',
    chelsea: '切尔西',
    arsenal: '阿森纳',
    tottenham: '热刺',
    
    // 西甲球队
    real_madrid: '皇家马德里',
    barcelona: '巴塞罗那',
    atletico_madrid: '马德里竞技',
    
    // 其他示例
    bayern_munich: '拜仁慕尼黑',
    psg: '巴黎圣日耳曼',
    juventus: '尤文图斯',
    ac_milan: 'AC米兰',
    inter_milan: '国际米兰'
  },
  
  // 时间相关
  time: {
    now: '刚刚',
    minutes: '分钟',
    hours: '小时',
    days: '天',
    weeks: '周',
    months: '月',
    years: '年',
    ago: '前',
    later: '后',
    today: '今天',
    yesterday: '昨天',
    tomorrow: '明天',
    thisWeek: '本周',
    lastWeek: '上周',
    nextWeek: '下周',
    thisMonth: '本月',
    lastMonth: '上月',
    nextMonth: '下月',
    thisYear: '今年',
    lastYear: '去年',
    nextYear: '明年',
    
    // 日期
    january: '一月',
    february: '二月',
    march: '三月',
    april: '四月',
    may: '五月',
    june: '六月',
    july: '七月',
    august: '八月',
    september: '九月',
    october: '十月',
    november: '十一月',
    december: '十二月',
    
    // 星期
    monday: '星期一',
    tuesday: '星期二',
    wednesday: '星期三',
    thursday: '星期四',
    friday: '星期五',
    saturday: '星期六',
    sunday: '星期日',
    
    // 缩写
    mon: '周一',
    tue: '周二',
    wed: '周三',
    thu: '周四',
    fri: '周五',
    sat: '周六',
    sun: '周日'
  },
  
  // 表单验证
  validation: {
    required: '此字段为必填项',
    email: '请输入有效的邮箱地址',
    phone: '请输入有效的手机号码',
    password: '密码必须包含字母和数字，长度至少8位',
    passwordMismatch: '两次输入的密码不一致',
    minLength: '长度至少{min}个字符',
    maxLength: '长度不能超过{max}个字符',
    minValue: '值不能小于{min}',
    maxValue: '值不能大于{max}',
    between: '值必须在{min}和{max}之间',
    numeric: '请输入数字',
    integer: '请输入整数',
    decimal: '请输入小数',
    url: '请输入有效的URL地址',
    date: '请输入有效的日期',
    time: '请输入有效的时间',
    datetime: '请输入有效的日期时间',
    custom: '请输入有效的内容'
  },
  
  // 错误信息
  errors: {
    network: '网络连接失败，请检查网络设置',
    server: '服务器错误，请稍后重试',
    timeout: '请求超时，请稍后重试',
    unauthorized: '未授权，请重新登录',
    forbidden: '权限不足，无法访问此资源',
    notFound: '请求的资源不存在',
    conflict: '资源冲突，请检查数据',
    validation: '数据验证失败',
    unknown: '未知错误，请联系管理员',
    
    // 业务错误
    matchNotFound: '比赛不存在',
    intelligenceNotFound: '情报不存在',
    userNotFound: '用户不存在',
    dataSourceError: '数据源错误',
    crawlerError: '爬虫错误',
    processingError: '数据处理错误'
  },
  
  // 成功消息
  success: {
    saved: '保存成功',
    deleted: '删除成功',
    updated: '更新成功',
    created: '创建成功',
    uploaded: '上传成功',
    downloaded: '下载成功',
    exported: '导出成功',
    imported: '导入成功',
    operation: '操作成功',
    
    // 业务成功
    matchAdded: '比赛添加成功',
    intelligenceAdded: '情报添加成功',
    analysisComplete: '分析完成',
    predictionGenerated: '预测生成成功'
  },
  
  // 用户相关
  user: {
    profile: '个人资料',
    settings: '设置',
    account: '账户',
    security: '安全',
    notifications: '通知',
    preferences: '偏好设置',
    subscription: '订阅',
    billing: '账单',
    
    // 角色
    roles: {
      super_admin: '超级管理员',
      admin: '管理员',
      editor: '编辑',
      viewer: '查看者',
      user: '用户',
      guest: '游客'
    },
    
    // 权限
    permissions: {
      view_matches: '查看比赛',
      edit_matches: '编辑比赛',
      view_intelligence: '查看情报',
      edit_intelligence: '编辑情报',
      view_users: '查看用户',
      edit_users: '编辑用户',
      admin_access: '管理后台访问',
      export_data: '导出数据',
      import_data: '导入数据'
    }
  },
  
  // 筛选器
  filters: {
    league: '联赛',
    dateRange: '日期范围',
    timeRange: '时间范围',
    status: '状态',
    type: '类型',
    source: '来源',
    confidence: '置信度',
    weight: '权重',
    impact: '影响',
    team: '球队',
    venue: '场地',
    referee: '裁判',
    
    // 操作
    applyFilters: '应用筛选',
    clearFilters: '清空筛选',
    saveFilter: '保存筛选',
    loadFilter: '加载筛选',
    resetFilters: '重置筛选'
  },
  
  // 统计数据
  stats: {
    totalMatches: '总比赛数',
    totalIntelligence: '总情报数',
    activeUsers: '活跃用户',
    successRate: '成功率',
    accuracy: '准确率',
    coverage: '覆盖率',
    timeliness: '及时性',
    completeness: '完整性',
    
    // 图表
    chart: {
      matchesByLeague: '联赛比赛分布',
      intelligenceByType: '情报类型分布',
      trends: '趋势图',
      comparison: '对比图',
      distribution: '分布图',
      correlation: '相关性图'
    }
  },
  
  // 管理后台
  admin: {
    dashboard: '仪表板',
    overview: '概览',
    analytics: '分析',
    monitoring: '监控',
    configuration: '配置',
    maintenance: '维护',
    
    // 数据质量
    dataQuality: {
      title: '数据质量',
      completeness: '完整性',
      accuracy: '准确性',
      timeliness: '及时性',
      consistency: '一致性',
      validity: '有效性',
      score: '质量评分'
    },
    
    // 监控
    monitoring: {
      title: '监控',
      system: '系统监控',
      performance: '性能监控',
      business: '业务监控',
      alerts: '告警',
      logs: '日志'
    }
  },
  
  // 工具提示
  tooltips: {
    refreshData: '刷新数据',
    toggleTheme: '切换主题',
    toggleLanguage: '切换语言',
    viewDetails: '查看详情',
    editItem: '编辑项目',
    deleteItem: '删除项目',
    addToFavorites: '添加到收藏',
    removeFromFavorites: '从收藏移除',
    compareMatches: '对比比赛',
    analyzeMatch: '分析比赛',
    predictOutcome: '预测结果',
    share: '分享',
    help: '帮助'
  }
};

/**
 * 英文（美国）翻译
 */
const enUS = {
  // Common
  common: {
    appName: 'Soccer Scanning System',
    loading: 'Loading...',
    saving: 'Saving...',
    submitting: 'Submitting...',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    edit: 'Edit',
    delete: 'Delete',
    search: 'Search',
    filter: 'Filter',
    clear: 'Clear',
    reset: 'Reset',
    refresh: 'Refresh',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    close: 'Close',
    open: 'Open',
    expand: 'Expand',
    collapse: 'Collapse',
    more: 'More',
    less: 'Less',
    all: 'All',
    none: 'None',
    selectAll: 'Select All',
    deselectAll: 'Deselect All',
    actions: 'Actions',
    status: 'Status',
    description: 'Description',
    remarks: 'Remarks',
    notes: 'Notes',
    tips: 'Tips',
    warning: 'Warning',
    error: 'Error',
    success: 'Success',
    info: 'Info',
    yes: 'Yes',
    no: 'No',
    ok: 'OK',
    apply: 'Apply',
    submit: 'Submit',
    upload: 'Upload',
    download: 'Download',
    preview: 'Preview',
    print: 'Print',
    export: 'Export',
    import: 'Import',
    copy: 'Copy',
    paste: 'Paste',
    cut: 'Cut',
    undo: 'Undo',
    redo: 'Redo',
    help: 'Help',
    settings: 'Settings',
    profile: 'Profile',
    logout: 'Logout',
    login: 'Login',
    register: 'Register',
    forgotPassword: 'Forgot Password',
    changePassword: 'Change Password',
    rememberMe: 'Remember Me',
    terms: 'Terms of Service',
    privacy: 'Privacy Policy',
    copyright: 'Copyright',
    version: 'Version',
    language: 'Language',
    theme: 'Theme',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    systemMode: 'Follow System'
  },
  
  // Navigation
  navigation: {
    home: 'Home',
    matches: 'Matches',
    intelligence: 'Intelligence',
    analysis: 'Analysis',
    comparison: 'Comparison',
    favorites: 'Favorites',
    history: 'History',
    notifications: 'Notifications',
    search: 'Search',
    settings: 'Settings',
    admin: 'Admin Panel',
    dashboard: 'Dashboard',
    users: 'User Management',
    roles: 'Role Management',
    permissions: 'Permission Management',
    dataSources: 'Data Source Management',
    matchManagement: 'Match Management',
    intelligenceManagement: 'Intelligence Management',
    dataQuality: 'Data Quality',
    systemConfig: 'System Configuration',
    monitoring: 'Monitoring & Operations',
    apiManagement: 'API Management',
    logs: 'Log Management',
    backup: 'Backup & Restore'
  },
  
  // Matches
  matches: {
    title: 'Matches',
    upcoming: 'Upcoming',
    live: 'Live',
    finished: 'Finished',
    postponed: 'Postponed',
    cancelled: 'Cancelled',
    allMatches: 'All Matches',
    matchDetails: 'Match Details',
    matchAnalysis: 'Match Analysis',
    matchPrediction: 'Match Prediction',
    matchComparison: 'Match Comparison',
    
    // Match status
    status: {
      not_started: 'Not Started',
      in_progress: 'In Progress',
      finished: 'Finished',
      postponed: 'Postponed',
      cancelled: 'Cancelled',
      suspended: 'Suspended',
      abandoned: 'Abandoned'
    },
    
    // Match information
    homeTeam: 'Home Team',
    awayTeam: 'Away Team',
    venue: 'Venue',
    referee: 'Referee',
    attendance: 'Attendance',
    weather: 'Weather',
    temperature: 'Temperature',
    humidity: 'Humidity',
    windSpeed: 'Wind Speed',
    precipitation: 'Precipitation',
    
    // Match results
    result: 'Result',
    score: 'Score',
    halftimeScore: 'Halftime Score',
    fulltimeScore: 'Fulltime Score',
    extraTimeScore: 'Extra Time Score',
    penaltyScore: 'Penalty Score',
    winner: 'Winner',
    draw: 'Draw',
    
    // Match statistics
    statistics: 'Statistics',
    possession: 'Possession',
    shots: 'Shots',
    shotsOnTarget: 'Shots on Target',
    corners: 'Corners',
    fouls: 'Fouls',
    offsides: 'Offsides',
    yellowCards: 'Yellow Cards',
    redCards: 'Red Cards',
    passes: 'Passes',
    passAccuracy: 'Pass Accuracy',
    tackles: 'Tackles',
    interceptions: 'Interceptions',
    clearances: 'Clearances',
    saves: 'Saves'
  },
  
  // Intelligence
  intelligence: {
    title: 'Intelligence',
    latest: 'Latest Intelligence',
    important: 'Important Intelligence',
    verified: 'Verified',
    unverified: 'Unverified',
    source: 'Source',
    confidence: 'Confidence',
    weight: 'Weight',
    impact: 'Impact',
    
    // Intelligence types
    types: {
      injury: 'Injury',
      suspension: 'Suspension',
      lineup: 'Lineup',
      tactics: 'Tactics',
      motivation: 'Motivation',
      weather: 'Weather',
      referee: 'Referee',
      venue: 'Venue',
      odds: 'Odds',
      transfer: 'Transfer',
      coach: 'Coach',
      historical: 'Historical Data',
      form: 'Form',
      fatigue: 'Fatigue',
      travel: 'Travel',
      other: 'Other'
    },
    
    // Injury information
    injury: {
      player: 'Player',
      position: 'Position',
      type: 'Injury Type',
      severity: 'Severity',
      expectedReturn: 'Expected Return',
      confirmed: 'Confirmed',
      doubtful: 'Doubtful',
      out: 'Out'
    },
    
    // Odds information
    odds: {
      title: 'Odds',
      initial: 'Initial',
      current: 'Current',
      change: 'Change',
      trend: 'Trend',
      probability: 'Probability',
      value: 'Value',
      overUnder: 'Over/Under',
      asianHandicap: 'Asian Handicap',
      european: 'European',
      homeWin: 'Home Win',
      draw: 'Draw',
      awayWin: 'Away Win'
    }
  },
  
  // Leagues
  leagues: {
    all: 'All Leagues',
    premier_league: 'Premier League',
    la_liga: 'La Liga',
    serie_a: 'Serie A',
    bundesliga: 'Bundesliga',
    ligue_1: 'Ligue 1',
    champions_league: 'Champions League',
    europa_league: 'Europa League',
    world_cup: 'World Cup',
    euro_cup: 'European Championship',
    copa_america: 'Copa America',
    afc_asian_cup: 'AFC Asian Cup',
    african_cup: 'African Cup of Nations',
    mls: 'MLS',
    j_league: 'J.League',
    k_league: 'K League',
    csl: 'Chinese Super League'
  },
  
  // Teams (examples)
  teams: {
    // Premier League
    man_united: 'Manchester United',
    man_city: 'Manchester City',
    liverpool: 'Liverpool',
    chelsea: 'Chelsea',
    arsenal: 'Arsenal',
    tottenham: 'Tottenham Hotspur',
    
    // La Liga
    real_madrid: 'Real Madrid',
    barcelona: 'Barcelona',
    atletico_madrid: 'Atlético Madrid',
    
    // Other examples
    bayern_munich: 'Bayern Munich',
    psg: 'Paris Saint-Germain',
    juventus: 'Juventus',
    ac_milan: 'AC Milan',
    inter_milan: 'Inter Milan'
  },
  
  // Time
  time: {
    now: 'Just now',
    minutes: 'minutes',
    hours: 'hours',
    days: 'days',
    weeks: 'weeks',
    months: 'months',
    years: 'years',
    ago: 'ago',
    later: 'later',
    today: 'Today',
    yesterday: 'Yesterday',
    tomorrow: 'Tomorrow',
    thisWeek: 'This Week',
    lastWeek: 'Last Week',
    nextWeek: 'Next Week',
    thisMonth: 'This Month',
    lastMonth: 'Last Month',
    nextMonth: 'Next Month',
    thisYear: 'This Year',
    lastYear: 'Last Year',
    nextYear: 'Next Year',
    
    // Months
    january: 'January',
    february: 'February',
    march: 'March',
    april: 'April',
    may: 'May',
    june: 'June',
    july: 'July',
    august: 'August',
    september: 'September',
    october: 'October',
    november: 'November',
    december: 'December',
    
    // Days of week
    monday: 'Monday',
    tuesday: 'Tuesday',
    wednesday: 'Wednesday',
    thursday: 'Thursday',
    friday: 'Friday',
    saturday: 'Saturday',
    sunday: 'Sunday',
    
    // Abbreviations
    mon: 'Mon',
    tue: 'Tue',
    wed: 'Wed',
    thu: 'Thu',
    fri: 'Fri',
    sat: 'Sat',
    sun: 'Sun'
  },
  
  // Validation
  validation: {
    required: 'This field is required',
    email: 'Please enter a valid email address',
    phone: 'Please enter a valid phone number',
    password: 'Password must contain letters and numbers, at least 8 characters',
    passwordMismatch: 'Passwords do not match',
    minLength: 'Minimum length is {min} characters',
    maxLength: 'Maximum length is {max} characters',
    minValue: 'Value must be at least {min}',
    maxValue: 'Value must be at most {max}',
    between: 'Value must be between {min} and {max}',
    numeric: 'Please enter a number',
    integer: 'Please enter an integer',
    decimal: 'Please enter a decimal number',
    url: 'Please enter a valid URL',
    date: 'Please enter a valid date',
    time: 'Please enter a valid time',
    datetime: 'Please enter a valid date and time',
    custom: 'Please enter valid content'
  },
  
  // Errors
  errors: {
    network: 'Network connection failed, please check your network settings',
    server: 'Server error, please try again later',
    timeout: 'Request timeout, please try again later',
    unauthorized: 'Unauthorized, please login again',
    forbidden: 'Insufficient permissions to access this resource',
    notFound: 'Requested resource not found',
    conflict: 'Resource conflict, please check data',
    validation: 'Data validation failed',
    unknown: 'Unknown error, please contact administrator',
    
    // Business errors
    matchNotFound: 'Match not found',
    intelligenceNotFound: 'Intelligence not found',
    userNotFound: 'User not found',
    dataSourceError: 'Data source error',
    crawlerError: 'Crawler error',
    processingError: 'Data processing error'
  },
  
  // Success messages
  success: {
    saved: 'Saved successfully',
    deleted: 'Deleted successfully',
    updated: 'Updated successfully',
    created: 'Created successfully',
    uploaded: 'Uploaded successfully',
    downloaded: 'Downloaded successfully',
    exported: 'Exported successfully',
    imported: 'Imported successfully',
    operation: 'Operation successful',
    
    // Business success
    matchAdded: 'Match added successfully',
    intelligenceAdded: 'Intelligence added successfully',
    analysisComplete: 'Analysis completed',
    predictionGenerated: 'Prediction generated successfully'
  },
  
  // User
  user: {
    profile: 'Profile',
    settings: 'Settings',
    account: 'Account',
    security: 'Security',
    notifications: 'Notifications',
    preferences: 'Preferences',
    subscription: 'Subscription',
    billing: 'Billing',
    
    // Roles
    roles: {
      super_admin: 'Super Admin',
      admin: 'Admin',
      editor: 'Editor',
      viewer: 'Viewer',
      user: 'User',
      guest: 'Guest'
    },
    
    // Permissions
    permissions: {
      view_matches: 'View Matches',
      edit_matches: 'Edit Matches',
      view_intelligence: 'View Intelligence',
      edit_intelligence: 'Edit Intelligence',
      view_users: 'View Users',
      edit_users: 'Edit Users',
      admin_access: 'Admin Panel Access',
      export_data: 'Export Data',
      import_data: 'Import Data'
    }
  },
  
  // Filters
  filters: {
    league: 'League',
    dateRange: 'Date Range',
    timeRange: 'Time Range',
    status: 'Status',
    type: 'Type',
    source: 'Source',
    confidence: 'Confidence',
    weight: 'Weight',
    impact: 'Impact',
    team: 'Team',
    venue: 'Venue',
    referee: 'Referee',
    
    // Actions
    applyFilters: 'Apply Filters',
    clearFilters: 'Clear Filters',
    saveFilter: 'Save Filter',
    loadFilter: 'Load Filter',
    resetFilters: 'Reset Filters'
  },
  
  // Statistics
  stats: {
    totalMatches: 'Total Matches',
    totalIntelligence: 'Total Intelligence',
    activeUsers: 'Active Users',
    successRate: 'Success Rate',
    accuracy: 'Accuracy',
    coverage: 'Coverage',
    timeliness: 'Timeliness',
    completeness: 'Completeness',
    
    // Charts
    chart: {
      matchesByLeague: 'Matches by League',
      intelligenceByType: 'Intelligence by Type',
      trends: 'Trends Chart',
      comparison: 'Comparison Chart',
      distribution: 'Distribution Chart',
      correlation: 'Correlation Chart'
    }
  },
  
  // Admin panel
  admin: {
    dashboard: 'Dashboard',
    overview: 'Overview',
    analytics: 'Analytics',
    monitoring: 'Monitoring',
    configuration: 'Configuration',
    maintenance: 'Maintenance',
    
    // Data quality
    dataQuality: {
      title: 'Data Quality',
      completeness: 'Completeness',
      accuracy: 'Accuracy',
      timeliness: 'Timeliness',
      consistency: 'Consistency',
      validity: 'Validity',
      score: 'Quality Score'
    },
    
    // Monitoring
    monitoring: {
      title: 'Monitoring',
      system: 'System Monitoring',
      performance: 'Performance Monitoring',
      business: 'Business Monitoring',
      alerts: 'Alerts',
      logs: 'Logs'
    }
  },
  
  // Tooltips
  tooltips: {
    refreshData: 'Refresh Data',
    toggleTheme: 'Toggle Theme',
    toggleLanguage: 'Toggle Language',
    viewDetails: 'View Details',
    editItem: 'Edit Item',
    deleteItem: 'Delete Item',
    addToFavorites: 'Add to Favorites',
    removeFromFavorites: 'Remove from Favorites',
    compareMatches: 'Compare Matches',
    analyzeMatch: 'Analyze Match',
    predictOutcome: 'Predict Outcome',
    share: 'Share',
    help: 'Help'
  }
};

/**
 * 日语翻译（示例）
 */
const jaJP = {
  common: {
    appName: 'サッカースキャニングシステム',
    loading: '読み込み中...',
    save: '保存',
    cancel: 'キャンセル',
    confirm: '確認'
  },
  // ... 其他日语翻译
};

/**
 * 韩语翻译（示例）
 */
const koKR = {
  common: {
    appName: '축구 스캐닝 시스템',
    loading: '로딩 중...',
    save: '저장',
    cancel: '취소',
    confirm: '확인'
  },
  // ... 其他韩语翻译
};

/**
 * 导出所有语言的消息配置
 */
export const messages = {
  'zh-CN': zhCN,
  'en-US': enUS,
  'ja-JP': jaJP,
  'ko-KR': koKR
};

/**
 * 导出单个语言的翻译，方便按需加载
 */
export const languagePacks = {
  zhCN,
  enUS,
  jaJP,
  koKR
};

/**
 * 获取语言包中的翻译键值对
 * @param {string} locale - 语言代码
 * @returns {Object} 该语言的翻译对象
 */
export function getLanguagePack(locale) {
  return messages[locale] || messages['zh-CN'];
}

/**
 * 获取扁平化的翻译键值对（用于搜索）
 * @param {string} locale - 语言代码
 * @returns {Object} 扁平化的翻译对象
 */
export function getFlatTranslations(locale) {
  const translations = {};
  const languagePack = getLanguagePack(locale);
  
  const flatten = (obj, prefix = '') => {
    for (const key in obj) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      if (typeof obj[key] === 'string') {
        translations[fullKey] = obj[key];
      } else if (typeof obj[key] === 'object') {
        flatten(obj[key], fullKey);
      }
    }
  };
  
  flatten(languagePack);
  return translations;
}

/**
 * 搜索翻译内容
 * @param {string} query - 搜索关键词
 * @param {string} locale - 语言代码
 * @returns {Array} 搜索结果
 */
export function searchTranslations(query, locale = 'zh-CN') {
  const translations = getFlatTranslations(locale);
  const results = [];
  
  for (const key in translations) {
    const value = translations[key];
    if (value.toLowerCase().includes(query.toLowerCase())) {
      results.push({
        key,
        value,
        path: key.split('.')
      });
    }
  }
  
  return results;
}

export default messages;