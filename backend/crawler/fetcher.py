"""
HTTP 请求封装

提供统一的 HTTP 请求接口，支持超时、重试等
"""

import asyncio
import httpx
from typing import Optional, Dict
from datetime import datetime


class Fetcher:
    """HTTP 请求器"""
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: str = "NewsGap/0.1.0 (Information Intelligence Tool)"
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
    
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
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True
                ) as client:
                    response = await client.get(url, headers=default_headers)
                    response.raise_for_status()
                    return response.text, response.status_code
            
            except httpx.HTTPStatusError as e:
                # HTTP 错误（4xx, 5xx）
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    # 服务器错误，重试
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise
            
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                # 网络错误，重试
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise
        
        raise Exception(f"Failed to fetch {url} after {self.max_retries} attempts")
    
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
            follow_redirects=True
        ) as client:
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response.content, response.status_code
    
    async def check_url(self, url: str) -> bool:
        """检查 URL 是否可访问"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.head(url, follow_redirects=True)
                return response.status_code < 400
        except Exception:
            return False
