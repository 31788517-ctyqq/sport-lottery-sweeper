# Intelligence Collection Network vs Backend Log Alignment

- startedAt: 2026-02-19T16:38:04.407Z
- endedAt: 2026-02-19T16:38:18.349Z
- pageAfterGoto: http://localhost:3000/admin/intelligence/collection
- screenshot: logs/intelligence_collection_capture.png

## /api/v1/admin/intelligence/collection/sources
- Browser request params:
```json
{
  "method": "GET",
  "query": {},
  "postData": null
}
```
- Browser response: status=200
- Backend logs: (no matched logs in window)

## /api/v1/admin/intelligence/collection/matches
- Browser request params:
```json
{
  "method": "GET",
  "query": {
    "page": "1",
    "size": "100",
    "search": "",
    "date_from": "2026-02-19",
    "date_to": "2026-02-19"
  },
  "postData": null
}
```
- Browser response: status=200
- Backend logs:
  - 2026-02-20 00:38:06 - backend.api.v1.admin.intelligence_collection - WARNING - [intelligence.collection.matches] params search='' date_from='2026-02-19' date_to='2026-02-19' page=1 size=100 matched_total=0 returned_ids=[] returned_schedule_dates=[]
  - 2026-02-20 00:38:08 - backend.api.v1.admin.intelligence_collection - WARNING - [intelligence.collection.matches] params search='' date_from='2026-02-10' date_to='2026-02-10' page=1 size=100 matched_total=11 returned_ids=[207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217] returned_schedule_dates=['2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10', '2026-02-10']

## /api/v1/admin/intelligence/collection/tasks
- Browser request params:
```json
{
  "method": "GET",
  "query": {
    "page": "1",
    "size": "100"
  },
  "postData": null
}
```
- Browser response: status=200
- Backend logs:
  - 2026-02-20 00:38:12 - backend.api.v1.admin.intelligence_collection - WARNING - [intelligence.collection.tasks.create] request mode=immediate match_ids_count=1 match_ids=[207] sources=['500w', 'ttyingqiu', 'tencent'] intel_types=['injury', 'weather', 'motivation', 'win_draw_lose', 'handicap_1x2'] offset_hours=[] by_admin=1
  - 2026-02-20 00:38:12 - backend.api.v1.admin.intelligence_collection - WARNING - [intelligence.collection.tasks.create] accepted task_id=10 status=running total_count=15

## /api/v1/admin/intelligence/collection/channels/dingtalk/bindings
- Browser request params:
```json
{
  "method": "GET",
  "query": {},
  "postData": null
}
```
- Browser response: status=200
- Backend logs: (no matched logs in window)

