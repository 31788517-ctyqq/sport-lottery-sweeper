"""
Multi-source proxy fetcher.
Tries multiple public proxy list sources and extracts ip:port pairs.
"""
import logging
import random
import re
import time
from typing import Iterable, List, Tuple

import requests

logger = logging.getLogger(__name__)


DEFAULT_SOURCES = [
    "http://www.kxdaili.com/dailiip.html",
    "https://www.zdaye.com/Free/",
    "http://www.xsdaili.cn/dltq.html",
    "http://http.taiyangruanjian.com/free/",
    "https://ip.ihuan.me/",
    "https://proxy.ip3366.net/free/",
    "http://cn-proxy.com/",
    "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1",
    "https://proxy.horocn.com/free-china-proxy/all.html",
    "https://openproxy.space/list",
    "https://www.proxy-list.download/HTTP",
    "https://awmproxy.net/freeproxy.php",
    "https://raw.githubusercontent.com/zqHero/FreeIpAgent/master/Ips.txt",
    "https://www.kuaidaili.com/free/",
    "http://www.ip3366.net/free/",
]


class MultiSourceProxyFetcher:
    def __init__(self, sources: Iterable[str] = None, timeout: int = 15):
        self.sources = list(sources) if sources else list(DEFAULT_SOURCES)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        })

    def fetch_all(self, max_per_source: int = 200) -> List[Tuple[str, str]]:
        collected: List[Tuple[str, str]] = []
        for url in self.sources:
            try:
                logger.info(f"Fetching proxies from: {url}")
                text = self._get_text(url)
                pairs = self._extract_ip_ports(text)
                if max_per_source:
                    pairs = pairs[:max_per_source]
                collected.extend(pairs)
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as exc:
                logger.warning(f"Failed to fetch {url}: {exc}")
        # de-duplicate
        unique = list({(ip, port) for ip, port in collected})
        logger.info(f"Collected {len(unique)} unique proxies from {len(self.sources)} sources")
        return unique

    def _get_text(self, url: str) -> str:
        resp = self.session.get(url, timeout=self.timeout, proxies={"http": None, "https": None})
        resp.encoding = resp.encoding or "utf-8"
        return resp.text or ""

    @staticmethod
    def _extract_ip_ports(text: str) -> List[Tuple[str, str]]:
        pattern = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})\s*[:]\s*(\d{2,5})")
        results = []
        for ip, port in pattern.findall(text):
            if MultiSourceProxyFetcher._valid_ip(ip) and MultiSourceProxyFetcher._valid_port(port):
                results.append((ip, port))
        return results

    @staticmethod
    def _valid_ip(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    @staticmethod
    def _valid_port(port: str) -> bool:
        try:
            p = int(port)
            return 1 <= p <= 65535
        except ValueError:
            return False
