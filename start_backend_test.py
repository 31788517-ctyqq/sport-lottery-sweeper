import sys
import os
import subprocess
import time

# 切换到backend目录
os.chdir('backend')

# 运行后端并捕获输出
proc = subprocess.Popen([sys.executable, 'main.py'], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE,
                       text=True)

# 等待几秒获取输出
time.sleep(3)

# 读取输出
stdout, stderr = proc.communicate(timeout=1)

print("STDOUT:", stdout)
print("STDERR:", stderr)

# 终止进程
proc.terminate()