"""
配置路由

处理系统配置和信息源管理
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel
import httpx
import time
import logging

from models import Source, IndustryCategory, SourceType
from storage.database import Database
from config_manager import ConfigManager
from crawler.rsshub_helper import get_rsshub_helper, RSSHubHelper
from utils.proxy_helper import ProxyHelper

logger = logging.getLogger(__name__)

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
    db: Database = Depends(get_db),
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """
    创建新的信息源
    """
    from crawler.service import CrawlerService
    
    # 获取代理配置用于验证信息源
    proxy_config = await config_mgr.get_detailed_proxy_config()
    if proxy_config and proxy_config.get('enabled'):
        formatted_config = {
            'enabled': True,
            'http': proxy_config.get('http'),
            'https': proxy_config.get('https'),
            'socks5': proxy_config.get('socks5')
        }
        crawler = CrawlerService(proxy_config=formatted_config)
    else:
        crawler = CrawlerService()
    
    # 验证信息源是否可访问
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


# 代理配置管理
class ProxyConfigRequest(BaseModel):
    enabled: bool
    http_proxy: str = ""  # 'http://host:port'
    https_proxy: str = ""  # 'https://host:port'
    socks5_proxy: str = ""  # 'socks5://host:port'


@router.get("/proxy")
async def get_proxy_config(
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """获取代理配置"""
    config = await config_mgr.get_detailed_proxy_config()
    return config


@router.post("/proxy")
async def set_proxy_config(
    request: ProxyConfigRequest,
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """设置代理配置"""
    # 检查是否有任何代理配置
    if request.enabled and not (request.http_proxy or request.https_proxy or request.socks5_proxy):
        # 如果启用了代理但没有任何代理配置，则要求至少一个有效配置
        raise HTTPException(
            status_code=400,
            detail="启用代理时必须至少配置一个代理地址 (HTTP, HTTPS, 或 SOCKS5)"
        )

    proxy_config = {
        'enabled': request.enabled,
        'http_proxy': request.http_proxy,
        'https_proxy': request.https_proxy,
        'socks5_proxy': request.socks5_proxy
    }

    await config_mgr.set_proxy_config(proxy_config)

    return {
        'success': True,
        'message': '代理配置已保存',
        'config': proxy_config
    }


@router.delete("/proxy")
async def delete_proxy_config(
    config_mgr: ConfigManager = Depends(get_config_manager)
):
    """删除/禁用代理配置"""
    proxy_config = {
        'enabled': False,
        'http_proxy': '',
        'https_proxy': '',
        'socks5_proxy': ''
    }
    await config_mgr.set_proxy_config(proxy_config)

    return {
        'success': True,
        'message': '代理配置已禁用'
    }


@router.post("/proxy/test")
async def test_proxy_config(
    request: ProxyConfigRequest,
):
    """测试代理连接

    使用提供的代理配置尝试访问多个测试目标，返回连通性结果。
    支持测试尚未保存的配置（用于保存前预检）。
    """
    if not request.enabled:
        raise HTTPException(status_code=400, detail="请先启用代理再进行测试")

    if not (request.http_proxy or request.https_proxy or request.socks5_proxy):
        raise HTTPException(status_code=400, detail="请至少配置一个代理地址")

    # 构建 ProxyHelper 所需的配置格式
    proxy_config = {
        'enabled': True,
        'http': request.http_proxy or None,
        'https': request.https_proxy or None,
        'socks5': request.socks5_proxy or None,
    }
    httpx_proxies = ProxyHelper.convert_to_httpx_proxies(proxy_config)

    if not httpx_proxies:
        raise HTTPException(status_code=400, detail="代理地址格式无效，请检查")

    # 测试目标：包含国内可达和需要代理才能达的目标
    test_targets = [
        {
            'name': 'httpbin.org',
            'url': 'https://httpbin.org/ip',
            'description': '通用连通性测试',
        },
        {
            'name': 'Google',
            'url': 'https://www.google.com/generate_204',
            'description': '外网可达性测试',
        },
        {
            'name': 'GitHub',
            'url': 'https://api.github.com',
            'description': 'GitHub API 连通性',
        },
    ]

    results = []
    overall_success = False

    for target in test_targets:
        result = {
            'name': target['name'],
            'url': target['url'],
            'description': target['description'],
            'success': False,
            'latency_ms': None,
            'status_code': None,
            'error': None,
            'proxy_ip': None,
        }

        try:
            start = time.time()
            async with httpx.AsyncClient(
                proxies=httpx_proxies,
                timeout=10,
                verify=False,
                follow_redirects=True,
            ) as client:
                response = await client.get(target['url'])
                latency = (time.time() - start) * 1000

                result['success'] = response.status_code < 400
                result['latency_ms'] = round(latency)
                result['status_code'] = response.status_code

                # 尝试从 httpbin 获取出口 IP
                if target['name'] == 'httpbin.org' and response.status_code == 200:
                    try:
                        body = response.json()
                        result['proxy_ip'] = body.get('origin')
                    except Exception:
                        pass

                if result['success']:
                    overall_success = True

        except httpx.ProxyError as e:
            result['error'] = f'代理连接失败: {str(e)}'
            logger.warning(f"代理测试 ProxyError ({target['name']}): {e}")
        except httpx.ConnectError as e:
            result['error'] = f'无法连接代理服务器，请检查代理地址和端口: {str(e)}'
            logger.warning(f"代理测试 ConnectError ({target['name']}): {e}")
        except httpx.TimeoutException:
            result['error'] = '连接超时 (10秒)，代理可能不可用'
            logger.warning(f"代理测试超时 ({target['name']})")
        except Exception as e:
            result['error'] = f'测试失败: {str(e)}'
            logger.warning(f"代理测试异常 ({target['name']}): {e}")

        results.append(result)

    return {
        'success': overall_success,
        'message': '代理连接正常' if overall_success else '代理连接失败，请检查代理配置',
        'proxy_config_used': httpx_proxies,
        'results': results,
    }

