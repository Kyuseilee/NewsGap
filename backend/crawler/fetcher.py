"""
HTTP 请求封装

提供统一的 HTTP 请求接口,支持超时、重试等
"""

import asyncio
import httpx
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Fetcher:
    """HTTP 请求器"""
    
    def __init__(
        self,
        timeout: int = 15,  # 减少超时时间从30秒到15秒
        max_retries: int = 2,  # 减少重试次数从3到2
        user_agent: str = "NewsGap/0.1.0 (Information Intelligence Tool)",
        verify_ssl: bool = False,  # 默认不验证 SSL，避免证书问题
        rsshub_fallback_instances: Optional[List[str]] = None
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.verify_ssl = verify_ssl
        self.rsshub_fallback_instances = rsshub_fallback_instances or []
    
    def _is_rsshub_url(self, url: str) -> bool:
        """判断是否是 RSSHub URL"""
        rsshub_indicators = [
            'localhost:1200',
            '127.0.0.1:1200',
            'rsshub.app',
            'rss.shab.fun',
            'rsshub.rssforever.com'
        ]
        return any(indicator in url for indicator in rsshub_indicators)
    
    def _replace_rsshub_domain(self, url: str, new_instance: str) -> str:
        """替换 RSSHub 域名"""
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        parsed_new = urlparse(new_instance)
        
        # 构建新的URL，保留原URL的路径和查询参数
        new_url = f"{parsed_new.scheme}://{parsed_new.netloc}{parsed_url.path}"
        if parsed_url.query:
            new_url += f"?{parsed_url.query}"
        
        return new_url
    
    async def fetch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> tuple[str, int]:
        """
        获取 URL 内容，支持 RSSHub 故障转移
        
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
        
        # 如果是 RSSHub URL，尝试使用备用实例
        urls_to_try = [url]
        if self._is_rsshub_url(url) and self.rsshub_fallback_instances:
            for fallback in self.rsshub_fallback_instances:
                fallback_url = self._replace_rsshub_domain(url, fallback)
                if fallback_url != url:
                    urls_to_try.append(fallback_url)
        
        last_exception = None
        
        for url_to_try in urls_to_try:
            # 对于每个URL，只尝试1次（不重试），快速失败
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=self.verify_ssl  # 控制 SSL 验证
                ) as client:
                    response = await client.get(url_to_try, headers=default_headers)
                    response.raise_for_status()
                    
                    # 成功获取，记录日志
                    if url_to_try != url:
                        logger.info(f"Successfully fetched using fallback: {url_to_try}")
                    
                    return response.text, response.status_code
            
            except httpx.HTTPStatusError as e:
                last_exception = e
                # HTTP 错误（4xx, 5xx），直接尝试下一个实例
                logger.warning(f"HTTP error {e.response.status_code} for {url_to_try}, trying next instance if available")
                continue
            
            except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as e:
                last_exception = e
                # 网络错误，直接尝试下一个实例
                logger.warning(f"Network error for {url_to_try}: {str(e)}, trying next instance if available")
                continue
        
        # 所有URL都失败了
        error_msg = f"Failed to fetch {url} after trying {len(urls_to_try)} instance(s)"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        raise Exception(error_msg)
    
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
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            verify=self.verify_ssl
        ) as client:
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response.content, response.status_code
    
    async def check_url(self, url: str) -> bool:
        """检查 URL 是否可访问"""
        try:
            async with httpx.AsyncClient(
                timeout=10,
                verify=self.verify_ssl
            ) as client:
                response = await client.head(url, follow_redirects=True)
                return response.status_code < 400
        except Exception:
            return False
