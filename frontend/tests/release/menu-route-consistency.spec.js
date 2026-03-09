import fs from 'node:fs'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import userRoutes from '../../src/router/modules/user-routes.js'
import matchRoutes from '../../src/router/modules/match-routes.js'
import drawPredictionRoutes from '../../src/router/modules/draw-prediction-routes.js'
import systemRoutes from '../../src/router/modules/system-routes.js'
import crawlerRoutes from '../../src/router/modules/crawler-routes.js'
import intelligenceRoutes from '../../src/router/modules/intelligence-routes.js'
import aiRoutes from '../../src/router/modules/ai-routes.js'
import decisionRoutes from '../../src/router/modules/decision-routes.js'
import reportRoutes from '../../src/router/modules/report-routes.js'

const EmptyView = { render: () => null }

function createAuditRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/admin',
        component: EmptyView,
        children: [
          {
            path: 'dashboard',
            name: 'AdminDashboard',
            component: EmptyView
          },
          ...userRoutes,
          ...crawlerRoutes,
          ...matchRoutes,
          {
            path: 'team-league-management',
            name: 'TeamLeagueManagement',
            redirect: '/admin/match-data/leagues'
          },
          ...drawPredictionRoutes,
          ...intelligenceRoutes,
          ...aiRoutes,
          ...decisionRoutes,
          ...reportRoutes,
          ...systemRoutes,
          {
            path: 'beidan-filter',
            name: 'BeidanFilterPanel',
            component: EmptyView
          },
          {
            path: 'beidan-betting-sim',
            name: 'BeidanBettingSimulator',
            component: EmptyView
          },
          {
            path: 'logs',
            name: 'LogManagement',
            redirect: '/admin/logs',
            children: [
              { path: '', name: 'LogsOverview', component: EmptyView },
              { path: 'system', name: 'SystemLogs', component: EmptyView },
              { path: 'user', name: 'UserLogs', component: EmptyView },
              { path: 'security', name: 'SecurityLogs', component: EmptyView },
              { path: 'api', name: 'APILogs', component: EmptyView },
              { path: 'ai', name: 'AILogs', component: EmptyView }
            ]
          }
        ]
      },
      { path: '/m/beidan-filter', name: 'MobileBeidanFilter', component: EmptyView },
      { path: '/m/beidan-filte', redirect: '/m/beidan-filter' }
    ]
  })
}

function getSidebarMenuPaths() {
  const source = fs.readFileSync('src/layout/Index.vue', 'utf8')
  return [...source.matchAll(/<el-menu-item\s+index=\"([^\"]+)\"/g)].map((m) => m[1])
}

describe('admin sidebar menu route consistency', () => {
  it('all sidebar menu paths should resolve to valid routes', () => {
    const router = createAuditRouter()
    const menuPaths = getSidebarMenuPaths()
    const unresolved = menuPaths.filter((menuPath) => router.resolve(menuPath).matched.length === 0)

    expect(unresolved).toEqual([])
  })

  it('route names used by admin/menu router should stay unique', () => {
    const router = createAuditRouter()
    const names = router
      .getRoutes()
      .map((route) => route.name)
      .filter(Boolean)
      .map(String)

    const duplicates = [...new Set(names.filter((name, index) => names.indexOf(name) !== index))]
    expect(duplicates).toEqual([])
  })
})
