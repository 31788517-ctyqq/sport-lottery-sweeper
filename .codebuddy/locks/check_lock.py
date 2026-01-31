#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI文件锁检查工具
防止多AI同时修改同一文件
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

LOCK_DIR = Path(".codebuddy/locks")
STATUS_FILE = Path(".codebuddy/status.json")

def check_lock(filename):
    """检查文件是否被锁定"""
    if not LOCK_DIR.exists():
        return None, "Lock directory not found"
    
    locks = list(LOCK_DIR.glob(f"{filename}.*.lock"))
    if not locks:
        return None, "No lock found"
    
    # 检查是否有过期锁(>30分钟)
    current_time = datetime.now()
    for lock_file in locks:
        timestamp_str = lock_file.stem.split('.')[-2]  # 提取时间戳
        try:
            lock_time = datetime.fromtimestamp(int(timestamp_str))
            if current_time - lock_time > timedelta(minutes=30):
                return "STALE", f"Stale lock found: {lock_file.name}"
        except:
            continue
    
    return "LOCKED", f"Active lock found: {locks[0].name}"

def create_lock(filename, ai_name):
    """创建文件锁"""
    if not LOCK_DIR.exists():
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已被锁定
    status, msg = check_lock(filename)
    if status == "LOCKED":
        return False, msg
    
    # 清理过期锁
    if status == "STALE":
        clean_stale_locks()
    
    timestamp = int(datetime.now().timestamp())
    lock_file = LOCK_DIR / f"{filename}.{ai_name}.{timestamp}.lock"
    
    lock_file.write_text("working")
    update_status(ai_name, filename)
    return True, f"Lock created: {lock_file.name}"

def release_lock(filename, ai_name):
    """释放文件锁"""
    if not LOCK_DIR.exists():
        return True, "No locks to release"
    
    locks = list(LOCK_DIR.glob(f"{filename}.{ai_name}.*.lock"))
    for lock_file in locks:
        lock_file.unlink()
    
    update_status(ai_name, None)
    return True, f"Released {len(locks)} lock(s)"

def clean_stale_locks():
    """清理过期锁"""
    if not LOCK_DIR.exists():
        return
    
    current_time = datetime.now()
    for lock_file in LOCK_DIR.glob("*.lock"):
        timestamp_str = lock_file.stem.split('.')[-2]
        try:
            lock_time = datetime.fromtimestamp(int(timestamp_str))
            if current_time - lock_time > timedelta(minutes=30):
                lock_file.unlink()
        except:
            continue

def update_status(ai_name, current_file):
    """更新状态文件"""
    try:
        if STATUS_FILE.exists():
            status = json.loads(STATUS_FILE.read_text())
        else:
            status = {"active_ais": [], "current_tasks": {}, "file_locks": [], "last_updated": ""}
        
        if current_file:
            if ai_name not in status["active_ais"]:
                status["active_ais"].append(ai_name)
            status["current_tasks"][ai_name] = f"修改{current_file}"
            
            # 更新文件锁列表
            locks = list(LOCK_DIR.glob("*.lock"))
            status["file_locks"] = [lock.name for lock in locks]
        else:
            if ai_name in status["active_ais"]:
                status["active_ais"].remove(ai_name)
            if ai_name in status["current_tasks"]:
                del status["current_tasks"][ai_name]
        
        status["last_updated"] = datetime.now().isoformat()
        STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"更新状态失败: {e}")

def main():
    if len(sys.argv) < 3:
        print("用法: python check_lock.py <action> <filename> [ai_name]")
        print("action: check|create|release")
        sys.exit(1)
    
    action = sys.argv[1]
    filename = sys.argv[2]
    ai_name = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    
    if action == "check":
        status, msg = check_lock(filename)
        print(f"{status}: {msg}")
    elif action == "create":
        success, msg = create_lock(filename, ai_name)
        print(msg)
        sys.exit(0 if success else 1)
    elif action == "release":
        success, msg = release_lock(filename, ai_name)
        print(msg)
    elif action == "clean":
        clean_stale_locks()
        print("Cleaned stale locks")
    else:
        print("Invalid action")
        sys.exit(1)

if __name__ == "__main__":
    main()