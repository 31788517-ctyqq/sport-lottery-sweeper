import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/Index.vue'
import userRoutes from './modules/user-routes.js' // AI_WORKING: coder1 @1770224919 - 导入用户管理模块路由
import matchRoutes from './modules/match-routes.js' // AI_WORKING: coder1 @1770224919 - 导入比赛数据管理模块路由
import drawPredictionRoutes from './modules/draw-prediction-routes.js' // AI_WORKING: coder1 @1770224919 - 导入平局预测模块路由
import systemRoutes from './modules/system-routes.js' // AI_WORKING: coder1 @1770224919 - 导入系统管理模块路由
import crawlerRoutes from './modules/crawler-routes.js' // AI_WORKING: coder1 @1770224919 - 导入爬虫管理模块路由
import intelligenceRoutes from './modules/intelligence-routes.js' // AI_WORKING: coder1 @1770224919 - 导入情报分析模块路由
import aiRoutes from './modules/ai-routes.js' // AI_WORKING: coder1 @1770224919 - 导入AI服务管理模块路由
import decisionRoutes from './modules/decision-routes.js' // AI_WORKING: coder1 @1770224919 - 导入智能决策模块路由
import authRoutes from './modules/auth-routes.js' // AI_WORKING: coder1 @1770224919 - 导入认证模块路由
import reportRoutes from './modules/report-routes.js' // AI_WORKING: coder1 @1770224919 - 导入报告生成模块路由
import frontendRoutes from './modules/frontend-routes.js' // AI_WORKING: coder1 @1770224919 - 导入前台用户页面模块路由

const routes = [
  // 认证路由 (已移至 modules/auth-routes.js)
  ...authRoutes,
  // 前台用户页面路由 (已移至 modules/frontend-routes.js)
  ...frontendRoutes,
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
      // 2. 用户管理 (已移至 modules/user-routes.js)
      ...userRoutes,
      // 3. 数据源管理
      ...crawlerRoutes,
      // 4. 比赛数据管理 (已移至 modules/match-routes.js)
      ...matchRoutes,
      // 5. 平局预测管理 (已移至 modules/draw-prediction-routes.js)
      ...drawPredictionRoutes,
      // 6. 情报分析 (已移至 modules/intelligence-routes.js)
      ...intelligenceRoutes,
      // 7. AI服务管理 (已移至 modules/ai-routes.js)
      ...aiRoutes,
      // 8. 智能决策 (已移至 modules/decision-routes.js)
      ...decisionRoutes,
      // 9. 报告生成 (已移至 modules/report-routes.js)
      ...reportRoutes,
      // 10. 系统管理 (已移至 modules/system-routes.js)
      ...systemRoutes,
      // 11. 比赛视图
      {
        path: 'match-view',
        name: 'MatchView',
        component: () => import('@/views/MatchView.vue'),  // 使用根目录下的比赛视图
        meta: {
          title: '比赛视图',
          icon: 'Football',
          roles: ['admin', 'manager']
        }
      },
      // 12. 数据统计
      {
        path: 'stats',
        name: 'StatsView',
        component: () => import('@/views/StatsView.vue'),  // 使用根目录下的统计视图
        meta: {
          title: '数据统计',
          icon: 'DataAnalysis',
          roles: ['admin', 'manager']
        }
      },
      // 13. 北单过滤
      {
        path: 'beidan-filter',
        name: 'BeidanFilterPanel',
        component: () => import('@/views/admin/BeidanFilterPanel.vue'),
        meta: {
          title: '北单过滤',
          icon: 'filter',
          roles: ['admin', 'manager']
        }
      },
      // 14. 日志管理
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
            component: () => import('@/views/admin/logs/AILogs.vue'),
            meta: { 
              title: 'AI服务日志', 
              icon: 'cpu',
              roles: ['admin'],
              noCache: true 
            }
          }
        ]
      },
      // 19. 比赛分析模拟
      {
        path: 'match-analysis-simulation',
        name: 'MatchAnalysisSimulation',
        component: () => import('@/views/admin/MatchAnalysisSimulation.vue'),
        meta: {
          title: '比赛分析模拟',
          icon: 'DataAnalysis',
          roles: ['admin', 'manager']
        }
      }
    ]
  },
  // AI_WORKING: coder1 @1770224919 - 向后兼容的独立用户管理路由
  {
    path: '/admin/user-management-main',
    name: 'UserManagementMain',
    component: () => import('@/views/admin/UserManagement.vue'),
    meta: {
      title: '用户管理主页面',
      icon: 'User',
      roles: ['admin']
    }
  },
  {
    path: '/admin/backend-users',
    name: 'BackendUsers',
    component: () => import('@/views/admin/users/BackendUsers.vue'),
    meta: {
      title: '后端用户管理',
      icon: 'User',
      roles: ['admin']
    }
  },
  {
    path: '/admin/frontend-users',
    name: 'FrontendUsers',
    component: () => import('@/views/admin/users/FrontendUsers.vue'),
    meta: {
      title: '前端用户管理',
      icon: 'User',
      roles: ['admin']
    }
  },
  {
    path: '/user-management',
    name: 'UserManagementPage',
    component: () => import('@/views/UserManagement.vue'),
    meta: {
      title: '用户管理',
      icon: 'User',
      roles: ['admin']
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router