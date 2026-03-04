# Crawler Headers/IPPool Rollout Guide

Version: v1.0  
Date: 2026-02-28

## 1. Scope

- Pool reconcile (`pool.reconcile`) dry-run and execution switch
- IP auto replenish
- Headers auto replenish and auto bind
- Proxy-first request with direct fallback

## 2. Feature Flags

- `POOL_RECONCILE_ENABLED`
- `POOL_RECONCILE_DRY_RUN`
- `IP_POOL_AUTO_REPLENISH_ENABLED`
- `HEADER_POOL_AUTO_REPLENISH_ENABLED`
- `REQUEST_USE_PROXY_BY_DEFAULT`
- `REQUEST_ALLOW_DIRECT_FALLBACK`

## 3. Rollout Phases

1. Phase-A (Observe only)
- `POOL_RECONCILE_DRY_RUN=true`
- Auto replenish flags off
- Verify reconcile output and capacity gaps

2. Phase-B (IP auto replenish)
- Turn on `IP_POOL_AUTO_REPLENISH_ENABLED=true`
- Keep headers auto replenish off
- Verify IP active gap closes automatically

3. Phase-C (Headers auto replenish + auto bind)
- Turn on `HEADER_POOL_AUTO_REPLENISH_ENABLED=true`
- Use `/api/admin/headers/auto-bind/data-source` in dry-run first, then execute
- Verify domain-level headers and binding coverage rise

4. Phase-D (Full linkage)
- Keep proxy-first and direct fallback enabled
- Verify scheduler request path has `request_meta` for traceability

## 4. Rollback Plan

1. Immediate rollback
- Set:
  - `IP_POOL_AUTO_REPLENISH_ENABLED=false`
  - `HEADER_POOL_AUTO_REPLENISH_ENABLED=false`
  - `POOL_RECONCILE_DRY_RUN=true`

2. Traffic safety fallback
- Ensure `REQUEST_ALLOW_DIRECT_FALLBACK=true`
- Keep `REQUEST_USE_PROXY_BY_DEFAULT=true` to retain proxy-first strategy

3. Verify rollback
- Reconcile tasks should report actions but not mutate data
- New headers/IP counts should stop auto-growing

## 5. Ops Checklist

- Confirm Celery beat has `pool.reconcile.scheduled`
- Confirm `ip-pools/stats` returns capacity fields
- Confirm `headers/stats` returns `domain_stats` and `capacity.bindings_coverage`
- Confirm front-end pages show gaps and coverage
