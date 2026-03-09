import Layout from '@/layout/Index.vue'

const adminRoutes = [
  {
    path: '/admin',
    component: Layout,
    redirect: '/admin/dashboard',
    meta: {
      title: 'System Management',
      icon: 'setting',
      roles: ['admin', 'manager'],
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: {
          title: 'Dashboard',
          icon: 'dashboard',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        redirect: '/admin/users/frontend',
        meta: {
          title: 'User Management',
          icon: 'user',
          roles: ['admin']
        },
        children: [
          {
            path: 'frontend',
            name: 'FrontendUsers',
            component: () => import('../views/admin/users/FrontendUsers.vue'),
            meta: {
              title: 'Frontend Users',
              icon: 'user',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'backend',
            name: 'BackendUsers',
            component: () => import('../views/admin/users/BackendUsers.vue'),
            meta: {
              title: 'Backend Users',
              icon: 'user',
              roles: ['admin']
            }
          }
        ]
      },
      // Crawler Management Module
      {
        path: 'crawler',
        name: 'CrawlerManagement',
        redirect: '/admin/crawler/data-source-management', // 更新重定向路径
        meta: {
          title: '爬虫管理',
          icon: 'bug',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'source-config',
            name: 'SourceConfig',
            component: () => import('../views/admin/crawler/SourceConfig.vue'),
            meta: {
              title: '源配置',
              icon: 'link',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'data-source',
            name: 'DataSource',
            component: () => import('../views/admin/crawler/DataSource.vue'),
            meta: {
              title: '数据源管理(旧)',
              icon: 'link',
              roles: ['admin'],
              hidden: true // 隐藏旧页面
            }
          },
          {
            path: 'data-source-management',
            name: 'DataSourceManagement',
            component: () => import('../views/admin/crawler/DataSourceManagement.vue'),
            meta: {
              title: '数据源管理',
              icon: 'link',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'task-console',
            name: 'TaskConsole',
            component: () => import('../views/admin/crawler/TaskConsole.vue'),
            meta: {
              title: '任务控制台',
              icon: 'console',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'task-scheduler',
            name: 'TaskScheduler',
            component: () => import('../views/admin/crawler/TaskScheduler.vue'),
            meta: {
              title: '任务调度',
              icon: 'schedule',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'data-intelligence',
            name: 'CrawlerDataIntelligence',
            component: () => import('../views/admin/crawler/DataIntelligence.vue'),
            meta: {
              title: '数据情报',
              icon: 'data-analysis',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'intelligence',
            name: 'DataIntelligence',
            component: () => import('../views/admin/crawler/DataIntelligence.vue'),
            meta: {
              title: '数据情报',
              icon: 'data-analysis',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'system-monitor',
            name: 'SystemMonitor',
            component: () => import('../views/admin/crawler/SystemMonitor.vue'),
            meta: {
              title: '系统监控',
              icon: 'monitor',
              roles: ['admin', 'manager']
            }
          },
          // 新增：数据中心路由
          {
            path: 'data-center',
            name: 'DataCenter',
            component: () => import('../views/admin/crawler/DataCenter.vue'),
            meta: {
              title: '数据中心',
              icon: 'data-analysis',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'configs',
            name: 'CrawlerConfigs',
            component: () => import('../views/admin/crawler/SourceConfig.vue'),
            meta: {
              title: '爬虫配置',
              icon: 'setting',
              roles: ['admin']
            }
          }
        ]
      },
      // Football SP Management Module (using existing SP components)
      {
        path: 'sp',
        name: 'SpManagement',
        redirect: '/admin/sp/data-source',
        meta: {
          title: '足球SP管理',
          icon: 'soccer',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'data-source',
            name: 'SpDataSources',
            component: () => import('../views/admin/sp/DataSourceManagement.vue'),
            meta: {
              title: '数据源管理',
              icon: 'link',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'matches',
            name: 'SpMatches',
            component: () => import('../views/admin/sp/MatchManagement.vue'),
            meta: {
              title: '比赛信息管理',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'records',
            name: 'SpRecords',
            component: () => import('../views/admin/sp/SPRecordManagement.vue'),
            meta: {
              title: 'SP值管理',
              icon: 'trend-charts',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'analysis',
            name: 'SpAnalysis',
            component: () => import('../views/admin/sp/DataAnalysisInsight.vue'),
            meta: {
              title: '数据分析与洞察',
              icon: 'pie-chart',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // Match Schedule Module
      {
        path: 'match-schedule',
        name: 'MatchSchedule',
        redirect: '/admin/match-schedule/lottery',
        meta: {
          title: '比赛赛程',
          icon: 'timer',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'lottery',
            name: 'LotterySchedule',
            component: () => import('../views/admin/match/LotterySchedule.vue'),
            meta: {
              title: '竞彩赛程',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // Monitoring module (using existing DataManagement component)
      {
        path: 'monitoring',
        name: 'MonitoringDashboard',
        redirect: '/admin/monitoring/data',
        meta: {
          title: '监控仪表板',
          icon: 'monitor',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'data',
            name: 'MonitoringOverview',
            component: () => import('../views/admin/DataManagement.vue'),
            meta: {
              title: '数据监控',
              icon: 'view',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // Draw Prediction Management Module
      {
        path: 'draw-prediction',
        name: 'DrawPredictionManagement',
        redirect: '/admin/draw-prediction/data-feature',
        meta: {
          title: '平局预测管理',
          icon: 'platform',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'data-feature',
            name: 'DrawDataFeature',
            component: () => import('../views/admin/draw_prediction/DrawDataFeature.vue'),
            meta: {
              title: '数据特征工程',
              icon: 'cpu',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'model-train-eval',
            name: 'DrawModelTrainEval',
            component: () => import('../views/admin/draw_prediction/DrawModelTrainEval.vue'),
            meta: {
              title: '模型训练与评估',
              icon: 'magic-stick',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'manage-deploy',
            name: 'DrawModelManageDeploy',
            component: () => import('../views/admin/draw_prediction/DrawModelManageDeploy.vue'),
            meta: {
              title: '模型管理与部署',
              icon: 'set-up',
              roles: ['admin']
            }
          },
          {
            path: 'prediction-monitor',
            name: 'DrawPredictionMonitor',
            component: () => import('../views/admin/draw_prediction/DrawPredictionMonitor.vue'),
            meta: {
              title: '预测监控',
              icon: 'trend',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // Intelligence Management Module
      {
        path: 'intelligence',
        name: 'IntelligenceManagement',
        redirect: '/admin/intelligence/screening',
        meta: {
          title: '情报管理',
          icon: 'document',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'screening',
            name: 'IntelligenceScreening',
            component: () => import('../views/admin/intelligence/ScreeningManagement.vue'),
            meta: {
              title: '智能筛选',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'collection',
            name: 'IntelligenceCollection',
            component: () => import('../views/admin/intelligence/CollectionManagement.vue'),
            meta: {
              title: '采集管理',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'model',
            name: 'IntelligenceModel',
            component: () => import('../views/admin/intelligence/ModelManagement.vue'),
            meta: {
              title: '模型管理',
              icon: 'cpu',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'weight',
            name: 'IntelligenceWeight',
            component: () => import('../views/admin/intelligence/WeightManagement.vue'),
            meta: {
              title: '权重管理',
              icon: 'scale',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'graph',
            name: 'IntelligenceGraph',
            component: () => import('../views/admin/intelligence/GraphManagement.vue'),
            meta: {
              title: '图表管理',
              icon: 'data-line',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'data-intelligence',
            name: 'IntelligenceData',
            component: () => import('../views/admin/intelligence/DataIntelligence.vue'),
            meta: {
              title: '数据分析',
              icon: 'data-analysis',
              roles: ['admin', 'manager'],
              hidden: true
            }
          },
          {
            path: 'system-monitor',
            name: 'CrawlerSystemMonitor',
            component: () => import('../views/admin/crawler/SystemMonitor.vue'),
            meta: {
              title: '系统监控',
              icon: 'chart-line',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // Match Management Module (redundant with match-schedule, keeping both for completeness)
      {
        path: 'match',
        name: 'MatchManagement',
        redirect: '/admin/match/lottery',
        meta: {
          title: '比赛管理',
          icon: 'calendar',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'lottery',
            name: 'LotteryMatch',
            component: () => import('../views/admin/match/LotterySchedule.vue'),
            meta: {
              title: '竞彩赛程',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'spider',
            name: 'SpiderMatch',
            component: () => import('../views/admin/match/SpiderSchedule.vue'),
            meta: {
              title: '爬虫赛程',
              icon: 'clock',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // System Settings Module
      {
        path: 'system',
        name: 'SystemManagement',
        component: () => import('../views/admin/settings/SystemSettings.vue'),
        meta: {
          title: '系统设置',
          icon: 'setting',
          roles: ['admin']
        }
      },
      // Data Management Module
      {
        path: 'data',
        name: 'DataManagement',
        component: () => import('../views/admin/Data.vue'),
        meta: {
          title: '数据管理',
          icon: 'data-analysis',
          roles: ['admin', 'manager'],
          hidden: true
        }
      }
    ]
  }
]

export default adminRoutes