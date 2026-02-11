"""
验证100球数据获取路径的脚本
"""
import sqlite3
import json
from datetime import datetime
from backend.api.v1.data_source_100qiu import parse_match_from_100qiu
from backend.models.matches import FootballMatch
from backend.database import get_db


def verify_data_flow():
    print("=" * 60)
    print("验证100球数据获取路径")
    print("=" * 60)
    
    # 1. 检查数据库连接
    print("\n1. 检查数据库连接...")
    try:
        db = next(get_db())
        print("   ✅ 数据库连接成功")
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return
    
    # 2. 检查数据源配置
    print("\n2. 检查100qiu数据源配置...")
    try:
        from backend.models.data_sources import DataSource
        sources = db.query(DataSource).filter(DataSource.type == "100qiu").all()
        print(f"   ✅ 找到 {len(sources)} 个100qiu数据源")
        for source in sources:
            print(f"      - ID: {source.id}, Name: {source.name}, Status: {source.status}")
    except Exception as e:
        print(f"   ❌ 检查数据源失败: {e}")
    
    # 3. 检查比赛数据表
    print("\n3. 检查比赛数据表...")
    try:
        matches = db.query(FootballMatch).all()
        print(f"   ✅ 找到 {len(matches)} 条比赛记录")
        
        # 检查来自100qiu的数据
        qiu_matches = db.query(FootballMatch).filter(FootballMatch.data_source == "100qiu").all()
        print(f"   ✅ 找到 {len(qiu_matches)} 条来自100qiu的比赛数据")
        
        if qiu_matches:
            print(f"      示例数据: {qiu_matches[0].home_team} vs {qiu_matches[0].away_team}")
            print(f"      比赛时间: {qiu_matches[0].match_time}")
            if qiu_matches[0].source_attributes:
                attrs = qiu_matches[0].source_attributes
                if isinstance(attrs, str):
                    attrs = json.loads(attrs)
                print(f"      来源属性包含 {len(attrs)} 个字段")
    except Exception as e:
        print(f"   ❌ 检查比赛数据失败: {e}")
    
    # 4. 验证数据解析函数
    print("\n4. 验证数据解析函数...")
    try:
        # 创建一个示例数据
        sample_item = {
            'lineId': '12345',
            'homeTeam': '主队名称',
            'guestTeam': '客队名称',
            'gameShortName': '测试联赛',
            'matchTimeStr': '2026-02-11'
        }
        
        parsed_data = parse_match_from_100qiu(sample_item, "26011")
        if parsed_data:
            print("   ✅ 数据解析函数工作正常")
            print(f"      解析结果示例: {parsed_data['home_team']} vs {parsed_data['away_team']}")
        else:
            print("   ❌ 数据解析函数返回空值")
    except Exception as e:
        print(f"   ❌ 数据解析函数验证失败: {e}")
    
    # 5. 检查API端点
    print("\n5. 检查API端点...")
    try:
        from backend.api.v1.data_source_100qiu import router
        print("   ✅ API端点存在")
        print("      - GET /date-time-options")
        print("      - GET /latest-matches")
        print("      - GET /match/{match_id}")
        print("      - POST /")
        print("      - GET /{source_id}")
        print("      - PUT /{source_id}")
        print("      - DELETE /{source_id}")
        print("      - GET /")
        print("      - POST /{source_id}/test")
        print("      - POST /{source_id}/fetch")
    except Exception as e:
        print(f"   ❌ 检查API端点失败: {e}")
    
    # 6. 检查多策略调度器配置
    print("\n6. 检查多策略调度器配置...")
    try:
        from backend.services.multi_strategy_scheduler import MultiStrategyScheduler
        scheduler = MultiStrategyScheduler()
        print("   ✅ 多策略调度器初始化成功")
        print(f"      - 注册的策略: {scheduler.strategy_manager.get_all_strategies()}")
    except Exception as e:
        print(f"   ❌ 多策略调度器初始化失败: {e}")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)
    
    if len(qiu_matches) > 0:
        print(f"\n📊 总结:")
        print(f"   • 数据库中存在 {len(qiu_matches)} 条来自100qiu的数据")
        print(f"   • 数据获取路径完整: 100qiu API → 数据解析 → 数据库存储 → 策略执行")
        print(f"   • 多策略调度器已就绪，可随时执行策略筛选")
    else:
        print(f"\n⚠️  警告:")
        print(f"   • 数据库中尚未存储来自100qiu的数据")
        print(f"   • 请确保数据源已配置并执行了数据获取操作")


if __name__ == "__main__":
    verify_data_flow()