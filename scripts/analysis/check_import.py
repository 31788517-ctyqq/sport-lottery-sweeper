import sys
import os

# 添加项目路径
sys.path.insert(0, r'c:\Users\11581\Downloads\sport-lottery-sweeper')

try:
    print("正在导入TaskSchedulerService...")
    from backend.services.task_scheduler_service import TaskSchedulerService
    print("✅ TaskSchedulerService 导入成功")
    
    print("正在检查方法是否存在...")
    if hasattr(TaskSchedulerService, '_execute_real_task_logic'):
        print("✅ _execute_real_task_logic 方法存在")
    else:
        print("❌ _execute_real_task_logic 方法不存在")
        
    print("正在检查trigger_task方法...")
    import inspect
    trigger_task_source = inspect.getsource(TaskSchedulerService.trigger_task)
    if '_execute_real_task_logic' in trigger_task_source:
        print("✅ trigger_task方法已更新使用_real_task_logic")
    else:
        print("❌ trigger_task方法未更新")
        
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()