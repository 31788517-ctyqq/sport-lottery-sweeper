#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞彩比赛信息智能爬虫 - VIPC JS Data Source
从 https://www.vipc.cn/js/app/live-index.js 获取比赛数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import time
import json
import pandas as pd
from datetime import datetime

# 导入自定义模块
try:
    from data_source import MatchInfo, Strategy, ScraperResult
    from sources import VipcCnJsSource # 修改导入，使用新的 JS 源
    module_available = True
except ImportError as e:
    logging.error(f"导入模块失败: {e}")
    module_available = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 检查 Pandas
try:
    pandas_available = True
except ImportError:
    pandas_available = False

class IntelligentVipcScraper:
    """智能竞彩爬虫主类"""
    def __init__(self):
        if not module_available:
            logger.error("核心模块不可用")
            self.js_source = None
        else:
            # 修改初始化，使用 VipcCnJsSource
            self.js_source = VipcCnJsSource()

    def run(self, days: int = 3) -> ScraperResult: # 修改默认值为 3
        """运行爬虫"""
        logger.info("=" * 60)
        logger.info(f"启动 VIPC JS 数据源爬虫 (获取未来数据)")
        logger.info("=" * 60)
        start_time = time.time()

        if not self.js_source:
            return ScraperResult(
                matches=[],
                strategy_used=Strategy.ALTERNATIVE_API, # JS 获取也算一种策略
                execution_time=0,
                success=False,
                error_message="JS源未初始化"
            )

        try:
            # 获取比赛数据
            raw_matches = self.js_source.get_matches()
            execution_time = time.time() - start_time
            success = len(raw_matches) > 0

            if success:
                logger.info(f"✓ JS数据源抓取成功，共获取 {len(raw_matches)} 场比赛")
                self._save_results(raw_matches)
                self._display_results(raw_matches)
            else:
                logger.warning("✗ JS数据源抓取成功但无有效数据")

            return ScraperResult(
                matches=raw_matches,
                strategy_used=Strategy.ALTERNATIVE_API, # 明确使用 JS 策略
                execution_time=execution_time,
                success=success,
                error_message="" if success else "无比赛数据"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"JS数据源爬虫运行出错: {e}")
            return ScraperResult(
                matches=[],
                strategy_used=Strategy.ALTERNATIVE_API, # 明确使用 JS 策略
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )

    def _save_results(self, matches: list):
        """保存结果"""
        if not matches:
            return
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存 JSON
        json_file = os.path.join(output_dir, f"matches_vipc_js_{timestamp}.json") # 修改文件名
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([m.to_dict() for m in matches], f, ensure_ascii=False, indent=2)
        logger.info(f"JSON 已保存: {json_file}")

        # 保存 CSV
        if pandas_available:
            csv_file = os.path.join(output_dir, f"matches_vipc_js_{timestamp}.csv") # 修改文件名
            df = pd.DataFrame([m.to_dict() for m in matches])
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"CSV 已保存: {csv_file}")

    def _display_results(self, matches: list):
        """打印结果"""
        logger.info("\n" + "=" * 40)
        for m in matches[:10]: # 只显示前10个
            time_str = m.kickoff_time.strftime('%m/%d %H:%M') if m.kickoff_time else 'N/A'
            logger.info(f"{m.match_id} {m.league} {m.home_team} vs {m.away_team} ({time_str}) - 状态: {m.status} - 策略: {m.strategy}")
        if len(matches) > 10:
            logger.info(f"... 还有 {len(matches) - 10} 场")
        logger.info("=" * 40)

def main():
    scraper = IntelligentVipcScraper()
    # 调用 run 方法
    result = scraper.run() # 移除了 days 参数，因为 JS 源可能不按天数过滤
    if result.success:
        print("\n程序执行完毕。")
    else:
        print(f"\n程序执行失败: {result.error_message}")

if __name__ == "__main__":
    main()