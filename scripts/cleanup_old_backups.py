#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旧备份文件定期清理脚本
自动清理超过指定天数的备份文件和临时文件，释放磁盘空间
"""

import os
import sys
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup_cleanup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BackupCleanup:
    def __init__(self, backup_dirs=None, retention_days=30, dry_run=False):
        """
        初始化清理器
        
        Args:
            backup_dirs: 要清理的备份目录列表
            retention_days: 保留天数，超过此天数的文件将被删除
            dry_run: 试运行模式，不实际删除文件
        """
        self.project_root = Path(__file__).parent.parent
        self.backup_dirs = backup_dirs or [
            self.project_root / 'backup_failed_tests',
            self.project_root / 'data' / '*.backup',
            self.project_root / '*.db.backup',
            self.project_root / '*.sql'
        ]
        self.retention_days = retention_days
        self.dry_run = dry_run
        self.cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # 统计信息
        self.stats = {
            'files_scanned': 0,
            'files_deleted': 0,
            'space_freed': 0,
            'errors': 0
        }
    
    def should_delete_file(self, file_path):
        """
        判断文件是否应该被删除
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否应该删除
        """
        try:
            # 检查文件是否存在
            if not file_path.exists():
                return False
            
            # 检查是否是文件
            if not file_path.is_file():
                return False
            
            # 获取文件修改时间
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # 检查是否超过保留期限
            if mtime < self.cutoff_date:
                # 保护重要的数据库文件不被误删
                if file_path.name == 'data/sport_lottery.db':
                    logger.warning(f"[WARN] 跳过重要数据库文件: {file_path}")
                    return False
                
                # 跳过最近7天内的日志文件
                if 'log' in file_path.suffix.lower() and mtime > (datetime.now() - timedelta(days=7)):
                    return False
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查文件失败 {file_path}: {e}")
            self.stats['errors'] += 1
            return False
    
    def get_file_size_mb(self, file_path):
        """获取文件大小（MB）"""
        try:
            return file_path.stat().st_size / (1024 * 1024)
        except:
            return 0
    
    def delete_file(self, file_path):
        """
        删除文件
        
        Args:
            file_path: 文件路径
        """
        try:
            file_size = self.get_file_size_mb(file_path)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] 将删除: {file_path} ({file_size:.2f} MB)")
            else:
                # 对于重要文件，先移动到回收站而不是直接删除
                if file_size > 100:  # 大于100MB的文件先备份
                    recycle_bin = self.project_root / 'backup_failed_tests' / 'recycle_bin'
                    recycle_bin.mkdir(parents=True, exist_ok=True)
                    backup_path = recycle_bin / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.move(str(file_path), str(backup_path))
                    logger.info(f"[MOVE] 大文件已移至回收站: {file_path} -> {backup_path} ({file_size:.2f} MB)")
                else:
                    file_path.unlink()
                    logger.info(f"[DELETE] 已删除: {file_path} ({file_size:.2f} MB)")
            
            self.stats['files_deleted'] += 1
            self.stats['space_freed'] += file_size
            
        except Exception as e:
            logger.error(f"删除文件失败 {file_path}: {e}")
            self.stats['errors'] += 1
    
    def cleanup_directory(self, directory):
        """
        清理指定目录
        
        Args:
            directory: 目录路径或通配符模式
        """
        path_pattern = Path(directory)
        
        # 处理通配符
        if '*' in str(path_pattern):
            parent = path_pattern.parent
            pattern = path_pattern.name
            
            if not parent.exists():
                logger.warning(f"目录不存在: {parent}")
                return
            
            matching_files = list(parent.glob(pattern))
        else:
            # 普通目录
            if not path_pattern.exists():
                logger.warning(f"目录不存在: {path_pattern}")
                return
            
            if path_pattern.is_file():
                matching_files = [path_pattern]
            else:
                matching_files = [f for f in path_pattern.rglob('*') if f.is_file()]
        
        for file_path in matching_files:
            self.stats['files_scanned'] += 1
            
            if self.should_delete_file(file_path):
                self.delete_file(file_path)
            else:
                logger.debug(f"保留文件: {file_path}")
    
    def cleanup_pycache(self):
        """清理Python缓存文件"""
        logger.info("[CLEAN] 清理Python缓存文件...")
        
        for pycache_dir in self.project_root.rglob('__pycache__'):
            if pycache_dir.is_dir():
                try:
                    dir_size = sum(f.stat().st_size for f in pycache_dir.rglob('*') if f.is_file()) / (1024 * 1024)
                    
                    if self.dry_run:
                        logger.info(f"[DRY RUN] 将删除缓存目录: {pycache_dir} ({dir_size:.2f} MB)")
                    else:
                        shutil.rmtree(pycache_dir)
                        logger.info(f"[DELETE] 已删除缓存目录: {pycache_dir} ({dir_size:.2f} MB)")
                    
                    self.stats['files_deleted'] += 1
                    self.stats['space_freed'] += dir_size
                    
                except Exception as e:
                    logger.error(f"删除缓存目录失败 {pycache_dir}: {e}")
                    self.stats['errors'] += 1
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        logger.info("[CLEAN] 清理临时文件...")
        
        temp_patterns = ['*.tmp', '*.temp', '*.cache', '.DS_Store', 'Thumbs.db', '*.log.old']
        
        for pattern in temp_patterns:
            for temp_file in self.project_root.rglob(pattern):
                if temp_file.is_file():
                    self.stats['files_scanned'] += 1
                    self.delete_file(temp_file)
    
    def run_cleanup(self):
        """执行清理操作"""
        logger.info("="*60)
        logger.info("[START] 开始备份文件清理")
        logger.info(f"[CONFIG] 保留期限: {self.retention_days} 天")
        logger.info(f"[CONFIG] 截止日期: {self.cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"[MODE] 试运行模式: {'是' if self.dry_run else '否'}")
        logger.info("="*60)
        
        # 清理备份目录
        for backup_dir in self.backup_dirs:
            if isinstance(backup_dir, str) and '*' in backup_dir:
                self.cleanup_directory(backup_dir)
            elif backup_dir.exists():
                logger.info(f"\n📁 清理目录: {backup_dir}")
                self.cleanup_directory(backup_dir)
        
        # 清理Python缓存
        self.cleanup_pycache()
        
        # 清理临时文件
        self.cleanup_temp_files()
        
        # 输出统计信息
        self.print_stats()
    
    def print_stats(self):
        """打印统计信息"""
        logger.info("\n" + "="*60)
        logger.info("[STATS] 清理统计")
        logger.info("="*60)
        logger.info(f"[SCAN] 扫描文件数: {self.stats['files_scanned']}")
        logger.info(f"[DELETE] 删除文件数: {self.stats['files_deleted']}")
        logger.info(f"[SPACE] 释放空间: {self.stats['space_freed']:.2f} MB")
        logger.info(f"[ERROR] 错误数: {self.stats['errors']}")
        
        if self.dry_run:
            logger.info("\n[WARN] 这是试运行模式，未实际删除任何文件")
            logger.info("   使用 --execute 参数执行实际清理")
        else:
            logger.info("\n[SUCCESS] 清理完成！")
        
        logger.info("="*60)

def main():
    parser = argparse.ArgumentParser(description='旧备份文件定期清理工具')
    parser.add_argument('--days', type=int, default=30,
                       help='保留天数（默认：30天）')
    parser.add_argument('--dry-run', action='store_true',
                       help='试运行模式，不实际删除文件')
    parser.add_argument('--execute', action='store_true',
                       help='执行实际清理（默认就是执行模式）')
    parser.add_argument('--dir', nargs='+',
                       help='指定要清理的目录')
    
    args = parser.parse_args()
    
    # 确保logs目录存在
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # 创建清理器实例
    cleanup = BackupCleanup(
        backup_dirs=args.dir,
        retention_days=args.days,
        dry_run=args.dry_run
    )
    
    try:
        cleanup.run_cleanup()
    except KeyboardInterrupt:
        logger.info("\n[WARN] 用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[ERROR] 清理过程出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()