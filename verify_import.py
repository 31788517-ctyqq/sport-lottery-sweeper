"""
验证数据导入结果
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.matches import FootballMatch


def verify_import():
    """验证数据导入结果"""
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 查询所有来自100qiu的数据
        hundred_qiu_matches = db.query(FootballMatch).filter(
            FootballMatch.match_id.like('hundred_qiu_%')
        ).all()
        
        print(f"数据库中找到 {len(hundred_qiu_matches)} 条来自100qiu的比赛数据")
        
        if hundred_qiu_matches:
            print("\n前5条记录示例:")
            for i, match in enumerate(hundred_qiu_matches[:5]):
                print(f"{i+1}. {match.home_team} VS {match.away_team}")
                print(f"   联赛: {match.league}")
                print(f"   时间: {match.match_time}")
                print(f"   状态: {match.status}")
                print()
        
        # 查询总数
        total_matches = db.query(FootballMatch).count()
        print(f"数据库中总共 {total_matches} 条比赛记录")
        
    except Exception as e:
        print(f"查询数据失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    verify_import()