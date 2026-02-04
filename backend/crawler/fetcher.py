"""
HTTP 请求封装

提供统一的 HTTP 请求接口,支持超时、重试、代理等
"""

import httpx
from typing import Optional, Dict
import logging
from utils.proxy_helper import ProxyHelper

logger = logging.getLogger(__name__)


class Fetcher:
    """HTTP 请求器"""
    
    def __init__(
        self,
        timeout: int = 15,
        user_agent: str = "NewsGap/0.1.0 (Information Intelligence Tool)",
        verify_ssl: bool = False,  # 默认不验证 SSL，避免证书问题
        proxy_url: Optional[str] = None,  # 旧版代理URL，格式: 'http://host:port' 或 'https://host:port' 或 'socks5://host:port'
        proxy_config: Optional[dict] = None  # 新版代理配置，格式: {'enabled': bool, 'http': 'http://host:port', 'https': 'https://host:port', 'socks5': 'socks5://host:port'}
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self.verify_ssl = verify_ssl
        
        # 统一处理代理配置（向后兼容）
        if proxy_config is None and proxy_url is not None:
            # 将单个代理 URL 转换为配置格式
            proxy_config = ProxyHelper.convert_single_url_to_config(proxy_url)
        
        # 预先转换为 httpx 格式，避免每次请求都转换
        self._httpx_proxies = ProxyHelper.convert_to_httpx_proxies(proxy_config)
        
        if self._httpx_proxies:
            logger.info(f"Fetcher 使用代理: {self._httpx_proxies}")
    
    def _get_client_kwargs(self) -> dict:
        """获取 httpx.AsyncClient 的统一配置参数"""
        return {
            'timeout': self.timeout,
            'follow_redirects': True,
            'verify': self.verify_ssl,
            'proxies': self._httpx_proxies
        }
    
    async def fetch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> tuple[str, int]:
        """
        获取 URL 内容
        
        Returns:
            (content, status_code)
        """
        default_headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.get(url, headers=default_headers)
                response.raise_for_status()
                return response.text, response.status_code
        
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} for {url}")
            raise Exception(f"HTTP error {e.response.status_code} for {url}")
        
        except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as e:
            logger.warning(f"Network error for {url}: {str(e)}")
            raise Exception(f"Network error for {url}: {str(e)}")
    
    async def fetch_binary(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> tuple[bytes, int]:
        """获取二进制内容（如图片）"""
        default_headers = {
            'User-Agent': self.user_agent,
        }
        
        if headers:
            default_headers.update(headers)
        
        async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response.content, response.status_code
    
    async def check_url(self, url: str) -> bool:
        """检查 URL 是否可访问"""
        try:
            # 使用较短的超时时间进行检查
            client_kwargs = self._get_client_kwargs()
            client_kwargs['timeout'] = 10  # 固定 10 秒超时
            
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.head(url, follow_redirects=True)
                return response.status_code < 400
        except Exception:
            return False
