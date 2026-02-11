/**
 * 页面映射表 - 集中管理所有页面组件
 * 用于快速查找和引用页面组件，避免重复创建
 */

export const pageMap = {
  // 用户管理模块
  userManagement: {
    // 用户管理主页面
    userManagementPage: () => import('@/views/admin/UserManagement.vue'),
    
    // 用户子页面
    userList: () => import('@/views/admin/users/UserList.vue'),
    rolePermission: () => import('@/views/admin/users/RolePermission.vue'),
    departmentManagement: () => import('@/views/admin/users/DepartmentManagement.vue'),
    userProfile: () => import('@/views/admin/users/UserProfile.vue'),
    userProfileManagement: () => import('@/views/admin/users/UserProfileManagement.vue'),
    operationLog: () => import('@/views/admin/users/OperationLog.vue'),
    
    // 后端用户管理
    backendUsers: () => import('@/views/admin/users/BackendUsers.vue'),
    frontendUsers: () => import('@/views/admin/users/FrontendUsers.vue'),
  },

  // 数据源管理模块
  dataSource: {
    // 数据源主页面
    dataSourceManagementMain: () => import('@/views/admin/crawler/DataSourceManagement.vue'),  // 重命名避免冲突
    
    // 数据源子页面
    config: () => import('@/views/admin/crawler/SourceConfig.vue'),
    monitor: () => import('@/views/admin/crawler/SystemMonitor.vue'),
    taskConsole: () => import('@/views/admin/crawler/TaskConsole.vue'),
    dataCenter: () => import('@/views/admin/crawler/DataCenter.vue'),
    ipPool: () => import('@/views/admin/crawler/IpPoolManagement.vue'),
    headers: () => import('@/views/admin/crawler/HeadersManagement.vue'),
    taskScheduler: () => import('@/views/admin/crawler/TaskScheduler.vue'),
    dataIntelligenceMain: () => import('@/views/admin/crawler/DataIntelligence.vue'),  // 重命名避免冲突
  },

  // 比赛数据管理模块
  matchData: {
    // 比赛数据主页面
    matchDataManagement: () => import('@/views/admin/sp/CompetitionManagement.vue'),
    
    // 比赛数据子页面
    matches: () => import('@/views/admin/sp/CompetitionManagement.vue'),
    odds: () => import('@/views/admin/sp/OddsManagement.vue'),
    competitionManagement: () => import('@/views/admin/sp/CompetitionManagement.vue'),
    dataSourceManagement: () => import('@/views/admin/sp/DataSourceManagement.vue'),  // 此处与数据源管理模块重名
    spRecordManagement: () => import('@/views/admin/sp/SPRecordManagement.vue'),
    scheduleManagement: () => import('@/views/admin/sp/ScheduleManagement.vue'),
    dataAnalysisInsight: () => import('@/views/admin/sp/DataAnalysisInsight.vue'),
  },

  // 比赛管理模块
  match: {
    // 比赛管理主页面
    matchManagement: () => import('@/views/admin/match/MatchManagement.vue'),
    
    // 比赛子页面
    beidanSchedule: () => import('@/views/admin/match/BeidanSchedule.vue'),
    leagueConfigManagement: () => import('@/views/admin/match/LeagueConfigManagement.vue'),
    leagueManagement: () => import('@/views/admin/match/LeagueManagement.vue'),
    lotterySchedule: () => import('@/views/admin/match/LotterySchedule.vue'),
    oddsManagement: () => import('@/views/admin/match/OddsManagement.vue'),
    spiderSchedule: () => import('@/views/admin/match/SpiderSchedule.vue'),
  },

  // 平局预测管理模块
  drawPrediction: {
    // 预测管理主页面
    
    // 预测子页面

  },

  // 比赛视图模块
  matchView: {
    matchViewMain: () => import('@/views/admin/MatchView.vue'),  // 重命名避免冲突
  },

  // 情报分析模块
  intelligence: {
    // 情报分析主页面
    intelligenceManagementMain: () => import('@/views/admin/intelligence/Dashboard.vue'),  // 重命名避免冲突
    
    // 情报子页面
    screening: () => import('@/views/admin/intelligence/ScreeningManagement.vue'),
    collection: () => import('@/views/admin/intelligence/CollectionManagement.vue'),
    model: () => import('@/views/admin/intelligence/ModelManagement.vue'),
    weight: () => import('@/views/admin/intelligence/WeightManagement.vue'),
    sentiment: () => import('@/views/admin/intelligence/SentimentAnalysis.vue'),
    multimodal: () => import('@/views/admin/intelligence/MultimodalAnalysis.vue'),
    crawlerIntelligence: () => import('@/views/admin/intelligence/CrawlerIntelligence.vue'),
    dataIntelligence: () => import('@/views/admin/intelligence/DataIntelligence.vue'),  // 此处与数据源管理模块重名
    graphManagement: () => import('@/views/admin/intelligence/GraphManagement.vue'),
  },

  // AI服务管理模块
  aiServices: {
    // AI服务管理主页面
    aiServiceManagement: () => import('@/views/admin/AIManagementView.vue'),
    
    // AI服务子页面
    local: () => import('@/views/admin/ai-services/LocalAIService.vue'),
    remote: () => import('@/views/admin/ai-services/RemoteAIService.vue'),
    costMonitoring: () => import('@/views/admin/ai-services/CostMonitoring.vue'),
    agentManagement: () => import('@/views/admin/ai-services/AgentManagement.vue'),
    modelManagement: () => import('@/views/admin/ai-services/ModelManagement.vue'),
    conversationAssistant: () => import('@/views/admin/ai-services/ConversationAssistant.vue'),
    configManagement: () => import('@/views/admin/ai-services/ConfigManagement.vue'),
  },

  // 智能决策模块
  intelligentDecision: {
    // 智能决策主页面
    intelligentDecision: () => import('@/views/admin/IntelligentDecisionView.vue'),
    
    // 智能决策子页面
    hedgingManagement: () => import('@/views/admin/hedging/HedgingManagement.vue'),
    recommendationSystem: () => import('@/views/admin/intelligent-decision/RecommendationManagement.vue'),
    riskControl: () => import('@/views/admin/intelligent-decision/RiskControlManagement.vue'),
  },

  // 报告生成模块
  reports: {
    autoReports: () => import('@/views/admin/Dashboard.vue'), // 占位符，待实现
    customReports: () => import('@/views/admin/Dashboard.vue'), // 占位符，待实现
    templates: () => import('@/views/admin/Dashboard.vue'), // 占位符，待实现
    distribution: () => import('@/views/admin/Dashboard.vue'), // 占位符，待实现
  },

  // 系统管理模块
  system: {
    systemManagement: () => import('@/views/admin/SystemManagement.vue'),
    systemSettings: () => import('@/views/admin/settings/SystemSettings.vue'),
    
    // 系统设置子页面
    basicSettings: () => import('@/views/admin/settings/settings-components/BasicSettings.vue'),
    crawlerSettings: () => import('@/views/admin/settings/settings-components/CrawlerSettings.vue'),
    dataSettings: () => import('@/views/admin/settings/settings-components/DataSettings.vue'),
    notificationSettings: () => import('@/views/admin/settings/settings-components/NotificationSettings.vue'),
    securitySettings: () => import('@/views/admin/settings/settings-components/SecuritySettings.vue'),
  },

  // 统计视图模块
  stats: {
    statsView: () => import('@/views/admin/StatsView.vue'),
  },

  // 日志管理模块
  logs: {
    // 日志管理主页面
    logManagement: () => import('@/views/admin/logs/LogManagement.vue'),
    
    // 日志子页面
    overview: () => import('@/views/admin/logs/LogManagement.vue'),
    system: () => import('@/views/admin/logs/SystemLogs.vue'),
    user: () => import('@/views/admin/logs/UserLogs.vue'),
    security: () => import('@/views/admin/logs/SecurityLogs.vue'),
    api: () => import('@/views/admin/logs/APILogs.vue'),
  },

  // 前台页面
  frontend: {
    // 主页面
    home: () => import('@/views/HomeView.vue'),
    login: () => import('@/views/Login.vue'),
    dashboard: () => import('@/views/Dashboard.vue'),
    dashboardPage: () => import('@/views/DashboardPage.vue'),
    
    // 功能页面
    jczqSchedule: () => import('@/views/JczqSchedule.vue'),
    matchList: () => import('@/views/MatchListView.vue'),
    matchView: () => import('@/views/MatchView.vue'),  // 此处与模块名重名
    favorites: () => import('@/views/FavoritesView.vue'),
    filter: () => import('@/views/FilterView.vue'),
    profile: () => import('@/views/ProfileView.vue'),
    proxyPool: () => import('@/views/ProxyPool.vue'),
    
    // 管理页面
    adminDashboard: () => import('@/views/AdminDashboard.vue'),
    adminLogin: () => import('@/views/AdminLogin.vue'),
    crawlerConfig: () => import('@/views/CrawlerConfig.vue'),
    crawlerManagement: () => import('@/views/CrawlerManagement.vue'),
    crawlerSourceConfig: () => import('@/views/CrawlerSourceConfig.vue'),
    dataManagement: () => import('@/views/DataManagement.vue'),
    drawPrediction: () => import('@/views/DrawPrediction.vue'),
    intelligenceManagement: () => import('@/views/IntelligenceManagement.vue'),  // 此处与模块名重名
    spManagement: () => import('@/views/SPManagement.vue'),
    userManagement: () => import('@/views/UserManagement.vue'),
  },
};

/**
 * 查找页面组件的辅助函数
 * @param {string} module 模块名
 * @param {string} page 页面名
 * @returns {Function} 页面组件导入函数
 */
export const findPageComponent = (module, page) => {
  if (!pageMap[module]) {
    console.warn(`Module "${module}" not found in page map`);
    return null;
  }
  
  if (!pageMap[module][page]) {
    console.warn(`Page "${page}" not found in module "${module}"`);
    return null;
  }
  
  return pageMap[module][page];
};

/**
 * 获取所有模块列表
 * @returns {string[]} 模块名数组
 */
export const getAllModules = () => {
  return Object.keys(pageMap);
};

/**
 * 获取指定模块的所有页面
 * @param {string} module 模块名
 * @returns {string[]} 页面名数组
 */
export const getPagesInModule = (module) => {
  if (!pageMap[module]) {
    return [];
  }
  
  return Object.keys(pageMap[module]);
};