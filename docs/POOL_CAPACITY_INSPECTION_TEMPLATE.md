# Pool Capacity Inspection Template

Version: v1.0  
Date: 2026-02-28

## 1. 5-Minute Snapshot (Fast Check)

Time window: `YYYY-MM-DD HH:mm`  
Collector: `<name>`

### 1.1 IP Pool

- active: `<n>`
- standby(inactive): `<n>`
- testing: `<n>`
- cooling: `<n>`
- banned: `<n>`
- active target: `<n>`
- standby target: `<n>`
- active gap: `<n>`
- standby gap: `<n>`

### 1.2 Headers Pool

- domains count: `<n>`
- low quality total: `<n>`
- min active per domain: `<n>`
- headers per active IP: `<n>`

### 1.3 Binding Coverage

- sources total: `<n>`
- sources with header binding: `<n>`
- coverage rate: `<n>%`

### 1.4 Risk Summary

- reconcile risk level: `low|medium|high`
- recommended actions count: `<n>`
- top 3 gap domains:
1. `<domain-a>` gap `<n>`
2. `<domain-b>` gap `<n>`
3. `<domain-c>` gap `<n>`

## 2. Hourly Summary (Ops)

Time window: `YYYY-MM-DD HH:00 - HH:59`

- average active gap: `<n>`
- max active gap: `<n>`
- average low quality headers: `<n>`
- 403 count: `<n>`
- 429 count: `<n>`
- direct fallback count: `<n>`
- pool reconcile executions: `<n>`
- manual intervention count: `<n>`

## 3. Thresholds

- Active IP below target for 3+ snapshots: `warning`
- Active IP below target for 6+ snapshots: `critical`
- Low-quality headers growth > 20% hourly: `warning`
- Binding coverage < 80%: `warning`
- 403/429 rise > 30% vs previous hour: `warning`

## 4. Actions

1. `<action-1>`
2. `<action-2>`
3. `<action-3>`
