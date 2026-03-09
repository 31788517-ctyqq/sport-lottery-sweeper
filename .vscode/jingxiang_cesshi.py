import requests
import time
import hashlib

def test_registry(url):
    # 可用性测试
    try:
        response = requests.get(f"{url}/v2/")
        if response.status_code != 200:
            return False, "API不可用"
    except requests.RequestException:
        return False, "网络错误"
    
    # 响应速度测试
    start = time.time()
    try:
        subprocess.run(["docker", "pull", f"{url}/nginx:latest"], check=True)
    except subprocess.CalledProcessError:
        return False, "拉取失败"
    duration = time.time() - start
    
    # 数据完整性验证
    local_hash = hashlib.sha256(open("/var/lib/docker/image/v2/repositories.json", "rb").read()).hexdigest()
    if local_hash != "官方校验值":
        return False, "数据损坏"
    
    return True, f"可用性:100%, 速度:{duration:.2f}s, 完整性:100%"

# 定时任务（每小时执行）
schedule.every().hour.do(test_registry, "https://mirror.example.com")
