#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models.matches import FootballMatch

def test_orm():
    db = SessionLocal()
    try:
        # 查询所有记录
        matches = db.query(FootballMatch).all()
        print(f"ORM query - Total records: {len(matches)}")
        
        # 尝试插入新记录
        from datetime import datetime
        new_match = FootballMatch(
            match_id="test_002",
            home_team="ORM测试主队",
            away_team="ORM测试客队",
            match_time=datetime(2026, 2, 7, 21, 0, 0),
            league="ORM测试联赛",
            status="pending"
        )
        db.add(new_match)
        db.commit()
        print("ORM insert successful")
        
        # 再次查询
        matches = db.query(FootballMatch).all()
        print(f"ORM query after insert - Total records: {len(matches)}")
        
        for match in matches:
            print(f"  {match.match_id}: {match.home_team} vs {match.away_team}")
            
    except Exception as e:
        print(f"ORM Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_orm()