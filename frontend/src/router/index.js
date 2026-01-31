import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Layout from '@/layout/Index.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Login
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/admin',
    component: Layout,
    redirect: '/admin/dashboard',
    meta: { title: '管理面板', icon: 'dashboard' },
    children: [
      // 1. Dashboard
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: {
          title: 'Dashboard',
          icon: 'dashboard',
          roles: ['admin', 'manager']
        }
      },
      // 2. 用户管理
      {
        path: 'users',
        name: 'UserManagement',
        redirect: '/admin/users/list',
        meta: {
          title: '用户管理',
          icon: 'UserFilled',
          roles: ['admin'],
          order: 2
        },
        children: [
          {
            path: 'list',
            name: 'UserList',
            component: () => import('@/views/admin/users/UserList.vue'),
            meta: {
              title: '用户列表',
              icon: 'User',
              roles: ['admin', 'manager'],
              keepAlive: true
            }
          },
          {
            path: 'roles',
            name: 'RolePermission',
            component: () => import('@/views/admin/users/RolePermission.vue'),
            meta: {
              title: '角色与权限',
              icon: 'Key',
              roles: ['admin'],
              keepAlive: true
            }
          },
          {
            path: 'departments',
            name: 'DepartmentManagement',
            component: () => import('@/views/admin/users/DepartmentManagement.vue'),
            meta: {
              title: '部门管理',
              icon: 'OfficeBuilding',
              roles: ['admin'],
              keepAlive: true
            }
          },
          {
            path: 'profile',
            name: 'UserProfile',
            component: () => import('@/views/admin/users/UserProfile.vue'),
            meta: {
              title: '个人中心',
              icon: 'Avatar',
              roles: ['admin', 'manager'],
              keepAlive: false
            }
          },
          {
            path: 'profiles',
            name: 'UserProfileManagement',
            component: () => import('@/views/admin/users/UserProfileManagement.vue'),
            meta: {
              title: '用户画像管理',
              icon: 'User',
              roles: ['admin'],
              keepAlive: true
            }
          },
          {
            path: 'logs',
            name: 'OperationLog',
            component: () => import('@/views/admin/users/OperationLog.vue'),
            meta: {
              title: '操作日志',
              icon: 'Document',
              roles: ['admin'],
              keepAlive: true
            }
          }
        ]
      },
      // 3. 数据源管理
      {
        path: 'data-source',
        name: 'DataSourceManagement',
        redirect: '/admin/data-source/config',
        meta: {
          title: '数据源管理',
          icon: 'SetUp',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'config',
            name: 'DataSourceConfig',
            component: () => import('@/views/admin/crawler/DataSourceManagement.vue'),
            meta: {
              title: '数据源配置',
              icon: 'link',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'monitor',
            name: 'DataSourceMonitor',
            component: () => import('@/views/admin/crawler/SystemMonitor.vue'),
            meta: {
              title: '爬虫监控',
              icon: 'monitor',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'task-console',
            name: 'TaskConsole',
            component: () => import('@/views/admin/crawler/TaskConsole.vue'),
            meta: {
              title: '任务控制台',
              icon: 'connection',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'data-center',
            name: 'DataCenter',
            component: () => import('@/views/admin/crawler/DataCenter.vue'),
            meta: {
              title: '数据中心',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'ip-pool',
            name: 'IpPoolManagement',
            component: () => import('@/views/admin/crawler/IpPoolManagement.vue'),
            meta: {
              title: 'IP池管理',
              icon: 'connection',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'headers',
            name: 'HeadersManagement',
            component: () => import('@/views/admin/crawler/HeadersManagement.vue'),
            meta: {
              title: '请求头管理',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 4. 比赛数据管理
      {
        path: 'match-data',
        name: 'MatchDataManagement',
        redirect: '/admin/match-data/matches',
        meta: {
          title: '比赛数据管理',
          icon: 'Soccer',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'matches',
            name: 'MatchDataMatches',
            component: () => import('@/views/admin/sp/CompetitionManagement.vue'),
            meta: {
              title: '比赛管理',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'odds',
            name: 'OddsManagement',
            component: () => import('@/views/admin/sp/OddsManagement.vue'),
            meta: {
              title: '赔率管理',
              icon: 'trend-charts',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'schedule/jczq',
            name: 'JCZQSchedule',
            component: () => import('@/admin/JingcaiMatchManagement.vue'),
            meta: {
              title: '竞彩赛程',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'schedule/bd',
            name: 'BDSchedule',
            component: () => import('@/admin/BeidanMatchManagement.vue'),
            meta: {
              title: '北单赛程',
              icon: 'calendar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'leagues',
            name: 'LeagueManagement',
            component: () => import('@/views/admin/match/LeagueManagement.vue'),
            meta: {
              title: '联赛管理',
              icon: 'football',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 5. 平局预测管理
      {
        path: 'draw-prediction',
        name: 'DrawPredictionManagement',
        redirect: '/admin/draw-prediction/data-features',
        meta: {
          title: '平局预测管理',
          icon: 'histogram',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'data-features',
            name: 'DataFeaturesManagement',
            component: () => import('@/views/admin/draw_prediction/DrawDataFeature.vue'),
            meta: {
              title: '数据与特征管理',
              icon: 'data-analysis',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'training-evaluation',
            name: 'TrainingEvaluation',
            component: () => import('@/views/admin/draw_prediction/DrawModelTrainEval.vue'),
            meta: {
              title: '模型训练与评估',
              icon: 'files',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'model-deployment',
            name: 'ModelDeployment',
            component: () => import('@/views/admin/draw_prediction/DrawModelManageDeploy.vue'),
            meta: {
              title: '模型管理与部署',
              icon: 'upload',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'prediction-monitoring',
            name: 'PredictionMonitoring',
            component: () => import('@/views/admin/draw_prediction/DrawPredictionMonitor.vue'),
            meta: {
              title: '预测服务与监控',
              icon: 'monitor',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 6. 比赛视图
      {
        path: 'match-view',
        name: 'MatchView',
        component: () => import('@/views/admin/MatchView.vue'),  // 新增的比赛视图页面
        meta: {
          title: '比赛视图',
          icon: 'Football',
          roles: ['admin', 'manager']
        }
      },
      // 7. 情报分析
      {
        path: 'intelligence',
        name: 'IntelligenceManagement',
        redirect: '/admin/intelligence/screening',
        meta: {
          title: '情报分析',
          icon: 'Document',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'screening',
            name: 'IntelligenceScreening',
            component: () => import('@/views/admin/intelligence/ScreeningManagement.vue'),
            meta: {
              title: '智能筛选',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'collection',
            name: 'IntelligenceCollection',
            component: () => import('@/views/admin/intelligence/CollectionManagement.vue'),
            meta: {
              title: '采集管理',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'model',
            name: 'IntelligenceModel',
            component: () => import('@/views/admin/intelligence/ModelManagement.vue'),
            meta: {
              title: '模型管理',
              icon: 'cpu',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'weight',
            name: 'IntelligenceWeight',
            component: () => import('@/views/admin/intelligence/WeightManagement.vue'),
            meta: {
              title: '权重管理',
              icon: 'scale-to-original',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'sentiment',
            name: 'SentimentAnalysis',
            component: () => import('@/views/admin/intelligence/SentimentAnalysis.vue'),
            meta: {
              title: '情感分析',
              icon: 'chat-dot-square',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'multimodal',
            name: 'MultimodalAnalysis',
            component: () => import('@/views/admin/intelligence/MultimodalAnalysis.vue'),
            meta: {
              title: '多模态分析',
              icon: 'camera',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 8. AI服务管理
      {
        path: 'ai-services',
        name: 'AIServiceManagement',
        redirect: '/admin/ai-services/local',
        meta: {
          title: 'AI服务管理',
          icon: 'ChatLineRound',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'local',
            name: 'LocalAIService',
            component: () => import('@/views/admin/ai-services/LocalAIService.vue'),
            meta: {
              title: '本地AI服务',
              icon: 'office-building',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'remote',
            name: 'RemoteAIService',
            component: () => import('@/views/admin/ai-services/RemoteAIService.vue'),
            meta: {
              title: '远程AI服务',
              icon: 'position',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'costs',
            name: 'CostMonitoring',
            component: () => import('@/views/admin/ai-services/CostMonitoring.vue'),
            meta: {
              title: '成本监控',
              icon: 'wallet',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'agents',
            name: 'AgentManagement',
            component: () => import('@/views/admin/ai-services/AgentManagement.vue'),
            meta: {
              title: '智能体管理',
              icon: 'avatar',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'models',
            name: 'ModelManagement',
            component: () => import('@/views/admin/ai-services/ModelManagement.vue'),
            meta: {
              title: '预测模型管理',
              icon: 'data-analysis',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'conversation',
            name: 'ConversationAssistant',
            component: () => import('@/views/admin/ai-services/ConversationAssistant.vue'),
            meta: {
              title: '对话助手',
              icon: 'chat-line',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'config',
            name: 'ConfigManagement',
            component: () => import('@/views/admin/ai-services/ConfigManagement.vue'),
            meta: {
              title: '配置管理',
              icon: 'setting',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 9. 智能决策
      {
        path: 'intelligent-decision',
        name: 'IntelligentDecision',
        redirect: '/admin/intelligent-decision/hedging',
        meta: {
          title: '智能决策',
          icon: 'Management',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'hedging',
            name: 'HedgingManagement',
            component: () => import('@/views/admin/hedging/HedgingManagement.vue'),
            meta: {
              title: '对冲策略管理',
              icon: 'money',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'recommendations',
            name: 'RecommendationSystem',
            component: () => import('@/views/admin/intelligent-decision/RecommendationManagement.vue'),
            meta: {
              title: '推荐系统管理',
              icon: 'star',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'risk-control',
            name: 'RiskControl',
            component: () => import('@/views/admin/intelligent-decision/RiskControlManagement.vue'),
            meta: {
              title: '风险控制',
              icon: 'lock',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 10. 情报分析（保留原有的，移除重复部分）
      {
        path: 'intelligence',
        name: 'IntelligenceManagement',
        redirect: '/admin/intelligence/screening',
        meta: {
          title: '情报分析',
          icon: 'Document',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'screening',
            name: 'IntelligenceScreening',
            component: () => import('@/views/admin/intelligence/ScreeningManagement.vue'),
            meta: {
              title: '智能筛选',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'collection',
            name: 'IntelligenceCollection',
            component: () => import('@/views/admin/intelligence/CollectionManagement.vue'),
            meta: {
              title: '采集管理',
              icon: 'document',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'model',
            name: 'IntelligenceModel',
            component: () => import('@/views/admin/intelligence/ModelManagement.vue'),
            meta: {
              title: '模型管理',
              icon: 'cpu',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'weight',
            name: 'IntelligenceWeight',
            component: () => import('@/views/admin/intelligence/WeightManagement.vue'),
            meta: {
              title: '权重管理',
              icon: 'scale-to-original',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'sentiment',
            name: 'SentimentAnalysis',
            component: () => import('@/views/admin/intelligence/SentimentAnalysis.vue'), // 修复：使用正确的组件
            meta: {
              title: '情感分析',
              icon: 'chat-dot-square',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'multimodal',
            name: 'MultimodalAnalysis',
            component: () => import('@/views/admin/intelligence/MultimodalAnalysis.vue'), // 修复：使用正确的组件
            meta: {
              title: '多模态分析',
              icon: 'camera',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 11. 报告生成
      {
        path: 'reports',
        name: 'ReportGeneration',
        redirect: '/admin/reports/auto',
        meta: {
          title: '报告生成',
          icon: 'Memo',
          roles: ['admin', 'manager']
        },
        children: [
          {
            path: 'auto',
            name: 'AutoReports',
            component: () => import('@/views/admin/Dashboard.vue'),
            meta: {
              title: '自动报告',
              icon: 'document-checked',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'custom',
            name: 'CustomReports',
            component: () => import('@/views/admin/Dashboard.vue'),
            meta: {
              title: '自定义报告',
              icon: 'edit',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'templates',
            name: 'ReportTemplates',
            component: () => import('@/views/admin/Dashboard.vue'),
            meta: {
              title: '模板管理',
              icon: 'folder',
              roles: ['admin', 'manager']
            }
          },
          {
            path: 'distribution',
            name: 'ReportDistribution',
            component: () => import('@/views/admin/Dashboard.vue'),
            meta: {
              title: '报告分发',
              icon: 'position',
              roles: ['admin', 'manager']
            }
          }
        ]
      },
      // 12. 系统管理
      {
        path: 'system',
        name: 'SystemManagement',
        component: () => import('@/views/admin/SystemManagement.vue'),  // 更新为实际的系统管理页面
        meta: {
          title: '系统管理',
          icon: 'Setting',
          roles: ['admin']
        }
      },
      // 13. 用户管理 (新增独立页面)
      {
        path: 'user-management',
        name: 'UserManagementPage',
        component: () => import('@/views/admin/UserManagement.vue'),  // 新增的用户管理页面
        meta: {
          title: '用户管理',
          icon: 'User',
          roles: ['admin']
        }
      },
      // 14. 统计视图
      {
        path: 'stats',
        name: 'StatsView',
        component: () => import('@/views/admin/StatsView.vue'),  // 新增的统计视图页面
        meta: {
          title: '数据统计',
          icon: 'DataAnalysis',
          roles: ['admin', 'manager']
        }
      },
      // 15. 日志管理
      {
        path: 'logs',
        name: 'LogManagement',
        redirect: '/admin/logs',
        meta: {
          title: '日志管理',
          icon: 'Tickets',
          roles: ['admin']
        },
        children: [
          {
            path: '',
            name: 'LogsOverview',
            component: () => import('@/views/admin/logs/LogManagement.vue'),
            meta: { 
              title: '日志总览', 
              icon: 'document',
              roles: ['admin']
            }
          },
          {
            path: 'system',
            name: 'SystemLogs',
            component: () => import('@/views/admin/logs/SystemLogs.vue'),
            meta: { 
              title: '系统日志', 
              icon: 'document',
              roles: ['admin'],
              noCache: true 
            }
          },
          {
            path: 'user',
            name: 'UserLogs',
            component: () => import('@/views/admin/logs/UserLogs.vue'),
            meta: { 
              title: '用户日志', 
              icon: 'user',
              roles: ['admin'],
              noCache: true 
            }
          },
          {
            path: 'security',
            name: 'SecurityLogs',
            component: () => import('@/views/admin/logs/SecurityLogs.vue'),
            meta: { 
              title: '安全日志', 
              icon: 'lock',
              roles: ['admin'],
              noCache: true 
            }
          },
          {
            path: 'api',
            name: 'APILogs',
            component: () => import('@/views/admin/logs/APILogs.vue'),
            meta: { 
              title: 'API日志', 
              icon: 'connection',
              roles: ['admin'],
              noCache: true 
            }
          },
          {
            path: 'ai',
            name: 'AILogs',
            component: () => import('@/views/admin/logs/SystemLogs.vue'),
            meta: { 
              title: 'AI服务日志', 
              icon: 'cpu',
              roles: ['admin'],
              noCache: true 
            }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router