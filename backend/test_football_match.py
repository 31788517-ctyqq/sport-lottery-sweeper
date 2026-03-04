#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接从文件导入
from backend.models.matches import FootballMatch
from backend.database import SessionLocal

def test_football_match():
    # 创建会话
    db = SessionLocal()
    
    try:
        # 查询所有记录
        matches = db.query(FootballMatch).all()
        print(f"Total FootballMatch records: {len(matches)}")
        
        if matches:
            for match in matches[:5]:
                print(f"ID: {match.id}, match_id: {match.match_id}, {match.home_team} vs {match.away_team}")
        else:
            print("No FootballMatch records found")
            
        # 尝试插入一条测试记录
        from datetime import datetime
        test_match = FootballMatch(
            match_id="test_001",
            home_team="测试主队",
            away_team="测试客队",
            match_time=datetime(2026, 2, 7, 20, 0, 0),
            league="测试联赛",
            status="pending"
        )
        db.add(test_match)
        db.commit()
        print("Test record inserted successfully")
        
        # 再次查询
        matches = db.query(FootballMatch).all()
        print(f"Total FootballMatch records after insert: {len(matches)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_football_match()