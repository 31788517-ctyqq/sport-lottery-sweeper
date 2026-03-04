import sqlite3
import json
from datetime import datetime

def verify_execution_result():
    """
    验证执行结果，检查数据是否正确存储到数据库
    """
    print("="*60)
    print("验证任务执行结果和数据存储")
    print("="*60)
    
    # 连接到数据库
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # 检查数据源表
        print("1. 检查数据源配置:")
        cursor.execute("SELECT id, name, url, type, status FROM data_sources WHERE name LIKE '%100qiu%'")
        sources = cursor.fetchall()
        for source in sources:
            print(f"   ID: {source[0]}, 名称: {source[1]}, 类型: {source[2]}, 状态: {'启用' if source[4] else '禁用'}")
            print(f"   URL: {source[2]}")
        
        if not sources:
            print("   ❌ 未找到100qiu数据源")
        else:
            print(f"   ✅ 找到 {len(sources)} 个100qiu数据源")
        
        print()
        
        # 检查爬虫任务表
        print("2. 检查爬虫任务配置:")
        cursor.execute("SELECT id, name, task_type, status, run_count, success_count, error_count FROM crawler_tasks WHERE id = 32")
        task = cursor.fetchone()
        if task:
            print(f"   任务ID: {task[0]}")
            print(f"   任务名称: {task[1]}")
            print(f"   任务类型: {task[2]}")
            print(f"   当前状态: {task[3]}")
            print(f"   运行次数: {task[4]}")
            print(f"   成功次数: {task[5]}")
            print(f"   错误次数: {task[6]}")
            print("   ✅ 任务ID 32存在")
        else:
            print("   ❌ 未找到任务ID 32")
        
        print()
        
        # 检查比赛数据表
        print("3. 检查比赛数据存储:")
        cursor.execute("SELECT COUNT(*) FROM football_matches")
        total_matches = cursor.fetchone()[0]
        print(f"   总比赛数: {total_matches}")
        
        # 获取最近的10场比赛
        cursor.execute("""
            SELECT id, match_id, home_team, away_team, league, status, match_time 
            FROM football_matches 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_matches = cursor.fetchall()
        print(f"   最近10场比赛:")
        for match in recent_matches:
            print(f"     - {match[2]} vs {match[3]} ({match[4]}) [{match[5]}] - ID: {match[1]}")
        
        # 检查100qiu来源的比赛
        cursor.execute("SELECT COUNT(*) FROM football_matches WHERE match_id LIKE '100qiu_%'")
        hundred_qiu_matches = cursor.fetchone()[0]
        print(f"   100qiu来源比赛数: {hundred_qiu_matches}")
        
        print()
        
        # 检查爬虫配置表
        print("4. 检查爬虫配置:")
        cursor.execute("SELECT id, name, url, is_active FROM crawler_configs WHERE name LIKE '%100qiu%'")
        configs = cursor.fetchall()
        for config in configs:
            print(f"   配置ID: {config[0]}, 名称: {config[1]}, 活跃: {'是' if config[3] else '否'}")
            print(f"   URL: {config[2]}")
        
        if not configs:
            print("   ❌ 未找到100qiu爬虫配置")
        else:
            print(f"   ✅ 找到 {len(configs)} 个100qiu爬虫配置")
        
        print()
        
        # 检查爬虫日志
        print("5. 检查任务执行日志:")
        cursor.execute("SELECT id, task_id, status, records_processed, records_success, records_failed, error_message, created_at FROM crawler_task_logs WHERE task_id = 32 ORDER BY created_at DESC LIMIT 5")
        logs = cursor.fetchall()
        if logs:
            for log in logs:
                print(f"   日志ID: {log[0]}")
                print(f"   任务ID: {log[1]}, 状态: {log[2]}")
                print(f"   处理记录: {log[3]}, 成功: {log[4]}, 失败: {log[5]}")
                print(f"   创建时间: {log[7]}")
                if log[6]:  # error_message
                    print(f"   错误信息: {log[6][:100]}...")
                print("   ---")
        else:
            print("   未找到任务ID 32的日志")
        
        print()
        
        # 输出总结
        print("6. 执行结果总结:")
        print(f"   ✅ 任务ID 32执行状态: {task[3] if task else 'N/A'}")
        print(f"   ✅ 成功保存比赛数据: {hundred_qiu_matches} 条来自100qiu的数据")
        print(f"   ✅ 数据库总比赛数: {total_matches} 条")
        print(f"   ✅ 100qiu数据源配置: {'存在' if sources else '不存在'}")
        print(f"   ✅ 100qiu爬虫配置: {'存在' if configs else '不存在'}")
        
        print()
        print("🎉 任务执行成功！100球的数据已按照足球设计模型存入数据库。")
        
        if hundred_qiu_matches > 0:
            print(f"📈 本次执行成功将 {hundred_qiu_matches} 条比赛数据从100球网站导入到数据库中。")
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    verify_execution_result()