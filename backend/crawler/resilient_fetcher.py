#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容错的RSS抓取器

实现以下策略：
1. 请求重试机制（3次，指数退避）
2. 禁用代理（避免SSL错误）
3. 超时控制
4. 错误分类和记录
5. 熔断机制（连续失败后自动禁用）
"""

import asyncio
import feedparser
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from models import Source, SourcePriority


class ResilientFetcher:
    """容错RSS抓取器"""
    
    # 熔断阈值
    MAX_ERROR_COUNT = 5  # 连续失败5次后触发熔断
    
    # 重试配置
    MAX_RETRIES = 3
    BASE_DELAY = 1  # 基础延迟（秒）
    
    # 超时配置（按优先级）
    TIMEOUT_MAP = {
        SourcePriority.OFFICIAL_RSS: 15,
        SourcePriority.RSSHUB_STABLE: 20,
        SourcePriority.RSSHUB_HIGH_RISK: 30,
        SourcePriority.CUSTOM_CRAWLER: 30,
    }
    
    def __init__(self):
        # 禁用代理的session配置
        self.session = requests.Session()
        self.session.proxies = {
            'http': None,
            'https': None,
        }
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    async def fetch_feed(self, source: Source) -> Dict[str, Any]:
        """
        抓取RSS feed，带重试和容错
        
        Returns:
            {
                'success': bool,
                'data': feedparser.FeedParserDict or None,
                'error': str or None,
                'error_type': str or None,  # 'network', 'ssl', 'timeout', 'parse', 'unknown'
                'should_disable': bool,  # 是否应该禁用该源
            }
        """
        timeout = self.TIMEOUT_MAP.get(source.priority, 20)
        
        for attempt in range(self.MAX_RETRIES):
            try:
                # 使用asyncio.to_thread在线程池中运行阻塞操作
                result = await asyncio.to_thread(
                    self._sync_fetch,
                    source.url,
                    timeout
                )
                
                # 检查是否成功解析
                if result.bozo == 0 or len(result.entries) > 0:
                    return {
                        'success': True,
                        'data': result,
                        'error': None,
                        'error_type': None,
                        'should_disable': False,
                    }
                else:
                    # 解析错误但可能有部分数据
                    error_msg = str(result.bozo_exception) if hasattr(result, 'bozo_exception') else 'Parse error'
                    
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(self.BASE_DELAY * (2 ** attempt))
                        continue
                    
                    return {
                        'success': False,
                        'data': None,
                        'error': error_msg,
                        'error_type': 'parse',
                        'should_disable': False,
                    }
            
            except requests.exceptions.SSLError as e:
                error_msg = f"SSL Error: {str(e)}"
                error_type = 'ssl'
                
                # SSL错误通常是配置问题，不应该立即禁用源
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.BASE_DELAY * (2 ** attempt))
                    continue
                
                return {
                    'success': False,
                    'data': None,
                    'error': error_msg,
                    'error_type': error_type,
                    'should_disable': False,
                }
            
            except requests.exceptions.Timeout:
                error_msg = f"Timeout after {timeout}s"
                error_type = 'timeout'
                
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.BASE_DELAY * (2 ** attempt))
                    continue
                
                # 超时可能是网络问题，也可能是源失效
                should_disable = source.priority == SourcePriority.RSSHUB_HIGH_RISK
                
                return {
                    'success': False,
                    'data': None,
                    'error': error_msg,
                    'error_type': error_type,
                    'should_disable': should_disable,
                }
            
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection Error: {str(e)}"
                error_type = 'network'
                
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.BASE_DELAY * (2 ** attempt))
                    continue
                
                return {
                    'success': False,
                    'data': None,
                    'error': error_msg,
                    'error_type': error_type,
                    'should_disable': False,
                }
            
            except Exception as e:
                error_msg = f"Unknown Error: {str(e)}"
                error_type = 'unknown'
                
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.BASE_DELAY * (2 ** attempt))
                    continue
                
                return {
                    'success': False,
                    'data': None,
                    'error': error_msg,
                    'error_type': error_type,
                    'should_disable': False,
                }
        
        # 所有重试都失败了
        return {
            'success': False,
            'data': None,
            'error': f'All {self.MAX_RETRIES} retries failed',
            'error_type': 'retry_exhausted',
            'should_disable': source.priority == SourcePriority.RSSHUB_HIGH_RISK,
        }
    
    def _sync_fetch(self, url: str, timeout: int) -> feedparser.FeedParserDict:
        """同步抓取（在线程池中运行）"""
        # 先用requests获取，禁用代理
        response = self.session.get(
            url,
            timeout=timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # 用feedparser解析
        return feedparser.parse(response.content)
    
    def should_trigger_circuit_breaker(self, source: Source) -> bool:
        """判断是否应该触发熔断"""
        return source.error_count >= self.MAX_ERROR_COUNT
    
    async def update_source_status(self, source: Source, result: Dict[str, Any]) -> Source:
        """
        根据抓取结果更新源状态
        
        Returns:
            更新后的Source对象
        """
        if result['success']:
            # 成功：重置错误计数
            source.error_count = 0
            source.last_error = None
            source.last_fetched_at = datetime.now()
        else:
            # 失败：增加错误计数，记录错误
            source.error_count += 1
            source.last_error = f"[{result['error_type']}] {result['error']}"
            
            # 检查是否应该禁用
            if result['should_disable'] or self.should_trigger_circuit_breaker(source):
                source.enabled = False
                print(f"⚠️  源 [{source.name}] 已被自动禁用（错误次数: {source.error_count}）")
        
        return source
    
    def get_priority_order(self) -> list:
        """获取抓取优先级顺序"""
        return [
            SourcePriority.OFFICIAL_RSS,
            SourcePriority.RSSHUB_STABLE,
            SourcePriority.RSSHUB_HIGH_RISK,
            SourcePriority.CUSTOM_CRAWLER,
        ]
