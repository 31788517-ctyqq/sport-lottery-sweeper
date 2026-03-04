import sys
import traceback
sys.path.insert(0, '.')
try:
    exec(open('setup_admin_and_test.py').read())
except Exception as e:
    print(f"脚本执行错误: {e}")
    traceback.print_exc()