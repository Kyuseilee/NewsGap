"""
分析路由

处理文章分析请求
"""

from fastapi import APIRouter, Depends, HTTPException

from models import AnalyzeRequest, AnalyzeResponse
from storage.database import Database
from analyzer import Analyzer
from config_manager import ConfigManager

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_config_manager(db: Database = Depends(get_db)):
    """依赖注入：配置管理器"""
    from config_manager import ConfigManager
    return ConfigManager(db)


@router.post("", response_model=AnalyzeResponse)
async def analyze_articles(
    request: AnalyzeRequest,
    db: Database = Depends(get_db),
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    分析文章
    
    对指定的文章进行情报分析
    """
    # 获取文章
    articles = []
    for article_id in request.article_ids:
        article = await db.get_article(article_id)
        if article:
            articles.append(article)
    
    if not articles:
        raise HTTPException(
            status_code=404,
            detail="未找到任何指定的文章"
        )
    
    # 获取 API Key（优先使用数据库中的配置）
    api_key = await config_mgr.get_api_key(request.llm_backend)
    
    # 检查是否需要 API Key
    if request.llm_backend != 'ollama' and not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"使用 {request.llm_backend.upper()} 需要先在设置页面配置 API Key"
        )
    
    # 获取代理配置
    proxy_url = await config_mgr.get_proxy_url()
    
    # 创建分析器
    analyzer = Analyzer(
        llm_backend=request.llm_backend,
        api_key=api_key,
        model=request.llm_model,  # 传递用户选择的模型
        proxy_url=proxy_url
    )
    
    # 执行分析
    try:
        analysis = await analyzer.analyze(
            articles=articles,
            analysis_type=request.analysis_type,
            custom_prompt=request.custom_prompt
        )
        
        # 保存分析结果
        analysis_id = await db.save_analysis(analysis)
        analysis.id = analysis_id
        
        return AnalyzeResponse(
            analysis_id=analysis_id,
            analysis=analysis
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


@router.post("/estimate-cost")
async def estimate_analysis_cost(
    request: AnalyzeRequest,
    db: Database = Depends(get_db),
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    估算分析成本
    
    在实际分析前估算 token 使用和成本
    """
    # 获取文章
    articles = []
    for article_id in request.article_ids:
        article = await db.get_article(article_id)
        if article:
            articles.append(article)
    
    if not articles:
        raise HTTPException(
            status_code=404,
            detail="未找到任何指定的文章"
        )
    
    # 获取 API Key
    api_key = await config_mgr.get_api_key(request.llm_backend)
    
    # 创建分析器并估算
    analyzer = Analyzer(
        llm_backend=request.llm_backend,
        api_key=api_key,
        model=request.llm_model
    )
    
    cost_estimate = analyzer.estimate_cost(articles)
    model_info = analyzer.get_model_info()
    
    return {
        **cost_estimate,
        'model_info': model_info,
        'article_count': len(articles)
    }
