"""
配置路由

处理系统配置和信息源管理
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel

from models import Source, IndustryCategory, SourceType
from storage.database import Database
from config_manager import ConfigManager
from crawler.rsshub_helper import get_rsshub_helper, RSSHubHelper

router = APIRouter(prefix="/api/config", tags=["config"])


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


async def get_config_manager(db: Database = Depends(get_db)):
    """依赖注入：配置管理器"""
    return ConfigManager(db)


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
    """删除信息源"""
    deleted = await db.delete_source(source_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"未找到信息源 {source_id}"
        )
    
    return {'success': True, 'message': '信息源已删除'}


@router.get("/llm-backends")
async def get_llm_backends():
    """获取支持的 LLM 后端列表"""
    return {
        'backends': [
            {
                'id': 'ollama',
                'name': 'Ollama (本地)',
                'requires_api_key': False,
                'cost': 0.0,
                'description': '本地运行，完全免费，需要安装 Ollama',
                'models': [
                    {'id': 'qwen2.5:7b', 'name': 'Qwen 2.5 7B'},
                    {'id': 'llama3.1:8b', 'name': 'Llama 3.1 8B'},
                    {'id': 'mistral:7b', 'name': 'Mistral 7B'},
                ]
            },
            {
                'id': 'deepseek',
                'name': 'DeepSeek',
                'requires_api_key': True,
                'cost': 0.00014,
                'description': '超低成本 API，中文效果好',
                'models': [
                    {'id': 'deepseek-chat', 'name': 'DeepSeek Chat'},
                    {'id': 'deepseek-reasoner', 'name': 'DeepSeek Reasoner'},
                ]
            },
            {
                'id': 'openai',
                'name': 'OpenAI (ChatGPT)',
                'requires_api_key': True,
                'cost': 0.00015,
                'description': '效果最佳，支持 GPT-4o-mini',
                'models': [
                    {'id': 'gpt-4o-mini', 'name': 'GPT-4o Mini'},
                    {'id': 'gpt-4o', 'name': 'GPT-4o'},
                    {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo'},
                ]
            },
            {
                'id': 'gemini',
                'name': 'Google Gemini',
                'requires_api_key': True,
                'cost': 0.0,
                'description': '免费使用（有限额），超长上下文',
                'models': [
                    {'id': 'gemini-2.5-flash', 'name': 'Gemini 2.5 Flash (推荐)'},
                    {'id': 'gemini-2.5-pro', 'name': 'Gemini 2.5 Pro'},
                    {'id': 'gemini-3-flash-preview', 'name': 'Gemini 3 Flash (预览)'},
                    {'id': 'gemini-3-pro-preview', 'name': 'Gemini 3 Pro (预览)'},
                    {'id': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash (即将弃用)'},
                ]
            }
        ]
    }


# API Key 管理
class APIKeyRequest(BaseModel):
    backend: str
    api_key: str


class APIKeyResponse(BaseModel):
    backend: str
    has_key: bool
    masked_key: Optional[str] = None


@router.get("/api-keys")
async def get_api_keys(
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """获取所有 API Key 状态（脱敏）"""
    backends = ['openai', 'deepseek', 'gemini']
    results = []
    
    for backend in backends:
        api_key = await config_mgr.get_api_key(backend)
        if api_key:
            # 脱敏处理：只显示前4和后4个字符
            masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
            results.append({
                'backend': backend,
                'has_key': True,
                'masked_key': masked
            })
        else:
            results.append({
                'backend': backend,
                'has_key': False,
                'masked_key': None
            })
    
    return {'api_keys': results}


@router.post("/api-keys")
async def set_api_key(
    request: APIKeyRequest,
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """设置 API Key"""
    if not request.api_key or len(request.api_key.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="API Key 无效"
        )
    
    await config_mgr.set_api_key(request.backend, request.api_key.strip())
    
    return {
        'success': True,
        'message': f'{request.backend.upper()} API Key 已保存',
        'backend': request.backend
    }


@router.delete("/api-keys/{backend}")
async def delete_api_key(
    backend: str,
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """删除 API Key"""
    await config_mgr.delete_api_key(backend)
    
    return {
        'success': True,
        'message': f'{backend.upper()} API Key 已删除'
    }


@router.get("/rsshub/routes")
async def get_rsshub_routes():
    """获取 RSSHub 常用路由"""
    return {
        'success': True,
        'routes': RSSHubHelper.get_available_routes(),
        'instance': get_rsshub_helper().get_instance_url()
    }


@router.get("/rsshub/instance")
async def get_rsshub_instance():
    """获取当前 RSSHub 实例地址"""
    helper = get_rsshub_helper()
    return {
        'instance': helper.get_instance_url(),
        'available_instances': RSSHubHelper.DEFAULT_INSTANCES
    }


@router.post("/rsshub/instance")
async def set_rsshub_instance(
    instance_url: str = Body(..., embed=True)
):
    """设置自定义 RSSHub 实例"""
    from crawler.rsshub_helper import set_rsshub_instance
    set_rsshub_instance(instance_url)
    
    return {
        'success': True,
        'message': f'RSSHub 实例已设置为: {instance_url}'
    }

