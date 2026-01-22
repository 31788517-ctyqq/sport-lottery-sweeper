import { createRouter, createWebHashHistory } from 'vue-router'

// 占位组件，避免路由报错
const Placeholder = {
  template: `<div style="padding:20px"><h2>{{ title }}</h2><p>此页面正在开发中...</p></div>`,
  props: ['title']
}

const routes = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/AdminLogin.vue'),
    meta: {
      title: '管理员登录'
    }
  },
  {
    path: '/',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin',
    name: 'Admin',
    redirect: '/admin/dashboard',
    meta: {
      title: '系统管理',
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: {
          title: '仪表板'
        }
      },
      // 爬虫管理模块
      {
        path: 'crawler',
        name: 'CrawlerManagement',
        redirect: '/admin/crawler/sources',
        meta: {
          title: '爬虫管理',
          icon: 'bug'
        },
        children: [
          {
            path: 'sources',
            name: 'CrawlerSources',
            component: () => import('../views/admin/crawler/DataSource.vue'),
            meta: {
              title: '数据源管理',
              icon: 'link'
            }
          },
          {
            path: 'tasks',
            name: 'TaskScheduler',
            component: () => import('../views/admin/crawler/TaskScheduler.vue'),
            meta: {
              title: '任务调度',
              icon: 'schedule'
            }
          },
          {
            path: 'intelligence',
            name: 'DataIntelligence',
            component: () => import('../views/admin/crawler/DataIntelligence.vue'),
            meta: {
              title: '数据情报',
              icon: 'data-analysis'
            }
          },
          {
            path: 'configs',
            name: 'CrawlerConfigs',
            component: () => import('../views/admin/crawler/SourceConfig.vue'),
            meta: {
              title: '爬虫配置',
              icon: 'setting'
            }
          }
        ]
      },
      // 用户管理（带子菜单）
      {
        path: 'users',
        name: 'UserManagement',
        redirect: '/admin/users/backend',
        meta: {
          title: '用户管理',
          icon: 'user'
        },
        children: [
          {
            path: 'backend',
            name: 'BackendUsers',
            component: () => import('../views/admin/users/BackendUsers.vue'),
            meta: {
              title: '后端用户',
              icon: 'user-filled'
            }
          },
          {
            path: 'frontend',
            name: 'FrontendUsers',
            component: () => import('../views/admin/users/FrontendUsers.vue'),
            meta: {
              title: '前端用户',
              icon: 'user'
            }
          }
        ]
      },
      // 足球SP管理（新增）
      {
        path: 'sp',
        name: 'SpManagement',
        redirect: '/admin/sp/data-sources',
        meta: {
          title: '足球SP管理',
          icon: 'soccer'
        },
        children: [
          {
            path: 'data-sources',
            name: 'SpDataSources',
            component: () => import('@/views/admin/sp/DataSourceManagement.vue'),
            meta: { title: '数据源管理', icon: 'link' }
          },
          {
            path: 'matches',
            name: 'SpMatches',
            component: () => import('@/views/admin/sp/MatchManagement.vue'),
            meta: { title: '比赛信息管理', icon: 'calendar' }
          },
          {
            path: 'records',
            name: 'SpRecords',
            component: () => import('@/views/admin/sp/SPRecordManagement.vue'),
            meta: { title: 'SP值管理', icon: 'trend-charts' }
          },
          {
            path: 'analysis',
            name: 'SpAnalysis',
            component: () => import('@/views/admin/sp/DataAnalysisInsight.vue'),
            meta: { title: '数据分析与洞察', icon: 'pie-chart' }
          }
        ]
      },
      // 赛程管理
      {
        path: 'match',
        name: 'MatchManagement',
        redirect: '/admin/match/lottery',
        meta: {
          title: '赛程管理',
          icon: 'calendar'
        },
        children: [
          {
            path: 'lottery',
            name: 'LotterySchedule',
            component: () => import('../views/admin/match/LotterySchedule.vue'),
            meta: {
              title: '彩票赛程',
              icon: 'ticket'
            }
          },
          {
            path: 'spider',
            name: 'SpiderSchedule',
            component: () => import('../views/admin/match/SpiderSchedule.vue'),
            meta: {
              title: '爬虫赛程',
              icon: 'set-up'
            }
          }
        ]
      },
      // 情报管理
      {
        path: 'intelligence',
        name: 'IntelligenceManagement',
        component: () => import('../views/admin/intelligence/CrawlerIntelligence.vue'),
        meta: {
          title: '情报管理',
          icon: 'data-analysis'
        }
      },
      // 数据管理
      {
        path: 'data',
        name: 'DataManagement',
        component: () => import('../views/admin/DataManagement.vue'),
        meta: {
          title: '数据管理',
          icon: 'folder-opened'
        }
      },
      // 平局预测
      {
        path: 'draw-prediction',
        name: 'DrawPredictionManagement',
        redirect: '/admin/draw-prediction/data-feature',
        meta: {
          title: '平局预测',
          icon: 'football',
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
      // 系统管理
      {
        path: 'system',
        name: 'SystemManagement',
        component: () => import('../views/admin/System.vue'),
        meta: {
          title: '系统管理',
          icon: 'setting'
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 动态获取 token 函数（与 request.js 保持一致）
const getToken = async () => {
  try {
    const storeModule = await import('@/store/user')
    const { useUserStore } = storeModule
    const userStore = useUserStore()
    return userStore.token || null
  } catch (error) {
    return null
  }
}

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 体育彩票扫盘系统`
  }

  // 如果是登录页面，直接放行
  if (to.path === '/admin/login') {
    next()
    return
  }

  // 开发环境下跳过认证检查（方便 Mock 测试）- 暂时禁用以便测试
  // if (import.meta.env.DEV) {
  //   next()
  //   return
  // }

  // 生产环境的认证检查
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = await getToken()
    if (token) {
      next()
    } else {
      next('/admin/login')
    }
  } else {
    next()
  }
})

export default router