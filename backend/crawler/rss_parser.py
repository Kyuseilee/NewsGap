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
            
            # 计算时间阈值
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            articles = []
            for entry in feed.entries:
                # 提取发布时间
                published_at = self._extract_published_time(entry)
                
                # 时间过滤
                if published_at and published_at < cutoff_time:
                    continue
                
                # 如果没有发布时间，使用当前时间
                if not published_at:
                    published_at = datetime.now()
                
                # 提取文章信息
                article = self._entry_to_article(entry, source, published_at)
                if article:
                    articles.append(article)
            
            return articles
        
        except Exception as e:
            raise Exception(f"Error parsing RSS feed {source.url}: {str(e)}")
    
    def _extract_published_time(self, entry) -> Optional[datetime]:
        """提取文章发布时间"""
        # RSS 中时间字段的可能名称
        time_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in time_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except Exception:
                        pass
        
        # 尝试解析字符串格式的时间
        for field in ['published', 'updated', 'created']:
            if hasattr(entry, field):
                time_str = getattr(entry, field)
                if time_str:
                    try:
                        return date_parser.parse(time_str)
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
        try:
            # 标题
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # URL
            url = entry.get('link', '').strip()
            if not url:
                return None
            
            # 内容（优先使用 content，其次 summary）
            content = ""
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].get('value', '')
            elif hasattr(entry, 'summary'):
                content = entry.summary
            
            # 移除 HTML 标签（简单处理）
            content = self._strip_html(content)
            
            if not content:
                content = title  # 至少有标题
            
            # 摘要
            summary = None
            if hasattr(entry, 'summary') and entry.summary:
                summary = self._strip_html(entry.summary)
                # 限制摘要长度
                if len(summary) > 500:
                    summary = summary[:500] + "..."
            
            # 作者
            author = None
            if hasattr(entry, 'author') and entry.author:
                author = entry.author
            
            # 字数统计
            word_count = len(content)
            
            return Article(
                title=title,
                url=url,
                source_id=source.id,
                source_name=source.name,
                content=content,
                summary=summary,
                industry=source.industry,
                published_at=published_at,
                author=author,
                word_count=word_count,
                tags=[],  # RSS 通常不提供标签，后续可通过 LLM 提取
                metadata={
                    'feed_url': source.url,
                    'source_type': 'rss'
                }
            )
        
        except Exception as e:
            # 跳过解析失败的条目
            return None
    
    def _strip_html(self, html: str) -> str:
        """移除 HTML 标签"""
        if not html:
            return ""
        
        # 简单的 HTML 标签移除（实际项目中应使用专门的库）
        import re
        
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除所有 HTML 标签
        html = re.sub(r'<[^>]+>', '', html)
        
        # 解码 HTML 实体
        import html as html_module
        html = html_module.unescape(html)
        
        # 清理多余空白
        html = re.sub(r'\s+', ' ', html)
        html = html.strip()
        
        return html
