"""
爬取路由

处理文章爬取请求
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import asyncio
import logging

from models import FetchRequest, FetchResponse, IndustryCategory
from storage.database import Database
from crawler.service import CrawlerService

router = APIRouter(prefix="/api/fetch", tags=["fetch"])
logger = logging.getLogger(__name__)


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_crawler(db: Database = Depends(get_db)):
    """依赖注入：爬虫（带代理配置）"""
    from config_manager import ConfigManager
    config_mgr = ConfigManager(db)
    proxy_config = await config_mgr.get_detailed_proxy_config()
    if proxy_config and proxy_config.get('enabled'):
        # Convert to the format expected by CrawlerService
        formatted_config = {
            'http': proxy_config.get('http'),
            'https': proxy_config.get('https'),
            'socks5': proxy_config.get('socks5')
        }
        return CrawlerService(proxy_config=formatted_config)
    else:
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
    
    # 并发爬取所有源
    async def fetch_from_source(source):
        """从单个源爬取"""
        try:
            logger.info(f"开始爬取: {source.name}")
            articles = await crawler.fetch(source, hours=request.hours)
            
            # 保存文章
            article_ids = []
            for article in articles:
                article_id = await db.save_article(article)
                article_ids.append(article_id)
            
            # 更新源的最后爬取时间
            from datetime import datetime
            source.last_fetched_at = datetime.now()
            await db.save_source(source)
            
            logger.info(f"✓ {source.name}: 爬取 {len(articles)} 篇文章")
            return {
                'success': True,
                'source_name': source.name,
                'article_ids': article_ids
            }
        
        except Exception as e:
            # 单个源失败不影响整体
            logger.error(f"✗ {source.name}: {str(e)}")
            return {
                'success': False,
                'source_name': source.name,
                'error': str(e)
            }
    
    # 并发执行所有爬取任务，设置超时
    try:
        results = await asyncio.gather(
            *[fetch_from_source(source) for source in sources],
            return_exceptions=False
        )
    except Exception as e:
        logger.error(f"批量爬取出错: {str(e)}")
        results = []
    
    # 汇总结果
    article_ids = []
    source_names = []
    failed_sources = []
    
    for result in results:
        if isinstance(result, dict):
            if result.get('success'):
                article_ids.extend(result.get('article_ids', []))
                source_names.append(result.get('source_name'))
            else:
                failed_sources.append({
                    'source': result.get('source_name'),
                    'error': result.get('error')
                })
    
    fetch_time = time.time() - start_time
    
    # 记录失败的源
    if failed_sources:
        logger.warning(f"失败的源 ({len(failed_sources)}): {failed_sources}")
    
    logger.info(f"爬取完成: {len(article_ids)} 篇文章, 耗时 {fetch_time:.2f}秒")
    
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
