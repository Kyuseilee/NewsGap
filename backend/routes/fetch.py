"""
爬取路由

处理文章爬取请求
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from models import FetchRequest, FetchResponse, IndustryCategory
from storage.database import Database
from crawler.service import CrawlerService

router = APIRouter(prefix="/api/fetch", tags=["fetch"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_crawler():
    """依赖注入：爬虫"""
    return CrawlerService()


@router.post("", response_model=FetchResponse)
async def fetch_articles(
    request: FetchRequest,
    db: Database = Depends(get_db),
    crawler: CrawlerService = Depends(get_crawler)
):
    """
    爬取文章
    
    根据行业和时间范围从配置的信息源爬取文章
    """
    import time
    start_time = time.time()
    
    # 获取信息源
    sources = await db.get_sources(
        industry=request.industry,
        enabled_only=True
    )
    
    # 如果指定了特定源，过滤
    if request.source_ids:
        sources = [s for s in sources if s.id in request.source_ids]
    
    if not sources:
        raise HTTPException(
            status_code=404,
            detail=f"未找到行业 '{request.industry}' 的可用信息源"
        )
    
    # 从每个源爬取
    article_ids = []
    source_names = []
    
    for source in sources:
        try:
            articles = await crawler.fetch(source, hours=request.hours)
            
            # 保存文章
            for article in articles:
                article_id = await db.save_article(article)
                article_ids.append(article_id)
            
            source_names.append(source.name)
            
            # 更新源的最后爬取时间
            from datetime import datetime
            source.last_fetched_at = datetime.now()
            await db.save_source(source)
        
        except Exception as e:
            # 单个源失败不影响整体
            print(f"从源 {source.name} 爬取失败: {str(e)}")
            continue
    
    fetch_time = time.time() - start_time
    
    return FetchResponse(
        article_ids=article_ids,
        count=len(article_ids),
        sources_used=source_names,
        fetch_time_seconds=fetch_time
    )


@router.get("/sources", response_model=List[str])
async def get_available_sources(
    industry: IndustryCategory,
    db: Database = Depends(get_db)
):
    """
    获取指定行业的可用信息源列表
    """
    sources = await db.get_sources(industry=industry, enabled_only=True)
    return [s.name for s in sources]
