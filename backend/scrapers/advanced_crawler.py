class AdvancedCrawler:
    """高级爬虫协调器"""
    
    def __init__(self):
        self.downloader = downloader
        self.parser = parser
        self.pipeline = pipeline
        self.logger = logging.getLogger(__name__)
        self.initialized = False
    
    async def initialize(self):
        """初始化爬虫系统"""
        if not self.initialized:
            await initialize_scheduler()
            await get_storage()
            self.initialized = True
            self.logger.info("高级爬虫系统初始化完成")
    
    async def crawl_sporttery_matches(self, days_ahead: int = 3) -> List[Dict[str, Any]]:
        """爬取竞彩网比赛数据"""
        await self.initialize()
        
        self.logger.info(f"开始爬取未来 {days_ahead} 天的竞彩比赛数据")
        
        try:
            # 使用Downloader获取页面内容
            async with self.downloader as dl:
                # 尝试获取竞彩网首页
                html_content = await dl.fetch(
                    "https://www.sporttery.cn/jc/zqszsc/", 
                    use_playwright=True  # 使用Playwright处理动态内容
                )
                
                if not html_content:
                    # 如果获取不到竞彩网数据，尝试备用网址
                    self.logger.warning("未能获取竞彩网页面内容，尝试备用数据源")
                    backup_urls = [
                        "https://www.sporttery.cn/",
                        "https://www.sporttery.cn/jc/"
                    ]
                    
                    for url in backup_urls:
                        html_content = await dl.fetch(url, use_playwright=True)
                        if html_content:
                            break
                
                if not html_content:
                    self.logger.warning("未能获取任何页面内容，使用模拟数据")
                    return self._generate_mock_data(days_ahead)
                
                # 使用Parser解析数据
                matches = self.parser.parse_sporttery_data(html_content)
                
                # 检查是否只返回了模拟数据
                if all('source' in match and match['source'] == 'mock' for match in matches):
                    self.logger.warning("解析结果仅为模拟数据，尝试使用更智能的解析方法")
                    # 使用更智能的解析方法
                    matches = self._smart_parse_content(html_content)
                
                # 如果仍然没有获取到有效数据，使用模拟数据
                if not matches or all(not match.get('home_team') or not match.get('away_team') for match in matches):
                    self.logger.warning("未能解析到有效比赛数据，使用模拟数据")
                    return self._generate_mock_data(days_ahead)
                
                # 使用Pipeline处理数据
                processed_matches = await self.pipeline.process_batch(matches)
                
                # 仅保存有效的处理后数据
                valid_matches = [match for match in processed_matches if match.get('home_team') and match.get('away_team')]
                
                return valid_matches
        
        except Exception as e:
            self.logger.error(f"爬取竞彩网比赛数据失败: {str(e)}")
            return []