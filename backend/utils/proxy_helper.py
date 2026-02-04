"""
代理配置工具类

统一处理代理配置的转换、验证和格式化
"""

import re
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class ProxyHelper:
    """代理配置助手类"""
    
    @staticmethod
    def validate_proxy_url(url: str) -> bool:
        """验证代理 URL 格式
        
        Args:
            url: 代理 URL，如 'http://127.0.0.1:7890'
        
        Returns:
            是否为有效格式
        
        Examples:
            >>> ProxyHelper.validate_proxy_url('http://127.0.0.1:7890')
            True
            >>> ProxyHelper.validate_proxy_url('socks5://proxy.example.com:1080')
            True
            >>> ProxyHelper.validate_proxy_url('invalid')
            False
        """
        if not url:
            return False
        
        # 支持 http, https, socks5 协议
        pattern = r'^(http|https|socks5)://[\w\-.]+(:\d+)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def get_first_available_proxy(proxy_config: Optional[Dict]) -> Optional[str]:
        """从代理配置中获取第一个可用的代理 URL
        
        按优先级返回: http > https > socks5
        
        Args:
            proxy_config: 代理配置字典，格式:
                {
                    'enabled': bool,
                    'http': 'http://host:port',
                    'https': 'https://host:port',
                    'socks5': 'socks5://host:port'
                }
        
        Returns:
            代理 URL 字符串，如果未启用或无可用代理则返回 None
        
        Examples:
            >>> config = {'enabled': True, 'http': 'http://proxy:7890', 'https': None}
            >>> ProxyHelper.get_first_available_proxy(config)
            'http://proxy:7890'
        """
        if not proxy_config or not proxy_config.get('enabled'):
            return None
        
        # 按优先级返回第一个可用的代理
        for key in ['http', 'https', 'socks5']:
            proxy_url = proxy_config.get(key)
            if proxy_url:
                if ProxyHelper.validate_proxy_url(proxy_url):
                    logger.debug(f"使用 {key.upper()} 代理: {proxy_url}")
                    return proxy_url
                else:
                    logger.warning(f"无效的代理 URL ({key}): {proxy_url}")
        
        return None
    
    @staticmethod
    def convert_to_httpx_proxies(proxy_config: Optional[Dict]) -> Optional[Dict[str, str]]:
        """转换为 httpx 库的代理格式
        
        Args:
            proxy_config: 代理配置字典，格式:
                {
                    'enabled': bool,
                    'http': 'http://host:port',
                    'https': 'https://host:port',
                    'socks5': 'socks5://host:port'
                }
        
        Returns:
            httpx 代理字典，格式:
                {
                    'http://': 'http://proxy:port',
                    'https://': 'https://proxy:port'
                }
            如果未启用或无可用代理则返回 None
        
        Examples:
            >>> config = {'enabled': True, 'http': 'http://proxy:7890'}
            >>> ProxyHelper.convert_to_httpx_proxies(config)
            {'http://': 'http://proxy:7890'}
        """
        if not proxy_config or not proxy_config.get('enabled'):
            return None
        
        proxies = {}
        
        # HTTP 代理
        http_proxy = proxy_config.get('http')
        if http_proxy and ProxyHelper.validate_proxy_url(http_proxy):
            proxies['http://'] = http_proxy
        
        # HTTPS 代理
        https_proxy = proxy_config.get('https')
        if https_proxy and ProxyHelper.validate_proxy_url(https_proxy):
            proxies['https://'] = https_proxy
        
        # SOCKS5 代理 (可以同时处理 HTTP 和 HTTPS)
        socks5_proxy = proxy_config.get('socks5')
        if socks5_proxy and ProxyHelper.validate_proxy_url(socks5_proxy):
            # SOCKS5 代理作为后备，如果对应协议还没有代理则使用
            if 'http://' not in proxies:
                proxies['http://'] = socks5_proxy
            if 'https://' not in proxies:
                proxies['https://'] = socks5_proxy
        
        if proxies:
            logger.debug(f"httpx 代理配置: {proxies}")
            return proxies
        
        return None
    
    @staticmethod
    def convert_single_url_to_config(proxy_url: Optional[str]) -> Optional[Dict]:
        """将单个代理 URL 转换为标准配置格式（向后兼容）
        
        Args:
            proxy_url: 代理 URL，如 'http://127.0.0.1:7890'
        
        Returns:
            标准代理配置字典
        
        Examples:
            >>> ProxyHelper.convert_single_url_to_config('http://proxy:7890')
            {'enabled': True, 'http': 'http://proxy:7890', 'https': None, 'socks5': None}
        """
        if not proxy_url:
            return None
        
        if not ProxyHelper.validate_proxy_url(proxy_url):
            logger.warning(f"无效的代理 URL: {proxy_url}")
            return None
        
        # 根据 URL 协议确定配置
        if proxy_url.startswith('http://'):
            return {
                'enabled': True,
                'http': proxy_url,
                'https': None,
                'socks5': None
            }
        elif proxy_url.startswith('https://'):
            return {
                'enabled': True,
                'http': None,
                'https': proxy_url,
                'socks5': None
            }
        elif proxy_url.startswith('socks5://'):
            return {
                'enabled': True,
                'http': None,
                'https': None,
                'socks5': proxy_url
            }
        else:
            # 默认当作 HTTP 代理
            return {
                'enabled': True,
                'http': proxy_url,
                'https': None,
                'socks5': None
            }
