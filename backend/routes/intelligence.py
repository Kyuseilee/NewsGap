"""
一键情报路由

处理爬取+分析的组合请求
"""

from fastapi import APIRouter, Depends, HTTPException
import time

from models import IntelligenceRequest, IntelligenceResponse
from storage.database import Database
from crawler.service import CrawlerService
from analyzer import Analyzer

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_crawler():
    """依赖注入：爬虫"""
    return CrawlerService()


@router.post("", response_model=IntelligenceResponse)
async def fetch_and_analyze(
    request: IntelligenceRequest,
    db: Database = Depends(get_db),
    crawler: CrawlerService = Depends(get_crawler)
):
    """
    一键情报
    
    先爬取，再分析，一步到位
    """
    start_time = time.time()
    
    # 第一步：爬取
    sources = await db.get_sources(
        industry=request.industry,
        enabled_only=True
    )
    
    if request.source_ids:
        sources = [s for s in sources if s.id in request.source_ids]
    
    if not sources:
        raise HTTPException(
            status_code=404,
            detail=f"未找到行业 '{request.industry}' 的可用信息源"
        )
    
    article_ids = []
    
    for source in sources:
        try:
            articles = await crawler.fetch(source, hours=request.hours)
            
            for article in articles:
                article_id = await db.save_article(article)
                article_ids.append(article_id)
            
            from datetime import datetime
            source.last_fetched_at = datetime.now()
            await db.save_source(source)
        
        except Exception as e:
            print(f"从源 {source.name} 爬取失败: {str(e)}")
            continue
    
    if not article_ids:
        raise HTTPException(
            status_code=404,
            detail="未爬取到任何文章"
        )
    
    # 第二步：分析
    articles = []
    for article_id in article_ids:
        article = await db.get_article(article_id)
        if article:
            articles.append(article)
    
    analyzer = Analyzer(
        llm_backend=request.llm_backend,
        api_key=None,
        model=None
    )
    
    try:
        from models import AnalysisType
        analysis = await analyzer.analyze(
            articles=articles,
            analysis_type=AnalysisType.COMPREHENSIVE
        )
        
        analysis_id = await db.save_analysis(analysis)
        analysis.id = analysis_id
        
        total_time = time.time() - start_time
        
        return IntelligenceResponse(
            article_ids=article_ids,
            article_count=len(article_ids),
            analysis_id=analysis_id,
            analysis=analysis,
            total_time_seconds=total_time
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )
