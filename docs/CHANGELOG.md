# Changelog

## 2026-02-28

- Added pool reconcile scheduler and task entry (`pool.reconcile`, `pool.reconcile.scheduled`).
- Added IP/Headers capacity-related config switches and fallback controls.
- Added pool capacity APIs:
  - `POST /api/admin/ip-pools/reconcile`
  - `GET /api/admin/ip-pools/stats` capacity fields
  - `GET /api/admin/headers/stats` domain capacity and binding coverage
  - `POST /api/admin/headers/auto-bind/data-source`
- Added services:
  - `backend/services/pool_reconciler_service.py`
  - `backend/services/headers_pool_service.py`
- Added front-end capacity dashboards and actions:
  - `IpPoolManagement.vue`
  - `HeadersManagement.vue`
  - `DataSourceManagement.vue`
- Added docs:
  - `docs/CRAWLER_HEADERS_IPPOOL_ROLLOUT.md`
  - `docs/POOL_CAPACITY_INSPECTION_TEMPLATE.md`
- Added unit/integration tests for pool capacity and reconcile flow.
