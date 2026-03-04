"""
简化版服务器，仅用于提供API接口
"""
from fastapi import FastAPI
import asyncio
from datetime import datetime, timedelta
from typing import List
import random

# 创建简化版的响应模型
class PublicMatchResponse:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# 创建FastAPI应用
app = FastAPI(title="竞彩足球扫盘系统", version="1.0.0")

# 模拟比赛数据
def generate_mock_matches(count=15):
    teams = ["曼城", "皇马", "拜仁", "国米", "巴黎", "利物浦", "切尔西", "阿森纳", "曼联", "巴萨", "尤文", "马竞"]
    leagues = ["英超", "西甲", "德甲", "意甲", "法甲", "欧冠", "欧联"]
    
    matches = []
    for i in range(count):
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        league = random.choice(leagues)
        
        # 生成未来几天内的随机时间
        future_time = datetime.now() + timedelta(days=random.randint(0, 3), hours=random.randint(18, 23), minutes=random.choice([0, 15, 30, 45]))
        
        match = {
            "id": f"mock_match_{i+1:03d}",
            "match_id": f"mock_{i+1:03d}",
            "home_team": home_team,
            "away_team": away_team,
            "league": league,
            "match_date": future_time.strftime("%Y-%m-%d %H:%M:%S"),
            "match_time": future_time.strftime("%Y-%m-%d %H:%M:%S"),
            "odds_home_win": round(random.uniform(1.5, 3.0), 2),
            "odds_draw": round(random.uniform(2.5, 4.0), 2),
            "odds_away_win": round(random.uniform(2.5, 5.0), 2),
            "status": "scheduled",
            "popularity": random.randint(1, 100),
            "predicted_result": random.choice(["home", "draw", "away"]),
            "prediction_confidence": round(random.uniform(0.6, 0.95), 2)
        }
        matches.append(match)
    
    return matches

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/public/matches/")
def get_public_matches(days_ahead: int = 3):
    """
    获取公开比赛数据，无需认证
    """
    # 生成模拟比赛数据
    matches = generate_mock_matches(15)
    
    # 过滤出指定天数内的比赛
    filtered_matches = []
    cutoff_date = datetime.now() + timedelta(days=days_ahead)
    
    for match in matches:
        match_time = datetime.strptime(match["match_time"], "%Y-%m-%d %H:%M:%S")
        if match_time <= cutoff_date:
            filtered_matches.append(match)
    
    return filtered_matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)