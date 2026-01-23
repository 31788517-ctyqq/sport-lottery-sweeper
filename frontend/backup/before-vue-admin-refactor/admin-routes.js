import Layout from './layout/Index.vue'

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
        component: () => import('./views/admin/Dashboard.vue'),
        meta: {
          title: 'Dashboard',
          icon: 'dashboard',
          roles: ['admin', 'manager']
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../views/admin/users/FrontendUsers.vue'),
        meta: {
          title: 'User Management',
          icon: 'user',
          roles: ['admin']
        }
      },
      // Crawler Management Module
      {
        path: 'crawler',
        name: 'CrawlerManagement',
        redirect: '/admin/crawler/sources',
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
              title: '数据源管理',
              icon: 'link',
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
      // Football SP Management Module (new, same level as crawler management)
      {
        path: 'sp',
        name: 'SpManagement',
        redirect: '/admin/sp/data-sources',
        meta: {
          title: '足球SP管理',
          icon: 'soccer',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'data-sources',
            name: 'SpDataSources',
            component: () => import('../../views/admin/sp/DataSourceManagement.vue'),
            meta: {
              title: '数据源管理',
              icon: 'link',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'matches',
            name: 'SpMatches',
            component: () => import('../../views/admin/sp/MatchManagement.vue'),
            meta: {
              title: '比赛信息管理',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'records',
            name: 'SpRecords',
            component: () => import('../../views/admin/sp/SPRecordManagement.vue'),
            meta: {
              title: 'SP值管理',
              icon: 'trend-charts',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'analysis',
            name: 'SpAnalysis',
            component: () => import('../../views/admin/sp/DataAnalysisInsight.vue'),
            meta: {
              title: '数据分析与洞察',
              icon: 'pie-chart',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      {
        path: 'crawler-alert',
        name: 'CrawlerAlert',
        redirect: '/admin/crawler-alert/rules',
        meta: {
          title: '爬虫告警',
          icon: 'warning',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'rules',
            name: 'AlertRules',
            component: () => import('../../views/admin/crawler/AlertRules.vue'),
            meta: {
              title: '告警规则管理',
              icon: 'bell',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'records',
            name: 'AlertRecords',
            component: () => import('../../views/admin/crawler/AlertRecords.vue'),
            meta: {
              title: '告警记录',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'check',
            name: 'AlertCheck',
            component: () => import('../../views/admin/crawler/AlertCheck.vue'),
            meta: {
              title: '告警检查',
              icon: 'search',
              roles: ['admin']
            }
          },
          {
            path: 'stats',
            name: 'AlertStats',
            component: () => import('../../views/admin/crawler/AlertStats.vue'),
            meta: {
              title: '告警统计',
              icon: 'data-board',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      {
        path: 'monitoring',
        name: 'MonitoringDashboard',
        redirect: '/admin/monitoring/dashboard',
        meta: {
          title: '监控仪表板',
          icon: 'monitor',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'dashboard',
            name: 'MonitoringOverview',
            component: () => import('../../views/admin/monitoring/Dashboard.vue'),
            meta: {
              title: '监控概览',
              icon: 'view',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'performance',
            name: 'SourcePerformance',
            component: () => import('../../views/admin/monitoring/SourcePerformance.vue'),
            meta: {
              title: '数据源性能',
              icon: 'speed',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'trends',
            name: 'AlertTrends',
            component: () => import('../../views/admin/monitoring/AlertTrends.vue'),
            meta: {
              title: '告警趋势',
              icon: 'trend',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'realtime',
            name: 'RealtimeMetrics',
            component: () => import('../../views/admin/monitoring/RealtimeMetrics.vue'),
            meta: {
              title: '实时指标',
              icon: 'timer',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'issues',
            name: 'TopIssues',
            component: () => import('../../views/admin/monitoring/TopIssues.vue'),
            meta: {
              title: '主要问题',
              icon: 'question',
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
      }
    ]
  }
]

export default adminRoutes
