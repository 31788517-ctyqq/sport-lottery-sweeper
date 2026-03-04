try:
    print("正在导入后端应用...")
    from backend.main import app
    print("✅ Backend app loaded successfully")
    
    print("正在导入数据库引擎...")
    from backend.database import engine
    print("✅ Database engine loaded successfully")
    
    print("正在导入TaskSchedulerService...")
    from backend.services.task_scheduler_service import TaskSchedulerService
    print("✅ TaskSchedulerService loaded successfully")
    
    print("所有导入成功！")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()