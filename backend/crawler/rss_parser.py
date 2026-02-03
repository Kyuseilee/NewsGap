"""
RSS Feed 解析器

解析 RSS/Atom feeds，提取文章信息
"""

import feedparser
from datetime import datetime, timedelta
from typing import List, Optional
from dateutil import parser as date_parser

from models import Article, Source, IndustryCategory
from crawler.fetcher import Fetcher


class RSSParser:
    """RSS/Atom feed 解析器"""
    
    def __init__(self):
        self.fetcher = Fetcher()
    
    async def parse(
        self,
        source: Source,
        hours: int = 24
    ) -> List[Article]:
        """
        解析 RSS feed
        
        Args:
            source: 信息源配置
            hours: 只获取最近多少小时的文章
            
        Returns:
            文章列表
        """
        try:
            # 获取 feed 内容
            content, _ = await self.fetcher.fetch(source.url)
            
            # 解析 feed
            feed = feedparser.parse(content)
            
            if feed.bozo and not feed.entries:
                # 解析失败
                raise ValueError(f"Failed to parse RSS feed: {source.url}")
            
            # 计算时间阈值（使用UTC时区避免比较问题）
            from datetime import timezone
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            articles = []
            for entry in feed.entries:
                # 提取发布时间
                published_at = self._extract_published_time(entry)
                
                # 时间过滤（确保时区一致）
                if published_at:
                    # 如果published_at没有时区信息，假设为UTC
                    if published_at.tzinfo is None:
                        published_at = published_at.replace(tzinfo=timezone.utc)
                    
                    if published_at < cutoff_time:
                        continue
                
                # 如果没有发布时间，使用当前时间（UTC）
                if not published_at:
                    published_at = datetime.now(timezone.utc)
                
                # 提取文章信息
                article = self._entry_to_article(entry, source, published_at)
                if article:
                    articles.append(article)
            
            return articles
        
        except Exception as e:
            raise ValueError(f"Error parsing RSS feed {source.url}: {str(e)}")
    
    def _extract_published_time(self, entry) -> Optional[datetime]:
        """从 feed entry 提取发布时间"""
        # 尝试多个可能的时间字段
        time_fields = ['published', 'updated', 'created']
        
        for field in time_fields:
            if hasattr(entry, field):
                time_str = getattr(entry, field)
                try:
                    # 使用 dateutil.parser 解析各种时间格式
                    return date_parser.parse(time_str)
                except Exception:
                    continue
        
        # 尝试 published_parsed / updated_parsed
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(entry.published_parsed))
            except Exception:
                pass
        
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(entry.updated_parsed))
            except Exception:
                pass
        
        return None
    
    def _entry_to_article(
        self,
        entry,
        source: Source,
        published_at: datetime
    ) -> Optional[Article]:
        """将 feed entry 转换为 Article 对象"""
        # 提取标题
        title = entry.get('title', '').strip()
        if not title:
            return None
        
        # 提取链接
        url = entry.get('link', '').strip()
        if not url:
            return None
        
        # 提取内容
        content = ''
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # 清理 HTML 标签（简单处理）
        import re
        content = re.sub(r'<[^>]+>', '', content)
        content = content.strip()
        
        if not content:
            content = title  # 如果没有内容，使用标题
        
        # 提取作者
        author = None
        if hasattr(entry, 'author'):
            author = entry.author
        elif hasattr(entry, 'authors') and entry.authors:
            author = entry.authors[0].get('name', None)
        
        # 创建 Article 对象
        from datetime import timezone
        
        # 确保时间都有时区信息
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        
        article = Article(
            title=title[:500],  # 限制标题长度
            url=url,
            source_id=source.id,
            source_name=source.name,
            content=content,
            summary=entry.get('summary', None),
            industry=source.industry,
            published_at=published_at,
            fetched_at=datetime.now(timezone.utc),
            author=author,
            tags=[]
        )
        
        return article
