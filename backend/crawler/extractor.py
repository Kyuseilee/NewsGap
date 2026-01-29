"""
网页正文提取器

使用 readability-lxml 提取网页正文内容
"""

import re
from datetime import datetime
from typing import Optional
from readability import Document
from bs4 import BeautifulSoup

from models import Article, Source
from crawler.fetcher import Fetcher


class ContentExtractor:
    """网页正文提取器"""
    
    def __init__(self):
        self.fetcher = Fetcher()
    
    async def extract(
        self,
        url: str,
        source: Optional[Source] = None
    ) -> Article:
        """
        从网页提取文章内容
        
        Args:
            url: 文章 URL
            source: 信息源配置（可选）
            
        Returns:
            Article 对象
        """
        # 获取网页内容
        html, _ = await self.fetcher.fetch(url)
        
        # 使用 readability 提取正文
        doc = Document(html)
        
        # 标题
        title = doc.title()
        if not title:
            title = self._extract_title_from_html(html)
        
        # 正文（HTML）
        content_html = doc.summary()
        
        # 转换为纯文本
        content = self._html_to_text(content_html)
        
        # 生成摘要（取前 200 字）
        summary = content[:200] + "..." if len(content) > 200 else content
        
        # 提取元数据
        metadata = self._extract_metadata(html)
        
        # 确定行业分类
        industry = source.industry if source else self._guess_industry(content)
        
        return Article(
            title=title,
            url=url,
            source_id=source.id if source else None,
            source_name=source.name if source else self._extract_domain(url),
            content=content,
            summary=summary,
            industry=industry,
            published_at=metadata.get('published_at', datetime.now()),
            author=metadata.get('author'),
            word_count=len(content),
            tags=[],
            metadata={
                'extraction_method': 'readability',
                **metadata
            }
        )
    
    def _html_to_text(self, html: str) -> str:
        """将 HTML 转换为纯文本"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 获取文本
        text = soup.get_text()
        
        # 清理空白
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_title_from_html(self, html: str) -> str:
        """从 HTML 中提取标题"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 尝试多种方式提取标题
        title_selectors = [
            ('meta[property="og:title"]', 'content'),
            ('meta[name="twitter:title"]', 'content'),
            ('title', 'text'),
            ('h1', 'text'),
        ]
        
        for selector, attr_type in title_selectors:
            element = soup.select_one(selector)
            if element:
                if attr_type == 'content':
                    title = element.get('content', '')
                else:
                    title = element.get_text()
                
                if title:
                    return title.strip()
        
        return "Untitled"
    
    def _extract_metadata(self, html: str) -> dict:
        """提取页面元数据"""
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {}
        
        # 作者
        author_selectors = [
            ('meta[name="author"]', 'content'),
            ('meta[property="article:author"]', 'content'),
            ('.author', 'text'),
        ]
        
        for selector, attr_type in author_selectors:
            element = soup.select_one(selector)
            if element:
                if attr_type == 'content':
                    metadata['author'] = element.get('content', '').strip()
                else:
                    metadata['author'] = element.get_text().strip()
                break
        
        # 发布时间
        time_selectors = [
            ('meta[property="article:published_time"]', 'content'),
            ('meta[name="publishdate"]', 'content'),
            ('time', 'datetime'),
        ]
        
        for selector, attr_type in time_selectors:
            element = soup.select_one(selector)
            if element:
                time_str = None
                if attr_type == 'content':
                    time_str = element.get('content', '').strip()
                elif attr_type == 'datetime':
                    time_str = element.get('datetime', '').strip()
                
                if time_str:
                    try:
                        from dateutil import parser as date_parser
                        metadata['published_at'] = date_parser.parse(time_str)
                    except Exception:
                        pass
                    break
        
        # 描述
        desc_element = soup.select_one('meta[name="description"]')
        if desc_element:
            metadata['description'] = desc_element.get('content', '').strip()
        
        # 关键词
        keywords_element = soup.select_one('meta[name="keywords"]')
        if keywords_element:
            keywords = keywords_element.get('content', '').strip()
            metadata['keywords'] = [k.strip() for k in keywords.split(',')]
        
        return metadata
    
    def _extract_domain(self, url: str) -> str:
        """从 URL 提取域名"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def _guess_industry(self, content: str) -> str:
        """根据内容猜测行业分类（简单实现）"""
        from models import IndustryCategory
        
        # 关键词映射（简化版）
        keywords_map = {
            IndustryCategory.AI: ['人工智能', 'AI', '机器学习', '深度学习', 'LLM', 'GPT'],
            IndustryCategory.TECH: ['科技', '技术', '软件', '硬件', '互联网'],
            IndustryCategory.FINANCE: ['金融', '财经', '股票', '投资', '银行'],
            IndustryCategory.HEALTHCARE: ['医疗', '健康', '医药', '生物'],
            IndustryCategory.ENERGY: ['能源', '电力', '新能源', '石油'],
        }
        
        content_lower = content.lower()
        
        for industry, keywords in keywords_map.items():
            if any(keyword.lower() in content_lower for keyword in keywords):
                return industry
        
        return IndustryCategory.OTHER
