import subprocess
import sys
import os
import time

# 切换到backend目录
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# 启动后端进程，输出到文件
log_file = open('startup.log', 'w')
proc = subprocess.Popen([sys.executable, 'main.py'], 
                       stdout=log_file,
                       stderr=subprocess.STDOUT,
                       text=True)

# 等待几秒让服务启动
time.sleep(5)

# 检查进程是否存活
if proc.poll() is None:
    print("后端服务启动成功，PID:", proc.pid)
    with open('backend.pid', 'w') as f:
        f.write(str(proc.pid))
else:
    print("后端服务启动失败，查看 startup.log")
    
log_file.close()