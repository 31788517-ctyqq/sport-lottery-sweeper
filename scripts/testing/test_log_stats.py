from backend.database import SessionLocal
from backend.services.log_service import LogService

db = SessionLocal()
service = LogService(db)
stats = service.get_log_statistics()

print('Stats structure:')
print(f'- total_logs: {stats.get("total_logs", "missing")}')
print(f'- logs_by_level: {type(stats.get("logs_by_level", {}))}')
print(f'- logs_by_module: {type(stats.get("logs_by_module", {}))}')

# 验证前端期望的属性是否存在
if "total_logs" in stats:
    print("✅ total_logs property exists")
else:
    print("❌ total_logs property missing")

if "logs_by_level" in stats:
    print("✅ logs_by_level property exists")
else:
    print("❌ logs_by_level property missing")

if "logs_by_module" in stats:
    print("✅ logs_by_module property exists")
else:
    print("❌ logs_by_module property missing")

db.close()