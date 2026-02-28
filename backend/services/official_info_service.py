"""
官方信息验证与管理服务
提供官方链接验证、更新和状态管理功能
"""

import re
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from backend.config.entity_mappings import TEAM_MAPPINGS, LEAGUE_MAPPINGS
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# 社交媒体平台验证规则
PLATFORM_VALIDATION_RULES = {
    "website": {
        "pattern": r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/]?",
        "verification_methods": [
            "check_http_status",
            "check_meta_tags"
        ]
    },
    "twitter": {
        "pattern": r"https?://(?:www\.)?twitter\.com/[\w_]+",
        "verification_methods": [
            "check_twitter_profile"
        ]
    },
    "facebook": {
        "pattern": r"https?://(?:www\.)?facebook\.com/[\w\.\-]+",
        "verification_methods": [
            "check_facebook_page"
        ]
    },
    "instagram": {
        "pattern": r"https?://(?:www\.)?instagram\.com/[\w\.\-]+",
        "verification_methods": [
            "check_instagram_profile"
        ]
    },
    "weibo": {
        "pattern": r"https?://(?:www\.)?weibo\.com/[\w\.\-]+",
        "verification_methods": [
            "check_weibo_profile"
        ]
    }
}

class OfficialInfoService:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "SportLotterySweeper/1.0 (+https://yourdomain.com/bot)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
            }
        )
    
    async def verify_all_official_links(self, entity_type: str = "all") -> Dict[str, Any]:
        """验证所有实体的官方链接状态"""
        results = {
            "teams": {},
            "leagues": {},
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "needs_update": 0,
                "last_verified": datetime.utcnow().isoformat()
            }
        }
        
        if entity_type in ["all", "teams"]:
            for team_id, team_data in TEAM_MAPPINGS.items():
                if "official_info" in team_data:
                    verification = await self.verify_entity_official_info("team", team_id, team_data["official_info"])
                    results["teams"][team_id] = verification
                    self._update_summary(results["summary"], verification)
        
        if entity_type in ["all", "leagues"]:
            for league_id, league_data in LEAGUE_MAPPINGS.items():
                if "official_info" in league_data:
                    verification = await self.verify_entity_official_info("league", league_id, league_data["official_info"])
                    results["leagues"][league_id] = verification
                    self._update_summary(results["summary"], verification)
        
        return results
    
    async def verify_entity_official_info(self, entity_type: str, entity_id: str, official_info: Dict) -> Dict:
        """验证单个实体的官方信息"""
        verification_result = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": "valid",
            "details": {},
            "last_verified": datetime.utcnow().isoformat(),
            "verification_time": time.time()
        }
        
        for platform, url in official_info.items():
            if platform in ["verified", "last_verified"]:
                continue
                
            if not url:
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "missing",
                    "message": "无官方链接"
                }
                continue
                
            # 检查URL格式
            if not self._validate_url_format(platform, url):
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "invalid_format",
                    "message": "URL格式无效"
                }
                verification_result["status"] = "invalid"
                continue
                
            # 验证URL可达性和真实性
            try:
                result = await self._verify_platform_url(platform, url)
                verification_result["details"][platform] = result
                
                if result["status"] != "valid":
                    verification_result["status"] = "invalid"
            except Exception as e:
                logger.error(f"验证{platform}链接失败 {url}: {str(e)}", exc_info=True)
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "error",
                    "message": str(e)
                }
                verification_result["status"] = "error"
        
        return verification_result
    
    def _validate_url_format(self, platform: str, url: str) -> bool:
        """验证URL格式是否符合平台要求"""
        if platform not in PLATFORM_VALIDATION_RULES:
            # 通用URL验证
            return bool(re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/]?", url))
        
        rule = PLATFORM_VALIDATION_RULES[platform]
        return bool(re.match(rule["pattern"], url))
    
    async def _verify_platform_url(self, platform: str, url: str) -> Dict:
        """验证特定平台的URL"""
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": None,
            "redirect_url": None,
            "verification_time": time.time()
        }
        
        # 首先检查HTTP状态
        try:
            response = await self._make_request_with_retry(url)
            result["http_status"] = response.status_code
            result["redirect_url"] = str(response.url)
            
            if response.status_code != 200:
                result["status"] = "unreachable"
                result["message"] = f"HTTP状态码: {response.status_code}"
                return result
        except Exception as e:
            result["status"] = "unreachable"
            result["message"] = f"请求失败: {str(e)}"
            return result
        
        # 根据平台执行特定验证
        if platform == "website":
            return self._verify_website(response)
        elif platform == "twitter":
            return self._verify_twitter(response, url)
        elif platform == "facebook":
            return self._verify_facebook(response, url)
        elif platform == "instagram":
            return self._verify_instagram(response, url)
        elif platform == "weibo":
            return self._verify_weibo(response, url)
        
        return result
    
    async def _make_request_with_retry(self, url: str) -> httpx.Response:
        """带重试机制的HTTP请求"""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url)
                return response
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))  # 指数退避
        
        raise Exception(f"请求失败，已达到最大重试次数: {self.max_retries}")
    
    def _verify_website(self, response: httpx.Response) -> Dict:
        """验证官方网站"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查关键meta标签
        title = soup.title.string if soup.title else ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        
        result = {
            "url": str(response.url),
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "title": title[:100] if title else "",
            "has_meta_desc": bool(meta_desc),
            "verification_time": time.time()
        }
        
        # 检查是否包含球队/联赛名称
        if "error" in response.text.lower() or "404" in response.text:
            result["status"] = "invalid_content"
            result["message"] = "页面包含错误信息"
        elif not title or len(title) < 5:
            result["status"] = "invalid_content"
            result["message"] = "页面标题无效"
            
        return result
    
    def _verify_twitter(self, response: httpx.Response, url: str) -> Dict:
        """验证Twitter账号"""
        # 实际应用中应使用Twitter API进行验证
        # 这里简化处理，检查页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time()
        }
        
        # 检查是否包含Twitter特征元素
        if soup.find("meta", property="og:site_name", content="Twitter"):
            # 检查是否为官方认证账号
            if soup.find("svg", {"aria-label": "Verified account"}):
                result["verified_badge"] = True
            return result
        
        result["status"] = "invalid_content"
        result["message"] = "非Twitter官方页面"
        return result
    
    def _verify_facebook(self, response: httpx.Response, url: str) -> Dict:
        """验证Facebook页面"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time()
        }
        
        # 检查Facebook页面特征
        if "facebook.com" in str(response.url):
            if soup.find("meta", property="og:type", content="website"):
                return result
        
        result["status"] = "invalid_content"
        result["message"] = "非Facebook官方页面"
        return result
    
    def _verify_instagram(self, response: httpx.Response, url: str) -> Dict:
        """验证Instagram账号"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time()
        }
        
        # 检查Instagram页面特征
        if "instagram.com" in str(response.url):
            if soup.find("meta", property="og:type", content="profile"):
                return result
        
        result["status"] = "invalid_content"
        result["message"] = "非Instagram官方页面"
        return result
    
    def _verify_weibo(self, response: httpx.Response, url: str) -> Dict:
        """验证微博账号"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time()
        }
        
        # 检查微博页面特征
        if "weibo.com" in str(response.url):
            if soup.find("meta", attrs={"name": "appkey"}):
                return result
        
        result["status"] = "invalid_content"
        result["message"] = "非微博官方页面"
        return result
    
    def _update_summary(self, summary: Dict, verification: Dict):
        """更新验证摘要"""
        summary["total"] += 1
        
        if verification["status"] == "valid":
            summary["valid"] += 1
        else:
            summary["invalid"] += 1
            
        # 如果上次验证超过30天，标记为需要更新
        last_verified = datetime.fromisoformat(verification["last_verified"])
        if datetime.utcnow() - last_verified > timedelta(days=30):
            summary["needs_update"] += 1
    
    async def update_official_info(self, entity_type: str, entity_id: str, new_info: Dict) -> bool:
        """更新实体的官方信息"""
        try:
            # 获取当前映射
            if entity_type == "team":
                current = TEAM_MAPPINGS.get(entity_id)
            else:
                current = LEAGUE_MAPPINGS.get(entity_id)
                
            if not current:
                return False
                
            # 更新official_info
            if "official_info" not in current:
                current["official_info"] = {}
                
            current["official_info"].update(new_info)
            current["official_info"]["last_verified"] = datetime.utcnow().isoformat()

            # Respect explicit verified state from caller instead of forcing True.
            if "verified" in new_info:
                current["official_info"]["verified"] = bool(new_info["verified"])
            else:
                current["official_info"]["verified"] = bool(current["official_info"].get("verified", False))
            
            # 保存更新（在实际项目中，这里应该是数据库更新）
            # update_entity_mapping(entity_type, entity_id, current)
            return True
        except Exception as e:
            logger.error(f"更新{entity_type} {entity_id}官方信息失败: {str(e)}", exc_info=True)
            return False
    
    async def discover_official_links(self, entity_type: str, entity_id: str) -> Dict:
        """尝试发现实体的官方链接"""
        # 实现搜索引擎查询和模式匹配逻辑
        # 这里简化实现
        results = {
            "website": None,
            "twitter": None,
            "facebook": None,
            "instagram": None,
            "weibo": None,
            "confidence": 0.0,
            "sources": []
        }
        
        # 模拟搜索引擎查询
        search_queries = [
            f"{entity_id.replace('_', ' ')} official website",
            f"{entity_id.replace('_', ' ')} twitter",
            f"{entity_id.replace('_', ' ')} facebook"
        ]
        
        # 实际应用中应调用搜索引擎API
        for query in search_queries:
            # 模拟搜索结果
            if "website" in query:
                results["website"] = f"https://www.{entity_id}.com/"
                results["confidence"] = max(results["confidence"], 0.7)
                results["sources"].append("search_engine")
            elif "twitter" in query:
                results["twitter"] = f"https://twitter.com/{entity_id}"
                results["confidence"] = max(results["confidence"], 0.6)
        
        return results

# 单例实例
official_info_service = OfficialInfoService()
