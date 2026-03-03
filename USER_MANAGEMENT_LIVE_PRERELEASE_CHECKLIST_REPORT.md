# User Management Pre-Release Live Checklist

- Time: 2026-03-03T03:13:17.517Z
- Backend: http://127.0.0.1:8000
- Account: admin

## Checkpoints
1. [PASS] minimal test data prep - created username=e2e_live_1772507594742, id=12
2. [PASS] prep activate user - status=200, verify=active
3. [PASS] export - ui-export status=200, content-type=text/csv; charset=utf-8; charset=utf-8
4. [PASS] batch disable/enable - disable=200 -> inactive, enable=200 -> active
5. [PASS] edit-save secondary verify - update=200, verify=200, real_name=E2E-LIVE-1772507597167
6. [PASS] api health - no 401/5xx
7. [PASS] cleanup - delete=200, recycled=true

## Summary
- Total: 7
- Failed: 0
- Passed: 7