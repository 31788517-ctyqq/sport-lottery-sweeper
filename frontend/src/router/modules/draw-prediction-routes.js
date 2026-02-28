// 平局预测模块路由
const drawPredictionRoutes = [
  {
    path: 'draw-prediction',
    name: 'DrawPredictionManagement',
    redirect: '/admin/draw-prediction/ai-draw',
    meta: {
      title: '平局预测管理',
      icon: 'histogram',
      roles: ['admin', 'manager'],
      order: 5
    },
    children: [
      {
        path: 'ai-draw',
        name: 'AiDrawScanner',
        component: () => import('@/views/admin/draw_prediction/AiDrawScanner.vue'),
        meta: {
          title: '北单平局预测扫盘',
          icon: 'data-analysis',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'poisson-11',
        name: 'Poisson11Scanner',
        component: () => import('@/views/admin/draw_prediction/Poisson11Scanner.vue'),
        meta: {
          title: '1-1比分预测扫盘',
          icon: 'data-analysis',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'suggestion-center',
        name: 'DrawSuggestionCenter',
        component: () => import('@/views/admin/draw_prediction/DrawSuggestionCenter.vue'),
        meta: {
          title: '下注建议中心',
          icon: 'tickets',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'killswitch',
        name: 'DrawKillSwitchMonitor',
        component: () => import('@/views/admin/draw_prediction/DrawKillSwitchMonitor.vue'),
        meta: {
          title: '风控与熔断监控',
          icon: 'warning',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'model-workbench',
        name: 'DrawModelWorkbench',
        component: () => import('@/views/admin/draw_prediction/ModelWorkbench.vue'),
        meta: {
          title: '模型工坊',
          icon: 'grid',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'data-features',
        redirect: '/admin/draw-prediction/model-workbench?tab=data'
      },
      {
        path: 'training-evaluation',
        redirect: '/admin/draw-prediction/model-workbench?tab=training'
      },
      {
        path: 'model-deployment',
        redirect: '/admin/draw-prediction/model-workbench?tab=deployment'
      },
      {
        path: 'prediction-monitoring',
        redirect: '/admin/draw-prediction/model-workbench?tab=monitoring'
      }
    ]
  }
]

export default drawPredictionRoutes
