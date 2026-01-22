#!/usr/bin/env python
"""
一键诊断后端启动问题（修复 UnicodeDecodeError）
运行: python diagnose_backend_start.py
"""
import os
import subprocess
import sys
import time
from threading import Thread

def main():
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["BACKEND_ENV"] = "development"

    # 指定 encoding='utf-8'，errors='replace' 防止解码失败
    proc = subprocess.Popen(
        [sys.executable, "-u", "backend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )

    success_keywords = ["Application startup complete", "Uvicorn running on", "Listening at", "Started server", "Running on"]
    error_keywords = ["Error", "Exception", "Traceback", "Failed", "ImportError", "ModuleNotFoundError", "can't render element", "no attribute"]

    errors = []
    success = False

    def read_output():
        nonlocal success
        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            print(line, end='')
            lower = line.lower()
            for kw in success_keywords:
                if kw.lower() in lower:
                    success = True
            for kw in error_keywords:
                if kw.lower() in lower:
                    errors.append(line.strip())
        proc.stdout.close()

    thread = Thread(target=read_output, daemon=True)
    thread.start()

    # 最多等待 15 秒
    for _ in range(150):
        if proc.poll() is not None:
            break
        if success:
            print("\n[✓] 后端启动成功！")
            proc.terminate()
            return
        time.sleep(0.1)

    proc.terminate()
    print("\n[✗] 启动超时或未检测到成功标志")
    if errors:
        print("\n错误摘要:")
        for e in errors[-10:]:
            print(e)
    else:
        print("未发现明显错误关键词，请检查日志输出。")

if __name__ == "__main__":
    main()
