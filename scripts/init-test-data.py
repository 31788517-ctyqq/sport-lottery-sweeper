#!/usr/bin/env python3
# AI_WORKING: coder1 @2026-01-28T14:32:00 - 创建测试数据初始化脚本
"""
测试数据初始化脚本
为前后端测试创建必要的测试数据
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

class TestDataInitializer:
    """测试数据初始化器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_dir = self.project_root / "frontend"
        self.backend_dir = self.project_root / "backend"
        
    def init_frontend_test_data(self):
        """初始化前端测试数据"""
        print("📁 初始化前端测试数据...")
        
        # 创建测试数据目录
        test_data_dir = self.frontend_dir / "tests" / "fixtures"
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 数据源测试数据
        data_sources = [
            {
                "id": 1,
                "name": "500彩票网API",
                "type": "api",
                "url": "https://api.500.com/v1",
                "status": "enabled",
                "error_rate": 2.5,
                "last_checked": "2026-01-28T10:30:00Z",
                "description": "官方500彩票网API接口，提供实时比赛数据"
            },
            {
                "id": 2,
                "name": "本地比赛数据",
                "type": "file",
                "url": "file:///data/local_matches.json",
                "status": "enabled", 
                "error_rate": 0.0,
                "last_checked": "2026-01-28T09:15:00Z",
                "description": "本地存储的历史比赛数据文件"
            },
            {
                "id": 3,
                "name": "测试数据源",
                "type": "test",
                "url": "test://mock/data",
                "status": "disabled",
                "error_rate": 15.0,
                "last_checked": "2026-01-27T14:20:00Z",
                "description": "用于测试的模拟数据源"
            }
        ]
        
        with open(test_data_dir / "data-sources.json", "w", encoding="utf-8") as f:
            json.dump(data_sources, f, indent=2, ensure_ascii=False)
        
        # 2. 用户测试数据
        users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@sport-lottery.com",
                "roles": ["admin", "manager"],
                "department": "技术部",
                "created_at": "2026-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "username": "analyst",
                "email": "analyst@sport-lottery.com", 
                "roles": ["analyst"],
                "department": "数据分析部",
                "created_at": "2026-01-05T09:30:00Z"
            },
            {
                "id": 3,
                "username": "viewer",
                "email": "viewer@sport-lottery.com",
                "roles": ["viewer"],
                "department": "运营部",
                "created_at": "2026-01-10T14:15:00Z"
            }
        ]
        
        with open(test_data_dir / "users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        
        # 3. 比赛数据测试数据
        matches = []
        today = datetime.now().date()
        
        for i in range(10):
            match_date = today + timedelta(days=i)
            matches.append({
                "id": i + 1,
                "match_id": f"MATCH{1000 + i}",
                "league": "英超" if i % 3 == 0 else "西甲" if i % 3 == 1 else "意甲",
                "home_team": f"球队{i*2}A",
                "away_team": f"球队{i*2+1}B",
                "match_time": f"{match_date.isoformat()}T20:00:00Z",
                "status": "scheduled" if i > 2 else "live" if i == 1 else "finished",
                "home_score": 2 if i == 0 else None,
                "away_score": 1 if i == 0 else None,
                "sp_data": {
                    "win": 1.8 + i * 0.1,
                    "draw": 3.2 - i * 0.05,
                    "lose": 4.0 + i * 0.15
                }
            })
        
        with open(test_data_dir / "matches.json", "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 前端测试数据已生成到: {test_data_dir}")
    
    def init_backend_test_data(self):
        """初始化后端测试数据"""
        print("📁 初始化后端测试数据...")
        
        # 创建测试数据库目录
        test_db_dir = self.backend_dir / "test_data"
        test_db_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite测试数据库
        db_path = test_db_dir / "test.db"
        
        if db_path.exists():
            print("ℹ️  测试数据库已存在，跳过创建")
            return
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            roles TEXT NOT NULL,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建数据源表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL,
            status TEXT NOT NULL,
            error_rate REAL DEFAULT 0.0,
            last_checked TIMESTAMP,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建比赛数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE NOT NULL,
            league TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_time TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            sp_win REAL,
            sp_draw REAL,
            sp_lose REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 插入测试用户数据
        test_users = [
            ("admin", "admin@sport-lottery.com", 
             "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", 
             "admin,manager", "技术部"),
            ("analyst", "analyst@sport-lottery.com",
             "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
             "analyst", "数据分析部"),
            ("viewer", "viewer@sport-lottery.com",
             "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
             "viewer", "运营部")
        ]
        
        cursor.executemany(
            "INSERT INTO users (username, email, password_hash, roles, department) VALUES (?, ?, ?, ?, ?)",
            test_users
        )
        
        # 插入测试数据源
        test_data_sources = [
            ("500彩票网API", "api", "https://api.500.com/v1", "enabled", 2.5,
             "2026-01-28 10:30:00", "官方500彩票网API接口"),
            ("本地比赛数据", "file", "file:///data/local_matches.json", "enabled", 0.0,
             "2026-01-28 09:15:00", "本地存储的历史比赛数据文件"),
            ("测试数据源", "test", "test://mock/data", "disabled", 15.0,
             "2026-01-27 14:20:00", "用于测试的模拟数据源")
        ]
        
        cursor.executemany(
            "INSERT INTO data_sources (name, type, url, status, error_rate, last_checked, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            test_data_sources
        )
        
        # 插入测试比赛数据
        import random
        from datetime import datetime, timedelta
        
        today = datetime.now()
        test_matches = []
        
        for i in range(20):
            match_time = today + timedelta(days=i, hours=random.randint(14, 22))
            match_id = f"MATCH{1000 + i}"
            
            # 随机状态
            if i < 5:
                status = "finished"
                home_score = random.randint(0, 5)
                away_score = random.randint(0, 5)
            elif i == 5:
                status = "live"
                home_score = random.randint(0, 2)
                away_score = random.randint(0, 2)
            else:
                status = "scheduled"
                home_score = None
                away_score = None
            
            # 随机联赛
            leagues = ["英超", "西甲", "意甲", "德甲", "法甲"]
            league = leagues[i % len(leagues)]
            
            # 随机SP值
            sp_win = round(1.5 + random.random() * 2.0, 2)
            sp_draw = round(3.0 + random.random() * 1.5, 2)
            sp_lose = round(4.0 + random.random() * 3.0, 2)
            
            test_matches.append((
                match_id, league, f"球队{i*2}A", f"球队{i*2+1}B",
                match_time.strftime("%Y-%m-%d %H:%M:%S"), status,
                home_score, away_score, sp_win, sp_draw, sp_lose
            ))
        
        cursor.executemany(
            """INSERT INTO matches 
            (match_id, league, home_team, away_team, match_time, status, 
             home_score, away_score, sp_win, sp_draw, sp_lose) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            test_matches
        )
        
        # 提交事务
        conn.commit()
        
        # 验证数据插入
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM data_sources")
        ds_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        match_count = cursor.fetchone()[0]
        
        print(f"✅ 后端测试数据已生成:")
        print(f"   - 用户数: {user_count}")
        print(f"   - 数据源数: {ds_count}")
        print(f"   - 比赛数: {match_count}")
        print(f"   - 数据库文件: {db_path}")
        
        # 关闭连接
        conn.close()
        
        # 创建测试数据JSON文件
        test_data_json = {
            "users": test_users,
            "data_sources": test_data_sources[:3],  # 只取前3个
            "matches": test_matches[:5]  # 只取前5个
        }
        
        with open(test_db_dir / "test_data.json", "w", encoding="utf-8") as f:
            json.dump(test_data_json, f, indent=2, ensure_ascii=False)
    
    def create_test_configs(self):
        """创建测试配置文件"""
        print("⚙️  创建测试配置文件...")
        
        # 前端测试配置
        frontend_test_env = """# 前端测试环境配置
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENV=testing
VITE_USE_MOCK=true
VITE_TEST_USERNAME=admin
VITE_TEST_PASSWORD=admin123
VITE_TEST_TIMEOUT=30000
VITE_LOG_LEVEL=debug
"""
        
        with open(self.frontend_dir / ".env.test", "w", encoding="utf-8") as f:
            f.write(frontend_test_env)
        
        # 后端测试配置
        backend_test_env = """# 后端测试环境配置
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=test-secret-key-for-local-testing
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=INFO
TEST_MODE=true
"""
        
        with open(self.backend_dir / ".env.test", "w", encoding="utf-8") as f:
            f.write(backend_test_env)
        
        print("✅ 测试配置文件已创建")
    
    def run(self):
        """运行所有初始化步骤"""
        print("🚀 开始初始化测试数据...")
        print("="*50)
        
        try:
            self.init_frontend_test_data()
            print()
            
            self.init_backend_test_data()
            print()
            
            self.create_test_configs()
            print()
            
            print("="*50)
            print("🎉 测试数据初始化完成！")
            print()
            print("📋 下一步：")
            print("1. 运行前端测试: cd frontend && npm run test:run")
            print("2. 运行后端测试: cd backend && pytest tests/unit/ -v")
            print("3. 运行端到端测试: cd frontend && npx playwright test")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return 1
        
        return 0

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    initializer = TestDataInitializer(project_root)
    return initializer.run()

if __name__ == "__main__":
    sys.exit(main())

# AI_DONE: coder1 @2026-01-28T14:32:00