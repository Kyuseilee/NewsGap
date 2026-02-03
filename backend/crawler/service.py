"""
爬虫服务（实现 CrawlerInterface）
"""

from typing import List
from datetime import datetime, timedelta

from models import Source, Article, CrawlerInterface, SourceType
from crawler.fetcher import Fetcher
from crawler.rss_parser import RSSParser
from crawler.extractor import ContentExtractor


class CrawlerService(CrawlerInterface):
    """爬虫服务"""
    
    def __init__(self, proxy_config: dict = None):
        """
        Args:
            proxy_config: 代理配置，格式: {'http': 'http://host:port', 'https': 'https://host:port', 'socks5': 'socks5://host:port'}
        """
        self.fetcher = Fetcher(proxy_config=proxy_config)
        self.rss_parser = RSSParser(fetcher=self.fetcher)
        self.extractor = ContentExtractor(fetcher=self.fetcher)
    
    async def fetch(
        self,
        source: Source,
        hours: int = 24
    ) -> List[Article]:
        """
        从指定信息源爬取内容
        
        根据源类型选择合适的爬取方式：
        - RSS: 使用 RSS 解析器
        - WEB: 使用正文提取器
        """
        if source.source_type == SourceType.RSS:
            return await self.rss_parser.parse(source, hours)
        
        elif source.source_type == SourceType.WEB:
            # Web 源通常是单个文章 URL，直接提取
            article = await self.extractor.extract(source.url, source)
            
            # 检查时间过滤
            cutoff_time = datetime.now() - timedelta(hours=hours)
            if article.published_at >= cutoff_time:
                return [article]
            else:
                return []
        
        else:
            raise NotImplementedError(f"Source type {source.source_type} not supported yet")
    
    async def validate_source(self, source: Source) -> bool:
        """验证信息源是否可访问"""
        try:
            if source.source_type == SourceType.RSS:
                # 尝试获取并解析 RSS
                content, _ = await self.fetcher.fetch(source.url)
                import feedparser
                feed = feedparser.parse(content)
                return not feed.bozo or len(feed.entries) > 0
            
            elif source.source_type == SourceType.WEB:
                # 检查 URL 是否可访问
                return await self.fetcher.check_url(source.url)
            
            else:
                return False
        
        except Exception:
            return False
