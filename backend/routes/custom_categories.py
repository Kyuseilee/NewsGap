"""
自定义分类路由

提供自定义分类的 CRUD API
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel

from models import CustomCategory, Source
from storage.database import Database

router = APIRouter(prefix="/api/custom-categories", tags=["custom-categories"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


# ============================================================================
# 请求/响应模型
# ============================================================================

class CreateCustomCategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None
    custom_prompt: str
    source_ids: List[str] = []


class UpdateCustomCategoryRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    custom_prompt: Optional[str] = None
    source_ids: Optional[List[str]] = None
    enabled: Optional[bool] = None


# ============================================================================
# API 端点
# ============================================================================

@router.get("", response_model=List[CustomCategory])
async def get_custom_categories(
    enabled_only: bool = True,
    db: Database = Depends(get_db)
):
    """获取所有自定义分类"""
    categories = await db.get_custom_categories(enabled_only=enabled_only)
    return categories


@router.get("/{category_id}", response_model=CustomCategory)
async def get_custom_category(
    category_id: str,
    db: Database = Depends(get_db)
):
    """获取单个自定义分类"""
    category = await db.get_custom_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分类 {category_id}"
        )
    
    return category


@router.post("", response_model=CustomCategory)
async def create_custom_category(
    request: CreateCustomCategoryRequest,
    db: Database = Depends(get_db)
):
    """创建新的自定义分类"""
    # 验证source_ids是否存在
    if request.source_ids:
        for source_id in request.source_ids:
            source = await db.get_source(source_id)
            if not source:
                raise HTTPException(
                    status_code=400,
                    detail=f"源 {source_id} 不存在"
                )
    
    category = CustomCategory(
        name=request.name,
        description=request.description,
        custom_prompt=request.custom_prompt,
        source_ids=request.source_ids
    )
    
    category_id = await db.save_custom_category(category)
    category.id = category_id
    
    return category


@router.put("/{category_id}", response_model=CustomCategory)
async def update_custom_category(
    category_id: str,
    request: UpdateCustomCategoryRequest,
    db: Database = Depends(get_db)
):
    """更新自定义分类"""
    # 获取现有分类
    category = await db.get_custom_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分类 {category_id}"
        )
    
    # 更新字段
    if request.name is not None:
        category.name = request.name
    if request.description is not None:
        category.description = request.description
    if request.custom_prompt is not None:
        category.custom_prompt = request.custom_prompt
    if request.source_ids is not None:
        # 验证source_ids
        for source_id in request.source_ids:
            source = await db.get_source(source_id)
            if not source:
                raise HTTPException(
                    status_code=400,
                    detail=f"源 {source_id} 不存在"
                )
        category.source_ids = request.source_ids
    if request.enabled is not None:
        category.enabled = request.enabled
    
    await db.save_custom_category(category)
    
    return category


@router.delete("/{category_id}")
async def delete_custom_category(
    category_id: str,
    db: Database = Depends(get_db)
):
    """删除自定义分类"""
    deleted = await db.delete_custom_category(category_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分类 {category_id}"
        )
    
    return {'success': True, 'message': '分类已删除'}


@router.get("/{category_id}/sources", response_model=List[Source])
async def get_category_sources(
    category_id: str,
    db: Database = Depends(get_db)
):
    """获取分类关联的所有源"""
    category = await db.get_custom_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分类 {category_id}"
        )
    
    sources = await db.get_sources_by_custom_category(category_id)
    return sources


@router.post("/{category_id}/sources/{source_id}")
async def add_source_to_category(
    category_id: str,
    source_id: str,
    db: Database = Depends(get_db)
):
    """添加源到分类"""
    category = await db.get_custom_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分类 {category_id}"
        )
    
    source = await db.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=404,
            detail=f"未找到源 {source_id}"
        )
    
    if source_id not in category.source_ids:
        category.source_ids.append(source_id)
        await db.save_custom_category(category)
    
    return {'success': True, 'message': '源已添加到分类'}


@router.delete("/{category_id}/sources/{source_id}")
async def remove_source_from_category(
    category_id: str,
    source_id: str,
    db: Database = Depends(get_db)
):
    """从分类中移除源"""
    category = await db.get_custom_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"未找到分类 {category_id}"
        )
    
    if source_id in category.source_ids:
        category.source_ids.remove(source_id)
        await db.save_custom_category(category)
    
    return {'success': True, 'message': '源已从分类中移除'}
