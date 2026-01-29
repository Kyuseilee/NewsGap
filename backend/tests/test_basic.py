"""
单元测试

基础的测试框架和示例测试
"""

import pytest
import asyncio
from datetime import datetime

import sys
from pathlib import Path
# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Article, Source, IndustryCategory, SourceType


class TestModels:
    """测试数据模型"""
    
    def test_article_creation(self):
        """测试文章创建"""
        article = Article(
            title="测试文章",
            url="https://example.com/test",
            content="这是测试内容",
            industry=IndustryCategory.AI,
            tags=["测试", "示例"],
            published_at=datetime.now(),
            fetched_at=datetime.now(),
            language="zh",
            archived=False
        )
        
        assert article.title == "测试文章"
        assert article.industry == IndustryCategory.AI
        assert len(article.tags) == 2
    
    def test_source_creation(self):
        """测试信息源创建"""
        source = Source(
            name="测试源",
            url="https://example.com/feed",
            source_type=SourceType.RSS,
            industry=IndustryCategory.TECH,
            enabled=True,
            fetch_interval_hours=24
        )
        
        assert source.name == "测试源"
        assert source.source_type == SourceType.RSS
        assert source.enabled is True


class TestStorage:
    """测试存储模块"""
    
    @pytest.mark.asyncio
    async def test_database_initialization(self):
        """测试数据库初始化"""
        from storage.database import Database
        
        db = Database(db_path=":memory:")
        await db.initialize()
        
        # 测试是否成功初始化
        sources = await db.get_sources()
        assert isinstance(sources, list)
    
    @pytest.mark.asyncio
    async def test_save_and_get_article(self):
        """测试保存和获取文章"""
        from storage.database import Database
        
        db = Database(db_path=":memory:")
        await db.initialize()
        
        article = Article(
            title="测试文章",
            url="https://example.com/test-" + str(datetime.now().timestamp()),
            content="测试内容",
            industry=IndustryCategory.AI,
            tags=[],
            published_at=datetime.now(),
            fetched_at=datetime.now(),
            language="zh",
            archived=False
        )
        
        # 保存
        article_id = await db.save_article(article)
        assert article_id is not None
        
        # 获取
        loaded = await db.get_article(article_id)
        assert loaded is not None
        assert loaded.title == "测试文章"


class TestCrawler:
    """测试爬虫模块"""
    
    def test_fetcher_initialization(self):
        """测试 Fetcher 初始化"""
        from crawler.fetcher import Fetcher
        
        fetcher = Fetcher()
        assert fetcher.timeout == 30
        assert fetcher.max_retries == 3


class TestAnalyzer:
    """测试分析模块"""
    
    def test_analyzer_initialization(self):
        """测试 Analyzer 初始化"""
        from analyzer import Analyzer
        
        analyzer = Analyzer(llm_backend="ollama")
        assert analyzer.adapter is not None
        
        model_info = analyzer.get_model_info()
        assert "backend" in model_info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
