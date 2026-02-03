"""
一键情报路由

处理爬取+分析的组合请求
"""

from fastapi import APIRouter, Depends, HTTPException
import time
import asyncio
import logging

from models import IntelligenceRequest, IntelligenceResponse
from storage.database import Database
from crawler.service import CrawlerService
from analyzer import Analyzer
from config_manager import ConfigManager

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])
logger = logging.getLogger(__name__)


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_crawler():
    """依赖注入：爬虫"""
    return CrawlerService()


async def get_config_manager(db: Database = Depends(get_db)):
    """依赖注入：配置管理器"""
    return ConfigManager(db)


@router.post("", response_model=IntelligenceResponse)
async def fetch_and_analyze(
    request: IntelligenceRequest,
    db: Database = Depends(get_db),
    crawler: CrawlerService = Depends(get_crawler),
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    一键情报
    
    先爬取，再分析，一步到位。
    支持标准行业分类或自定义分类。
    """
    start_time = time.time()
    
    # 验证：industry 和 custom_category_id 二选一
    if not request.industry and not request.custom_category_id:
        raise HTTPException(
            status_code=400,
            detail="必须指定 industry 或 custom_category_id"
        )
    
    if request.industry and request.custom_category_id:
        raise HTTPException(
            status_code=400,
            detail="industry 和 custom_category_id 不能同时指定"
        )
    
    # 获取自定义提示词（如果使用自定义分类）
    custom_prompt = None
    category_name = None
    
    if request.custom_category_id:
        category = await db.get_custom_category(request.custom_category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"未找到自定义分类 {request.custom_category_id}"
            )
        if not category.enabled:
            raise HTTPException(
                status_code=400,
                detail=f"自定义分类 '{category.name}' 已禁用"
            )
        custom_prompt = category.custom_prompt
        category_name = category.name
        
        # 获取分类关联的源
        sources = await db.get_sources_by_custom_category(request.custom_category_id)
        
        # 如果还指定了source_ids，进一步筛选
        if request.source_ids:
            sources = [s for s in sources if s.id in request.source_ids]
    else:
        # 使用标准行业分类
        sources = await db.get_sources(
            industry=request.industry,
            enabled_only=True
        )
        
        if request.source_ids:
            sources = [s for s in sources if s.id in request.source_ids]
    
    if not sources:
        detail = f"未找到自定义分类 '{category_name}' 的可用信息源" if request.custom_category_id else f"未找到行业 '{request.industry}' 的可用信息源"
        raise HTTPException(
            status_code=404,
            detail=detail
        )
    
    article_ids = []
    article_urls = set()  # 用于去重
    fetch_summary = {
        'total_sources': len(sources),
        'successful_sources': 0,
        'failed_sources': 0,
        'total_articles': 0,
        'new_articles': 0,
        'updated_articles': 0
    }
    
    logger.info(f"\n{'='*80}")
    logger.info(f"[DEBUG] 开始爬取 {request.industry} 行业")
    logger.info(f"[DEBUG] 信息源数量: {len(sources)}")
    logger.info(f"[DEBUG] 时间范围: 最近 {request.hours} 小时")
    logger.info(f"[DEBUG] 请求时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info('='*80)
    
    # 并发爬取所有源
    async def fetch_from_source(source):
        """从单个源爬取"""
        try:
            logger.info(f"\n[DEBUG] 正在爬取: {source.name}")
            logger.info(f"[DEBUG] URL: {source.url}")
            
            articles = await crawler.fetch(source, hours=request.hours)
            
            logger.info(f"[DEBUG] {source.name}: 获取到 {len(articles)} 篇文章")
            
            # 保存文章
            saved_ids = []
            for article in articles:
                # 去重：同一个 URL 在本次爬取中只处理一次
                if article.url not in article_urls:
                    article_urls.add(article.url)
                    article_id = await db.save_article(article)
                    saved_ids.append(article_id)
            
            from datetime import datetime
            source.last_fetched_at = datetime.now()
            await db.save_source(source)
            
            return {
                'success': True,
                'source_name': source.name,
                'article_ids': saved_ids,
                'article_count': len(articles)
            }
        
        except Exception as e:
            logger.error(f"[ERROR] 从源 {source.name} 爬取失败: {str(e)}")
            return {
                'success': False,
                'source_name': source.name,
                'error': str(e)
            }
    
    # 并发执行所有爬取任务
    try:
        results = await asyncio.gather(
            *[fetch_from_source(source) for source in sources],
            return_exceptions=False
        )
    except Exception as e:
        logger.error(f"批量爬取出错: {str(e)}")
        results = []
    
    # 汇总结果
    for result in results:
        if isinstance(result, dict):
            if result.get('success'):
                article_ids.extend(result.get('article_ids', []))
                fetch_summary['successful_sources'] += 1
                fetch_summary['total_articles'] += result.get('article_count', 0)
            else:
                fetch_summary['failed_sources'] += 1
    
    logger.info(f"\n{'='*80}")
    logger.info(f"[DEBUG] 爬取完成!")
    logger.info(f"[DEBUG] 成功: {fetch_summary['successful_sources']}/{fetch_summary['total_sources']} 个源")
    logger.info(f"[DEBUG] 失败: {fetch_summary['failed_sources']} 个源")
    logger.info(f"[DEBUG] 文章总数: {fetch_summary['total_articles']} 篇")
    logger.info(f"[DEBUG] 去重后: {len(article_ids)} 篇")
    logger.info(f"[DEBUG] 文章ID列表前5个: {article_ids[:5]}")
    logger.info('='*80 + '\n')
    
    if not article_ids:
        # 提供详细的错误信息
        error_details = {
            "message": "未能从任何信息源获取到文章",
            "sources_attempted": fetch_summary['total_sources'],
            "sources_failed": fetch_summary['failed_sources'],
            "suggestion": "请检查信息源配置或稍后重试"
        }
        
        if request.custom_category_id:
            error_details["category"] = category_name
        else:
            error_details["industry"] = request.industry.value if request.industry else None
        
        raise HTTPException(
            status_code=404,
            detail=error_details
        )
    
    # 第二步：分析 - 确保使用本次爬取的文章
    logger.info(f"\n{'='*80}")
    logger.info(f"[DEBUG] 开始分析")
    logger.info(f"[DEBUG] 本次爬取的文章ID数量: {len(article_ids)}")
    logger.info(f"[DEBUG] 文章ID: {article_ids}")
    logger.info('='*80)
    
    # 重新从数据库加载文章（确保获取最新内容）
    articles = []
    for article_id in article_ids:
        article = await db.get_article(article_id)
        if article:
            articles.append(article)
            logger.debug(f"[DEBUG] 加载文章: ID={article_id[:8]}..., 标题={article.title[:30]}...")
    
    logger.info(f"\n[DEBUG] 成功加载 {len(articles)} 篇文章用于分析")
    if articles:
        logger.info(f"[DEBUG] 第一篇: {articles[0].title}")
        logger.info(f"[DEBUG] 发布时间: {articles[0].published_at}")
        logger.info(f"[DEBUG] 最后一篇: {articles[-1].title}")
        logger.info(f"[DEBUG] 发布时间: {articles[-1].published_at}")
    else:
        raise HTTPException(
            status_code=500,
            detail="无法加载文章数据"
        )
    print('='*80 + '\n')
    
    # 获取 API Key
    api_key = await config_mgr.get_api_key(request.llm_backend)
    
    # 检查是否需要 API Key
    if request.llm_backend != 'ollama' and not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"使用 {request.llm_backend.upper()} 需要先在设置页面配置 API Key"
        )
    
    analyzer = Analyzer(
        llm_backend=request.llm_backend,
        api_key=api_key,
        model=request.llm_model  # 传递用户选择的模型
    )
    
    try:
        from models import AnalysisType
        analysis = await analyzer.analyze(
            articles=articles,
            analysis_type=AnalysisType.COMPREHENSIVE,
            custom_prompt=custom_prompt,  # 传递自定义提示词
            industry=None  # 自定义分类时不使用industry
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
