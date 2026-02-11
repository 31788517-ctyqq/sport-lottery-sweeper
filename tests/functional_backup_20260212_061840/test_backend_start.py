import subprocess, time, sys, os
os.chdir('.')
cmd = [sys.executable, 'backend/main.py']
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
# 等待几秒
time.sleep(3)
# 读取输出
output = []
try:
    for line in iter(proc.stdout.readline, ''):
        output.append(line)
        if len(output) > 10:
            break
except:
    pass
# 终止进程
proc.terminate()
try:
    proc.wait(timeout=2)
except:
    proc.kill()
print('Output from backend startup:')
for line in output:
    print(line, end='')
print('---')