# AI Remote Services Live Pre-Release Checklist

- Time: 2026-02-18T11:29:29.578Z
- Backend: http://127.0.0.1:8000
- Account: admin

## Checkpoints
1. [PASS] data count api - status=200, count=9
2. [PASS] data list api - status=200, list=9
3. [PASS] data recovered providers >= 4 - current=9
4. [PASS] render table visible - page+table visible
5. [PASS] render rows > 0 - rows=9
6. [PASS] logic search request - rows=3
7. [PASS] logic reset request - rows=9
8. [PASS] data create temp provider api - status=201
9. [PASS] logic search temp provider - search triggered
10. [PASS] render temp provider row - rows=1
11. [PASS] logic toggle provider status - status=200
12. [PASS] logic delete temp provider - status=204
13. [PASS] api health - no 401/5xx

## Summary
- Total: 13
- Failed: 0
- Passed: 13