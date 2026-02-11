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
import time

LOCK_DIR = Path(".codebuddy/locks")
STATUS_FILE = Path(".codebuddy/status.json")

def ensure_lock_dir():
    """确保锁目录存在"""
    LOCK_DIR.mkdir(parents=True, exist_ok=True)

def check_lock(filename):
    """检查文件是否被锁定"""
    ensure_lock_dir()
    
    # 查找该文件的所有锁
    file_locks = list(LOCK_DIR.glob(f"*{filename}*.lock"))
    
    if not file_locks:
        return "UNLOCKED", "文件未锁定，可以安全修改"
    
    # 检查是否有活跃锁（创建时间在30分钟内）
    current_time = datetime.now()
    for lock_file in file_locks:
        # 提取时间戳
        parts = lock_file.stem.split('.')
        if len(parts) >= 3:
            try:
                timestamp_str = parts[-2]
                lock_time = datetime.fromtimestamp(int(timestamp_str))
                if current_time - lock_time < timedelta(minutes=30):
                    # 获取AI名称
                    ai_name = parts[-3] if len(parts) >= 4 else "unknown"
                    return "LOCKED", f"文件已被 {ai_name} 锁定，锁文件: {lock_file.name}"
            except (ValueError, IndexError):
                continue
    
    # 所有锁都已过期
    return "STALE", "存在过期锁，可以清理后修改"

def create_lock(filename, ai_name):
    """创建文件锁"""
    ensure_lock_dir()
    
    # 先检查是否已锁定
    status, msg = check_lock(filename)
    if status == "LOCKED":
        return False, f"无法创建锁: {msg}"
    
    # 清理该文件的过期锁
    clean_stale_locks_for_file(filename)
    
    # 生成时间戳
    timestamp = int(time.time())
    
    # 创建锁文件名
    lock_filename = f"{filename}.{ai_name}.{timestamp}.lock"
    lock_file = LOCK_DIR / lock_filename
    
    # 创建锁文件
    try:
        lock_file.write_text(f"AI:{ai_name}\nFile:{filename}\nTimestamp:{timestamp}\nCreated:{datetime.now().isoformat()}")
        
        # 更新状态文件
        update_status(ai_name, filename)
        
        return True, f"锁创建成功: {lock_filename}"
    except Exception as e:
        return False, f"创建锁失败: {str(e)}"

def release_lock(filename, ai_name):
    """释放文件锁"""
    ensure_lock_dir()
    
    # 查找该AI对该文件的锁
    file_locks = list(LOCK_DIR.glob(f"*{filename}*.{ai_name}.*.lock"))
    
    if not file_locks:
        return True, f"未找到 {ai_name} 对 {filename} 的锁"
    
    # 释放所有找到的锁
    released = 0
    for lock_file in file_locks:
        try:
            lock_file.unlink()
            released += 1
        except Exception:
            continue
    
    # 更新状态文件
    update_status(ai_name, None)
    
    return True, f"已释放 {released} 个锁"

def clean_stale_locks():
    """清理所有过期锁"""
    ensure_lock_dir()
    
    current_time = datetime.now()
    cleaned = 0
    
    for lock_file in LOCK_DIR.glob("*.lock"):
        try:
            # 提取时间戳
            parts = lock_file.stem.split('.')
            if len(parts) >= 3:
                timestamp_str = parts[-2]
                lock_time = datetime.fromtimestamp(int(timestamp_str))
                if current_time - lock_time > timedelta(minutes=30):
                    lock_file.unlink()
                    cleaned += 1
        except (ValueError, IndexError):
            # 如果无法解析时间戳，也删除（可能是无效锁文件）
            try:
                lock_file.unlink()
                cleaned += 1
            except:
                continue
    
    return cleaned

def clean_stale_locks_for_file(filename):
    """清理指定文件的过期锁"""
    ensure_lock_dir()
    
    current_time = datetime.now()
    cleaned = 0
    
    file_locks = list(LOCK_DIR.glob(f"*{filename}*.lock"))
    for lock_file in file_locks:
        try:
            parts = lock_file.stem.split('.')
            if len(parts) >= 3:
                timestamp_str = parts[-2]
                lock_time = datetime.fromtimestamp(int(timestamp_str))
                if current_time - lock_time > timedelta(minutes=30):
                    lock_file.unlink()
                    cleaned += 1
        except (ValueError, IndexError):
            try:
                lock_file.unlink()
                cleaned += 1
            except:
                continue
    
    return cleaned

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
        print("action: check|create|release|clean")
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
        cleaned = clean_stale_locks()
        print(f"清理了 {cleaned} 个过期锁文件")
    else:
        print("Invalid action")
        sys.exit(1)

if __name__ == "__main__":
    main()