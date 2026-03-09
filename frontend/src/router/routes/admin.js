import Layout from '@/layout/Index.vue'

// Admin dashboard sub-routes
const dashboardRoutes = [
  {
    path: 'dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { 
      title: '管理仪表板',
      icon: 'Dashboard',
      breadcrumb: ['管理后台', '仪表板']
    }
  }
]

// Intelligence management routes
const intelligenceRoutes = [
  {
    path: 'intelligence',
    component: () => import('@/components/IntelligenceLayout.vue'),
    meta: { 
      title: '情报管理',
      icon: 'Collection',
      breadcrumb: ['管理后台', '情报管理']
    },
    children: [
      {
        path: 'screening',
        name: 'ScreeningManagement',
        component: () => import('@/views/admin/intelligence/ScreeningManagement.vue'),
        meta: { 
          title: '信息筛选',
          breadcrumb: ['管理后台', '情报管理', '信息筛选']
        }
      },
      {
        path: 'collection',
        name: 'CollectionManagement',
        component: () => import('@/views/admin/intelligence/CollectionManagement.vue'),
        meta: { 
          title: '信息采集',
          breadcrumb: ['管理后台', '情报管理', '信息采集']
        }
      },
      {
        path: 'model',
        name: 'ModelManagement',
        component: () => import('@/views/admin/intelligence/ModelManagement.vue'),
        meta: { 
          title: '情报模型',
          breadcrumb: ['管理后台', '情报管理', '情报模型']
        }
      },
      {
        path: 'weight',
        name: 'WeightManagement',
        component: () => import('@/views/admin/intelligence/WeightManagement.vue'),
        meta: { 
          title: '情报权重',
          breadcrumb: ['管理后台', '情报管理', '情报权重']
        }
      },
      {
        path: 'graph',
        name: 'GraphManagement',
        component: () => import('@/views/admin/intelligence/GraphManagement.vue'),
        meta: { 
          title: '情报图谱',
          breadcrumb: ['管理后台', '情报管理', '情报图谱']
        }
      },
      {
        path: 'data-intelligence',
        name: 'DataIntelligence',
        component: () => import('@/views/admin/intelligence/DataIntelligence.vue'),
        meta: { 
          title: '数据情报',
          breadcrumb: ['管理后台', '情报管理', '数据情报']
        }
      }
    ]
  }
]

// User management routes
const userRoutes = [
  {
    path: 'users',
    name: 'UserManagement',
    meta: { 
      title: '用户管理',
      icon: 'User',
      breadcrumb: ['管理后台', '用户管理']
    },
    children: [
      {
        path: 'frontend',
        name: 'FrontendUsers',
        component: () => import('@/views/admin/users/FrontendUsers.vue'),
        meta: { 
          title: '前台用户',
          breadcrumb: ['管理后台', '用户管理', '前台用户']
        }
      },
      {
        path: 'backend',
        name: 'BackendUsers',
        component: () => import('@/views/admin/users/BackendUsers.vue'),
        meta: { 
          title: '后台用户',
          breadcrumb: ['管理后台', '用户管理', '后台用户']
        }
      }
    ]
  }
]

// Crawler management routes
const crawlerRoutes = [
  {
    path: 'crawler',
    name: 'CrawlerManagement',
    meta: { 
      title: '爬虫管理',
      icon: 'SetUp',
      breadcrumb: ['管理后台', '爬虫管理']
    },
    children: [
      {
        path: 'source-config',
        name: 'SourceConfigManagement',
        component: () => import('@/views/admin/crawler/SourceConfig.vue'),
        meta: { 
          title: '源配置',
          breadcrumb: ['管理后台', '爬虫管理', '源配置']
        }
      },
      {
        path: 'data-source',
        name: 'DataSourceManagement',
        component: () => import('@/views/admin/crawler/DataSource.vue'),
        meta: { 
          title: '数据源管理',
          breadcrumb: ['管理后台', '爬虫管理', '数据源管理']
        }
      },
      {
        path: 'task-scheduler',
        name: 'TaskSchedulerManagement',
        component: () => import('@/views/admin/crawler/TaskScheduler.vue'),
        meta: { 
          title: '任务调度',
          breadcrumb: ['管理后台', '爬虫管理', '任务调度']
        }
      },
      {
        path: 'data-intelligence',
        name: 'DataIntelligenceManagement',
        component: () => import('@/views/admin/crawler/DataIntelligence.vue'),
        meta: { 
          title: '数据情报',
          breadcrumb: ['管理后台', '爬虫管理', '数据情报']
        }
      }
    ]
  }
]

// SP management routes
const spRoutes = [
  {
    path: 'sp',
    name: 'SpManagement',
    meta: { 
      title: '足球SP管理',
      icon: 'Calendar',
      breadcrumb: ['管理后台', '足球SP管理']
    },
    children: [
      {
        path: 'data-sources',
        name: 'SpDataSources',
        component: () => import('@/views/admin/sp/DataSourceManagement.vue'),
        meta: { 
          title: '数据源管理',
          breadcrumb: ['管理后台', '足球SP管理', '数据源管理']
        }
      },
      {
        path: 'matches',
        name: 'SpMatches',
        component: () => import('@/views/admin/sp/MatchManagement.vue'),
        meta: { 
          title: '比赛信息管理',
          breadcrumb: ['管理后台', '足球SP管理', '比赛信息管理']
        }
      },
      {
        path: 'records',
        name: 'SpRecords',
        component: () => import('@/views/admin/sp/SPRecordManagement.vue'),
        meta: { 
          title: 'SP值管理',
          breadcrumb: ['管理后台', '足球SP管理', 'SP值管理']
        }
      },
      {
        path: 'analysis',
        name: 'SpAnalysis',
        component: () => import('@/views/admin/sp/DataAnalysisInsight.vue'),
        meta: { 
          title: '数据分析与洞察',
          breadcrumb: ['管理后台', '足球SP管理', '数据分析与洞察']
        }
      }
    ]
  }
]

// Draw prediction management routes
const drawPredictionRoutes = [
  {
    path: 'draw-prediction',
    name: 'DrawPredictionManagement',
    meta: { 
      title: '平局预测管理',
      icon: 'Platform',
      breadcrumb: ['管理后台', '平局预测管理']
    },
    children: [
      {
        path: 'data-feature',
        name: 'DrawDataFeature',
        component: () => import('@/views/admin/draw_prediction/DrawDataFeature.vue'),
        meta: { 
          title: '数据特征工程',
          breadcrumb: ['管理后台', '平局预测管理', '数据特征工程']
        }
      },
      {
        path: 'model-train-eval',
        name: 'DrawModelTrainEval',
        component: () => import('@/views/admin/draw_prediction/DrawModelTrainEval.vue'),
        meta: { 
          title: '模型训练与评估',
          breadcrumb: ['管理后台', '平局预测管理', '模型训练与评估']
        }
      },
      {
        path: 'manage-deploy',
        name: 'DrawModelManageDeploy',
        component: () => import('@/views/admin/draw_prediction/DrawModelManageDeploy.vue'),
        meta: { 
          title: '模型管理与部署',
          breadcrumb: ['管理后台', '平局预测管理', '模型管理与部署']
        }
      },
      {
        path: 'prediction-monitor',
        name: 'DrawPredictionMonitor',
        component: () => import('@/views/admin/draw_prediction/DrawPredictionMonitor.vue'),
        meta: { 
          title: '预测监控',
          breadcrumb: ['管理后台', '平局预测管理', '预测监控']
        }
      }
    ]
  }
]

// Match schedule routes
const matchScheduleRoutes = [
  {
    path: 'match-schedule',
    name: 'MatchSchedule',
    meta: { 
      title: '比赛赛程',
      icon: 'Timer',
      breadcrumb: ['管理后台', '比赛赛程']
    },
    children: [
      {
        path: 'lottery',
        name: 'LotterySchedule',
        component: () => import('@/views/admin/match/LotterySchedule.vue'),
        meta: { 
          title: '竞彩赛程',
          breadcrumb: ['管理后台', '比赛赛程', '竞彩赛程']
        }
      }
    ]
  }
]

// Data statistics routes
const dataStatisticsRoutes = [
  {
    path: 'data',
    name: 'DataStatistics',
    component: () => import('@/views/admin/Data.vue'),
    meta: { 
      title: '数据统计',
      icon: 'DataAnalysis',
      breadcrumb: ['管理后台', '数据统计']
    }
  }
]

// System settings route
const systemRoute = [
  {
    path: 'system',
    name: 'SystemSettings',
    component: () => import('@/views/admin/System.vue'),
    meta: { 
      title: '系统设置',
      icon: 'Setting',
      breadcrumb: ['管理后台', '系统设置']
    }
  }
]

// Combine all admin routes
const adminRoutes = [
  ...dashboardRoutes,
  ...matchScheduleRoutes,
  ...dataStatisticsRoutes,
  ...intelligenceRoutes,
  ...userRoutes,
  ...crawlerRoutes,
  ...spRoutes,
  ...drawPredictionRoutes,
  ...systemRoute
]

export default adminRoutes