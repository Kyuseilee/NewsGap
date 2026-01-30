"""
配置管理模块

处理应用配置的存储和读取
"""

import json
from typing import Optional, Dict
from storage.database import Database


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
