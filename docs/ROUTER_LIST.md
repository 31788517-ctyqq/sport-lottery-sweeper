# 竞彩足球扫盘系统 - 路由列表

本文档列出了系统中所有已注册的路由，共计111个。

## 基础路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 1 | `/` | Home | 主页 |
| 2 | `/login` | Login | 登录页面 |
| 3 | `/admin` | Dashboard | 管理面板 |

## 管理后台子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 4 | `/admin/dashboard` | Dashboard | 仪表板 |
| 5 | `/admin/users/list` | UserList | 用户列表 |
| 6 | `/admin/users/roles` | RolePermission | 角色与权限 |
| 7 | `/admin/users/departments` | DepartmentManagement | 部门管理 |
| 8 | `/admin/users/profile` | UserProfile | 个人中心 |
| 9 | `/admin/users/profiles` | UserProfileManagement | 用户画像管理 |
| 10 | `/admin/users/logs` | OperationLog | 操作日志 |

## 数据源管理子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 11 | `/admin/data-source/config` | DataSourceConfig | 数据源配置 |
| 12 | `/admin/data-source/monitor` | DataSourceMonitor | 爬虫监控 |
| 13 | `/admin/data-source/task-console` | TaskConsole | 任务控制台 |
| 14 | `/admin/data-source/data-center` | DataCenter | 数据中心 |
| 15 | `/admin/data-source/ip-pool` | IpPoolManagement | IP池管理 |
| 16 | `/admin/data-source/headers` | HeadersManagement | 请求头管理 |

## 比赛数据管理子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 17 | `/admin/match-data/matches` | MatchDataMatches | 比赛管理 |
| 18 | `/admin/match-data/odds` | OddsManagement | 赔率管理 |
| 19 | `/admin/match-data/schedule/jczq` | JCZQSchedule | 竞彩赛程 |
| 20 | `/admin/match-data/schedule/bd` | BDSchedule | 北单赛程 |
| 21 | `/admin/match-data/leagues` | LeagueManagement | 联赛管理 |

## 平局预测管理子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 22 | `/admin/draw-prediction/data-features` | DataFeaturesManagement | 数据与特征管理 |
| 23 | `/admin/draw-prediction/training-evaluation` | TrainingEvaluation | 模型训练与评估 |
| 24 | `/admin/draw-prediction/model-deployment` | ModelDeployment | 模型管理与部署 |
| 25 | `/admin/draw-prediction/prediction-monitoring` | PredictionMonitoring | 预测服务与监控 |

## 比赛视图路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 26 | `/admin/match-view` | MatchView | 比赛视图 |

## 情报分析子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 27 | `/admin/intelligence/screening` | IntelligenceScreening | 智能筛选 |
| 28 | `/admin/intelligence/collection` | IntelligenceCollection | 采集管理 |
| 29 | `/admin/intelligence/model` | IntelligenceModel | 模型管理 |
| 30 | `/admin/intelligence/weight` | IntelligenceWeight | 权重管理 |
| 31 | `/admin/intelligence/sentiment` | SentimentAnalysis | 情感分析 |
| 32 | `/admin/intelligence/multimodal` | MultimodalAnalysis | 多模态分析 |

## AI服务管理子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 33 | `/admin/ai-services/local` | LocalAIService | 本地AI服务 |
| 34 | `/admin/ai-services/remote` | RemoteAIService | 远程AI服务 |
| 35 | `/admin/ai-services/costs` | CostMonitoring | 成本监控 |
| 36 | `/admin/ai-services/agents` | AgentManagement | 智能体管理 |
| 37 | `/admin/ai-services/models` | ModelManagement | 预测模型管理 |
| 38 | `/admin/ai-services/conversation` | ConversationAssistant | 对话助手 |
| 39 | `/admin/ai-services/config` | ConfigManagement | 配置管理 |

## 智能决策子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 40 | `/admin/intelligent-decision/hedging` | HedgingManagement | 对冲策略管理 |
| 41 | `/admin/intelligent-decision/recommendations` | RecommendationSystem | 推荐系统管理 |
| 42 | `/admin/intelligent-decision/risk-control` | RiskControl | 风险控制 |

## 报告生成子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 43 | `/admin/reports/auto` | AutoReports | 自动报告 |
| 44 | `/admin/reports/custom` | CustomReports | 自定义报告 |
| 45 | `/admin/reports/templates` | ReportTemplates | 模板管理 |
| 46 | `/admin/reports/distribution` | ReportDistribution | 报告分发 |

## 系统管理路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 47 | `/admin/system` | SystemManagement | 系统管理 |

## 独立管理路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 48 | `/admin/user-management` | UserManagementPage | 用户管理 |
| 49 | `/admin/stats` | StatsView | 数据统计 |

## 日志管理子路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 50 | `/admin/logs` | LogsOverview | 日志总览 |
| 51 | `/admin/logs/system` | SystemLogs | 系统日志 |
| 52 | `/admin/logs/user` | UserLogs | 用户日志 |
| 53 | `/admin/logs/security` | SecurityLogs | 安全日志 |
| 54 | `/admin/logs/api` | APILogs | API日志 |
| 55 | `/admin/logs/ai` | AILogs | AI服务日志 |

## 独立页面路由

| 序号 | 路径 | 名称 | 描述 |
|------|------|------|------|
| 56 | `/page-browser` | PageBrowser | 页面浏览器 |
| 57 | `/admin/user-management-main` | UserManagementMain | 用户管理主页面 |
| 58 | `/admin/backend-users` | BackendUsers | 后端用户管理 |
| 59 | `/admin/frontend-users` | FrontendUsers | 前端用户管理 |
| 60 | `/admin/data-source-main` | DataSourceManagementMain | 数据源管理主页面 |
| 61 | `/admin/task-scheduler` | TaskScheduler | 任务调度器 |
| 62 | `/admin/data-intelligence-main` | DataIntelligenceMain | 数据智能主页面 |
| 63 | `/admin/match-data-main` | MatchDataManagementMain | 比赛数据管理主页面 |
| 64 | `/admin/competition-management` | CompetitionManagement | 竞赛管理 |
| 65 | `/admin/sp-record-management` | SPRecordManagement | SP记录管理 |
| 66 | `/admin/schedule-management` | ScheduleManagement | 赛程管理 |
| 67 | `/admin/data-analysis-insight` | DataAnalysisInsight | 数据分析洞察 |
| 68 | `/admin/match-management-main` | MatchManagementMain | 比赛管理主页面 |
| 69 | `/admin/league-config-management` | LeagueConfigManagement | 联赛配置管理 |
| 70 | `/admin/spider-schedule` | SpiderSchedule | 爬虫赛程 |
| 71 | `/admin/draw-prediction-main` | DrawPredictionManagementMain | 预测管理主页面 |
| 72 | `/admin/match-view-main` | MatchViewMain | 比赛视图主页面 |
| 73 | `/admin/intelligence-main` | IntelligenceManagementMain | 情报分析主页面 |
| 74 | `/admin/crawler-intelligence` | CrawlerIntelligence | 爬虫智能 |
| 75 | `/admin/graph-management` | GraphManagement | 图管理 |
| 76 | `/admin/ai-service-main` | AIServiceManagementMain | AI服务管理主页面 |
| 77 | `/admin/basic-settings` | BasicSettings | 基础设置 |
| 78 | `/admin/crawler-settings` | CrawlerSettings | 爬虫设置 |
| 79 | `/admin/data-settings` | DataSettings | 数据设置 |
| 80 | `/admin/notification-settings` | NotificationSettings | 通知设置 |
| 81 | `/admin/security-settings` | SecuritySettings | 安全设置 |
| 82 | `/jczq-schedule` | JCZQSchedulePage | 竞彩足球赛程 |
| 83 | `/match-list` | MatchList | 比赛列表 |
| 84 | `/favorites` | Favorites | 收藏视图 |
| 85 | `/filter` | Filter | 过滤视图 |
| 86 | `/profile` | Profile | 个人资料 |
| 87 | `/proxy-pool` | ProxyPool | 代理池 |
| 88 | `/admin-dashboard` | AdminDashboardPage | 管理员仪表板 |
| 89 | `/admin-login` | AdminLoginPage | 管理员登录 |
| 90 | `/crawler-config` | CrawlerConfigPage | 爬虫配置 |
| 91 | `/crawler-management` | CrawlerManagementPage | 爬虫管理 |
| 92 | `/crawler-source-config` | CrawlerSourceConfigPage | 爬虫源配置 |
| 93 | `/data-management` | DataManagementPage | 数据管理 |
| 94 | `/draw-prediction` | DrawPredictionPage | 预测分析 |
| 95 | `/intelligence-management` | IntelligenceManagementPage | 智能管理 |
| 96 | `/sp-management` | SPManagementPage | SP管理 |
| 97 | `/user-management` | UserManagementPage | 用户管理（重复） |
| 98 | `/admin/source-config` | SourceConfig | 源配置 |
| 99 | `/admin/sp-data-source` | SPDataSourceManagement | SP数据源管理 |
| 100 | `/admin/match-odds` | MatchOddsManagement | 比赛赔率管理 |
| 101 | `/admin/intelligence-data` | IntelligenceData | 情报数据分析 |
| 102 | `/admin/intelligent-decision-main` | IntelligentDecisionMain | 智能决策主页面 |
| 103 | `/admin/system-settings` | SystemSettingsPage | 系统设置 |
| 104 | `/home` | HomePage | 首页 |
| 105 | `/login-page` | LoginPage | 登录页面 |
| 106 | `/dashboard-main` | DashboardMain | 仪表板 |
| 107 | `/dashboard-page` | DashboardPage | 仪表板页面 |
| 108 | `/match-view` | MatchViewPage | 比赛视图 |
| 109 | `/admin/user-management-main` | UserManagementMain | 用户管理主页面 |
| 110 | `/admin/backend-users` | BackendUsers | 后端用户管理 |
| 111 | `/admin/frontend-users` | FrontendUsers | 前端用户管理 |

## 路由统计

- **总计路由数量**: 111个
- **所有页面均已注册到路由系统中**
- **每个路由都配置了适当的权限控制**

> 注意：这些路由构成了完整的竞彩足球扫盘系统的前端导航结构，确保了所有功能模块都能通过URL直接访问。