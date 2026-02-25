// 平局预测模块路由
const drawPredictionRoutes = [
  {
    path: 'draw-prediction',
    name: 'DrawPredictionManagement',
    redirect: '/admin/draw-prediction/data-features',
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
        path: 'data-features',
        name: 'DataFeaturesManagement',
        component: () => import('@/views/admin/draw_prediction/DrawDataFeature.vue'),
        meta: {
          title: '数据与特征管理',
          icon: 'data-analysis',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'training-evaluation',
        name: 'TrainingEvaluation',
        component: () => import('@/views/admin/draw_prediction/DrawModelTrainEval.vue'),
        meta: {
          title: '模型训练与评估',
          icon: 'files',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'model-deployment',
        name: 'ModelDeployment',
        component: () => import('@/views/admin/draw_prediction/DrawModelManageDeploy.vue'),
        meta: {
          title: '模型管理与部署',
          icon: 'upload',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      },
      {
        path: 'prediction-monitoring',
        name: 'PredictionMonitoring',
        component: () => import('@/views/admin/draw_prediction/DrawPredictionMonitor.vue'),
        meta: {
          title: '预测服务与监控',
          icon: 'monitor',
          roles: ['admin', 'manager'],
          keepAlive: true
        }
      }
    ]
  }
]

export default drawPredictionRoutes
