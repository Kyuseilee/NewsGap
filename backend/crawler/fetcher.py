"""
HTTP 请求封装

提供统一的 HTTP 请求接口,支持超时、重试、代理等
"""

import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class Fetcher:
    """HTTP 请求器"""
    
    def __init__(
        self,
        timeout: int = 15,
        user_agent: str = "NewsGap/0.1.0 (Information Intelligence Tool)",
        verify_ssl: bool = False,  # 默认不验证 SSL，避免证书问题
        proxy_url: Optional[str] = None,  # 旧版代理URL，格式: 'http://host:port' 或 'https://host:port' 或 'socks5://host:port'
        proxy_config: Optional[dict] = None  # 新版代理配置，格式: {'http': 'http://host:port', 'https': 'https://host:port', 'socks5': 'socks5://host:port'}
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self.verify_ssl = verify_ssl
        # For backward compatibility, if proxy_config is not provided but proxy_url is, convert it
        if proxy_config is None and proxy_url is not None:
            # Convert single proxy URL to config format (put it in the appropriate slot based on URL scheme)
            if proxy_url.startswith('http://'):
                self.proxy_config = {'http': proxy_url, 'https': None, 'socks5': None}
            elif proxy_url.startswith('https://'):
                self.proxy_config = {'http': None, 'https': proxy_url, 'socks5': None}
            elif proxy_url.startswith('socks5://'):
                self.proxy_config = {'http': None, 'https': None, 'socks5': proxy_url}
            else:
                # Default to http if no scheme specified
                self.proxy_config = {'http': proxy_url, 'https': None, 'socks5': None}
        else:
            self.proxy_config = proxy_config or {}
    
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
            # 配置代理（如果提供）
            proxies = None
            if self.proxy_config:
                proxies = {}
                # 添加各个协议的代理配置
                if 'http' in self.proxy_config and self.proxy_config['http']:
                    proxies['http://'] = self.proxy_config['http']
                if 'https' in self.proxy_config and self.proxy_config['https']:
                    proxies['https://'] = self.proxy_config['https']
                if 'socks5' in self.proxy_config and self.proxy_config['socks5']:
                    # SOCKS5代理可以同时处理HTTP和HTTPS请求
                    if 'http://' not in proxies:
                        proxies['http://'] = self.proxy_config['socks5']
                    if 'https://' not in proxies:
                        proxies['https://'] = self.proxy_config['socks5']

            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                verify=self.verify_ssl,
                proxies=proxies
            ) as client:
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
        
        # 配置代理（如果提供）
        proxies = None
        if self.proxy_config:
            proxies = {}
            # 添加各个协议的代理配置
            if 'http' in self.proxy_config and self.proxy_config['http']:
                proxies['http://'] = self.proxy_config['http']
            if 'https' in self.proxy_config and self.proxy_config['https']:
                proxies['https://'] = self.proxy_config['https']
            if 'socks5' in self.proxy_config and self.proxy_config['socks5']:
                # SOCKS5代理可以同时处理HTTP和HTTPS请求
                if 'http://' not in proxies:
                    proxies['http://'] = self.proxy_config['socks5']
                if 'https://' not in proxies:
                    proxies['https://'] = self.proxy_config['socks5']

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            verify=self.verify_ssl,
            proxies=proxies
        ) as client:
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response.content, response.status_code
    
    async def check_url(self, url: str) -> bool:
        """检查 URL 是否可访问"""
        try:
            # 配置代理（如果提供）
            proxies = None
            if self.proxy_config:
                proxies = {}
                # 添加各个协议的代理配置
                if 'http' in self.proxy_config and self.proxy_config['http']:
                    proxies['http://'] = self.proxy_config['http']
                if 'https' in self.proxy_config and self.proxy_config['https']:
                    proxies['https://'] = self.proxy_config['https']
                if 'socks5' in self.proxy_config and self.proxy_config['socks5']:
                    # SOCKS5代理可以同时处理HTTP和HTTPS请求
                    if 'http://' not in proxies:
                        proxies['http://'] = self.proxy_config['socks5']
                    if 'https://' not in proxies:
                        proxies['https://'] = self.proxy_config['socks5']

            async with httpx.AsyncClient(
                timeout=10,
                verify=self.verify_ssl,
                proxies=proxies
            ) as client:
                response = await client.head(url, follow_redirects=True)
                return response.status_code < 400
        except Exception:
            return False
