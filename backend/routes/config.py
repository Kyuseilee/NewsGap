"""
配置路由

处理系统配置和信息源管理
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from models import Source, IndustryCategory, SourceType
from storage.database import Database

router = APIRouter(prefix="/api/config", tags=["config"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


@router.get("/sources", response_model=List[Source])
async def get_sources(
    industry: Optional[IndustryCategory] = None,
    enabled_only: bool = True,
    db: Database = Depends(get_db)
):
    """
    获取信息源列表
    """
    sources = await db.get_sources(industry=industry, enabled_only=enabled_only)
    return sources


@router.post("/sources", response_model=Source)
async def create_source(
    source: Source,
    db: Database = Depends(get_db)
):
    """
    创建新的信息源
    """
    from crawler.service import CrawlerService
    
    # 验证信息源是否可访问
    crawler = CrawlerService()
    is_valid = await crawler.validate_source(source)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="信息源验证失败，请检查 URL 是否正确"
        )
    
    source_id = await db.save_source(source)
    source.id = source_id
    
    return source


@router.put("/sources/{source_id}", response_model=Source)
async def update_source(
    source_id: str,
    source: Source,
    db: Database = Depends(get_db)
):
    """
    更新信息源
    """
    existing = await db.get_source(source_id)
    
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"未找到信息源 {source_id}"
        )
    
    source.id = source_id
    await db.save_source(source)
    
    return source


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    db: Database = Depends(get_db)
):
    """
    删除信息源（暂未实现）
    """
    # TODO: 实现删除功能
    return {'success': True, 'message': '功能开发中'}


@router.get("/llm-backends")
async def get_llm_backends():
    """
    获取支持的 LLM 后端列表
    """
    return {
        'backends': [
            {
                'id': 'ollama',
                'name': 'Ollama (本地)',
                'requires_api_key': False,
                'cost': 0.0
            },
            {
                'id': 'deepseek',
                'name': 'DeepSeek',
                'requires_api_key': True,
                'cost': 0.00014
            },
            {
                'id': 'openai',
                'name': 'OpenAI (ChatGPT)',
                'requires_api_key': True,
                'cost': 0.00015
            },
            {
                'id': 'gemini',
                'name': 'Google Gemini',
                'requires_api_key': True,
                'cost': 0.0
            }
        ]
    }
