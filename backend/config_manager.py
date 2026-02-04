"""
配置管理模块

处理应用配置的存储和读取
"""

import json
from typing import Optional, Dict
from storage.database import Database
from utils.proxy_helper import ProxyHelper


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_llm_config(self, backend: str) -> Optional[Dict]:
        """获取 LLM 配置"""
        async with self.db._get_connection() as conn:
            cursor = await conn.execute(
                "SELECT value FROM config WHERE key = ?",
                (f"llm_{backend}_config",)
            )
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None
    
    async def set_llm_config(self, backend: str, config: Dict):
        """设置 LLM 配置"""
        async with self.db._get_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, datetime('now'))",
                (f"llm_{backend}_config", json.dumps(config))
            )
            await conn.commit()
    
    async def get_api_key(self, backend: str) -> Optional[str]:
        """获取 API Key"""
        config = await self.get_llm_config(backend)
        if config:
            return config.get('api_key')
        return None
    
    async def set_api_key(self, backend: str, api_key: str):
        """设置 API Key"""
        config = await self.get_llm_config(backend) or {}
        config['api_key'] = api_key
        await self.set_llm_config(backend, config)
    
    async def delete_api_key(self, backend: str):
        """删除 API Key"""
        config = await self.get_llm_config(backend)
        if config and 'api_key' in config:
            del config['api_key']
            await self.set_llm_config(backend, config)
    
    async def set_proxy_config(self, proxy_config: Dict):
        """设置代理配置

        Args:
            proxy_config: {
                'enabled': bool,
                'http_proxy': str,  # 'http://host:port'
                'https_proxy': str, # 'https://host:port'
                'socks5_proxy': str # 'socks5://host:port'
            }
        """
        async with self.db._get_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, datetime('now'))",
                ("proxy_config", json.dumps(proxy_config))
            )
            await conn.commit()
    
    async def get_proxy_url(self) -> Optional[str]:
        """获取代理URL（如果启用）- 为了向后兼容，返回第一个可用的代理

        Returns:
            格式: 'http://host:port' 或 'https://host:port' 或 'socks5://host:port' 或 None
        """
        config = await self.get_proxy_config()
        return ProxyHelper.get_first_available_proxy(config)

    async def get_proxy_config(self) -> Optional[Dict]:
        """获取完整的代理配置

        Returns:
            代理配置字典，包含各个协议的代理设置
        """
        async with self.db._get_connection() as conn:
            cursor = await conn.execute(
                "SELECT value FROM config WHERE key = ?",
                ("proxy_config",)
            )
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    async def get_detailed_proxy_config(self) -> Optional[Dict]:
        """获取详细代理配置，返回各协议的独立配置

        Returns:
            格式: {
                'enabled': bool,
                'http': 'http://host:port' or None,
                'https': 'https://host:port' or None,
                'socks5': 'socks5://host:port' or None
            }
        """
        config = await self.get_proxy_config()
        if config and config.get('enabled'):
            return {
                'enabled': True,
                'http': config.get('http_proxy'),
                'https': config.get('https_proxy'),
                'socks5': config.get('socks5_proxy')
            }
        return {
            'enabled': False,
            'http': None,
            'https': None,
            'socks5': None
        }
