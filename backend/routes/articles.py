"""
文章路由

处理文章查询和管理
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from models import Article, ArticleListResponse, IndustryCategory
from storage.database import Database
from storage.archive import ArchiveService

router = APIRouter(prefix="/api/articles", tags=["articles"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


@router.get("", response_model=ArticleListResponse)
async def get_articles(
    industry: Optional[IndustryCategory] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    archived: Optional[bool] = None,
    db: Database = Depends(get_db)
):
    """
    查询文章列表
    
    支持按行业、时间范围、标签过滤
    """
    articles = await db.query_articles(
        industry=industry,
        start_time=start_time,
        end_time=end_time,
        tags=tags,
        limit=limit,
        offset=offset,
        archived=archived
    )
    
    # TODO: 实现总数统计（需要额外查询）
    total = len(articles)
    
    return ArticleListResponse(
        articles=articles,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: str,
    db: Database = Depends(get_db)
):
    """
    获取单篇文章详情
    """
    article = await db.get_article(article_id)
    
    if not article:
        raise HTTPException(
            status_code=404,
            detail=f"未找到文章 {article_id}"
        )
    
    return article


@router.get("/search/{query}")
async def search_articles(
    query: str,
    limit: int = Query(50, ge=1, le=100),
    db: Database = Depends(get_db)
):
    """
    全文搜索文章
    """
    articles = await db.search_articles(query, limit)
    
    return {
        'query': query,
        'count': len(articles),
        'articles': articles
    }


@router.post("/{article_id}/archive")
async def archive_article(
    article_id: str,
    db: Database = Depends(get_db)
):
    """
    归档单篇文章
    """
    article = await db.get_article(article_id)
    
    if not article:
        raise HTTPException(
            status_code=404,
            detail=f"未找到文章 {article_id}"
        )
    
    article.archived = True
    article.archived_at = datetime.now()
    await db.save_article(article)
    
    return {'success': True, 'message': '文章已归档'}


@router.post("/export")
async def export_articles(
    article_ids: List[str] = Body(..., embed=True),
    db: Database = Depends(get_db)
):
    """
    批量导出文章为 Markdown 归档
    """
    if not article_ids:
        raise HTTPException(status_code=400, detail="请提供至少一个文章ID")
    
    try:
        # 获取文章
        articles = []
        for aid in article_ids:
            article = await db.get_article(aid)
            if article:
                articles.append(article)
        
        if not articles:
            raise HTTPException(status_code=404, detail="未找到任何文章")
        
        # 创建归档服务
        archive_service = ArchiveService()
        
        # 归档文章
        output_paths = []
        for article in articles:
            path = await archive_service.save_article(article)
            output_paths.append(str(path))
            
            # 标记为已归档
            article.archived = True
            article.archived_at = datetime.now()
            await db.save_article(article)
        
        return {
            'success': True,
            'output_path': str(Path(output_paths[0]).parent) if output_paths else "./archives",
            'count': len(articles),
            'files': output_paths
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )
