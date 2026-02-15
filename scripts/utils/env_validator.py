#!/usr/bin/env python3
"""
环境变量验证和配置管理工具
确保各环境配置文件的一致性和完整性
"""
import os
import sys
from pathlib import Path
import logging
from typing import Dict, List, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class EnvValidator:
    """环境变量验证器"""
    
    # 必需的环境变量列表
    REQUIRED_VARS = {
        'database': ['DATABASE_URL', 'DATABASE_ECHO'],
        'security': ['SECRET_KEY'],
        'api': ['API_V1_STR', 'PROJECT_NAME', 'VERSION', 'DEBUG', 'HOST', 'PORT'],
        'redis': ['REDIS_HOST', 'REDIS_PORT'],
        'logging': ['LOG_LEVEL']
    }
    
    # 推荐的环境变量列表
    RECOMMENDED_VARS = {
        'database': ['DB_POOL_SIZE', 'DB_MAX_OVERFLOW', 'DB_POOL_TIMEOUT'],
        'redis': ['REDIS_PASSWORD', 'REDIS_DB', 'REDIS_POOL_SIZE'],
        'api': ['DOCS_ENABLED', 'BACKEND_CORS_ORIGINS'],
        'logging': ['LOG_FILE_MAX_BYTES', 'LOG_BACKUP_COUNT', 'LOG_ROTATION_INTERVAL']
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_env_file(self, env_path: Path) -> Dict:
        """验证单个环境文件"""
        if not env_path.exists():
            self.errors.append(f"环境文件不存在: {env_path}")
            return {'valid': False, 'errors': self.errors}
        
        logger.info(f"验证环境文件: {env_path}")
        
        # 读取环境变量
        env_vars = {}
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
        except Exception as e:
            self.errors.append(f"读取文件失败 {env_path}: {e}")
            return {'valid': False, 'errors': self.errors}
        
        # 验证必需变量
        for category, vars_list in self.REQUIRED_VARS.items():
            for var in vars_list:
                if var not in env_vars:
                    self.errors.append(f"[{category}] 缺少必需变量 {var} (文件: {env_path})")
                elif not env_vars[var] or env_vars[var].startswith('your-'):
                    self.warnings.append(f"[{category}] 变量 {var} 使用默认值或占位符 (文件: {env_path})")
        
        # 检查推荐变量
        for category, vars_list in self.RECOMMENDED_VARS.items():
            for var in vars_list:
                if var not in env_vars:
                    self.warnings.append(f"[{category}] 建议添加变量 {var} (文件: {env_path})")
        
        # 特定验证规则
        self._validate_specific_vars(env_vars, env_path)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'variables': env_vars
        }
    
    def _validate_specific_vars(self, env_vars: Dict, env_path: Path):
        """验证特定变量的格式和值"""
        
        # 验证SECRET_KEY长度
        if 'SECRET_KEY' in env_vars:
            secret_key = env_vars['SECRET_KEY']
            if len(secret_key) < 32:
                self.warnings.append(f"SECRET_KEY长度过短，建议至少32个字符 (文件: {env_path})")
        
        # 验证端口号
        if 'PORT' in env_vars:
            try:
                port = int(env_vars['PORT'])
                if not (1 <= port <= 65535):
                    self.errors.append(f"PORT值无效: {port} (文件: {env_path})")
            except ValueError:
                self.errors.append(f"PORT不是有效数字: {env_vars['PORT']} (文件: {env_path})")
        
        # 验证数据库URL格式
        if 'DATABASE_URL' in env_vars:
            db_url = env_vars['DATABASE_URL']
            valid_prefixes = ['sqlite:///', 'postgresql://', 'mysql://', 'sqlite+aiosqlite:///']
            if not any(db_url.startswith(prefix) for prefix in valid_prefixes):
                self.warnings.append(f"DATABASE_URL格式可能不正确: {db_url} (文件: {env_path})")
        
        # 验证日志级别
        if 'LOG_LEVEL' in env_vars:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if env_vars['LOG_LEVEL'].upper() not in valid_levels:
                self.warnings.append(f"LOG_LEVEL值无效: {env_vars['LOG_LEVEL']} (文件: {env_path})")
    
    def validate_all_env_files(self) -> Dict:
        """验证所有环境文件"""
        env_files = [
            project_root / '.env',
            project_root / '.env.example', 
            project_root / 'env.development',
            project_root / 'env.example'
        ]
        
        results = {}
        for env_file in env_files:
            if env_file.exists():
                results[str(env_file)] = self.validate_env_file(env_file)
        
        return results
    
    def generate_env_template(self, output_path: Path):
        """生成环境变量模板"""
        template_content = '''# =============================================================================
# Sport Lottery Sweeper System - 环境变量模板
# 复制此文件为 .env 并根据实际环境修改
# =============================================================================

# =============================================================================
# 数据库配置
# =============================================================================
# SQLite (默认开发环境)
DATABASE_URL=sqlite:///./data/sport_lottery.db

# PostgreSQL (生产环境推荐)
# DATABASE_URL=postgresql://username:password@localhost:5432/sport_lottery?pool_size=10&max_overflow=20

# MySQL (备选方案)
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/sport_lottery?charset=utf8mb4

# 数据库连接池设置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true

# 异步数据库URL
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./data/sport_lottery.db
# ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/sport_lottery

# =============================================================================
# Redis配置
# =============================================================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # 生产环境务必设置
REDIS_DB=0
REDIS_POOL_SIZE=10
REDIS_MAX_CONNECTIONS=20

# =============================================================================
# API配置
# =============================================================================
API_V1_STR=/api/v1
PROJECT_NAME=Sport Lottery Sweeper System
PROJECT_NAME_CN=竞彩足球扫盘系统
VERSION=0.2.0
DESCRIPTION=Professional sports lottery analysis and management platform
DEBUG=false  # 生产环境设为false
DOCS_ENABLED=true
HOST=0.0.0.0
PORT=8000

# =============================================================================
# 安全配置 - 生产环境必须修改
# =============================================================================
SECRET_KEY=your-super-secret-key-minimum-32-characters-change-in-production!!!
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# 跨域配置
# =============================================================================
# 开发环境
# BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
# 生产环境
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# =============================================================================
# 日志配置
# =============================================================================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=30
LOG_ROTATION_INTERVAL=midnight
LOG_ENCODING=utf-8
LOG_CLEANUP_ENABLED=true

# =============================================================================
# 爬虫配置
# =============================================================================
SCRAPE_INTERVAL=1800
MAX_RETRY=3
PROXY_POOL_ENABLED=false  # 生产环境谨慎开启
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        logger.info(f"环境变量模板已生成: {output_path}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='环境变量验证工具')
    parser.add_argument('--validate', action='store_true', help='验证所有环境文件')
    parser.add_argument('--template', action='store_true', help='生成环境模板')
    parser.add_argument('--file', type=str, help='验证指定文件')
    
    args = parser.parse_args()
    
    validator = EnvValidator()
    
    if args.template:
        template_path = project_root / '.env.template'
        validator.generate_env_template(template_path)
    
    if args.file:
        result = validator.validate_env_file(Path(args.file))
        print(f"\\n验证结果: {'通过' if result['valid'] else '失败'}")
        if result['errors']:
            print("错误:")
            for error in result['errors']:
                print(f"  - {error}")
        if result['warnings']:
            print("警告:")
            for warning in result['warnings']:
                print(f"  - {warning}")
    
    if args.validate or (not args.file and not args.template):
        results = validator.validate_all_env_files()
        
        print("\\n=== 环境变量验证报告 ===")
        all_valid = True
        for file_path, result in results.items():
            status = "✓ 通过" if result['valid'] else "✗ 失败"
            print(f"\\n{file_path}: {status}")
            
            if result['errors']:
                all_valid = False
                print("  错误:")
                for error in result['errors']:
                    print(f"    - {error}")
            
            if result['warnings']:
                print("  警告:")
                for warning in result['warnings']:
                    print(f"    - {warning}")
        
        print(f"\\n总体结果: {'✓ 所有文件验证通过' if all_valid else '✗ 存在验证错误'}")
        
        if not all_valid:
            sys.exit(1)

if __name__ == '__main__':
    main()