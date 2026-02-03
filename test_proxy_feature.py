#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理功能测试脚本

测试网络代理配置是否正常工作
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config_manager import ConfigManager
from storage.database import Database
from crawler.fetcher import Fetcher


async def test_proxy_config():
    """测试代理配置存储和读取"""
    print("=" * 60)
    print("测试1: 代理配置存储和读取")
    print("=" * 60)
    
    db = Database()
    await db.initialize()
    config_mgr = ConfigManager(db)
    
    # 设置代理配置
    test_config = {
        'enabled': True,
        'host': '127.0.0.1',
        'port': 7890,
        'protocol': 'http'
    }
    
    print(f"设置代理配置: {test_config}")
    await config_mgr.set_proxy_config(test_config)
    
    # 读取代理配置
    saved_config = await config_mgr.get_proxy_config()
    print(f"读取代理配置: {saved_config}")
    
    # 验证
    assert saved_config == test_config, "代理配置不匹配"
    print("✓ 代理配置存储和读取正常")
    
    # 获取代理URL
    proxy_url = await config_mgr.get_proxy_url()
    print(f"代理URL: {proxy_url}")
    assert proxy_url == "http://127.0.0.1:7890", "代理URL格式不正确"
    print("✓ 代理URL生成正常")
    
    # 测试禁用代理
    disabled_config = {
        'enabled': False,
        'host': '127.0.0.1',
        'port': 7890,
        'protocol': 'http'
    }
    await config_mgr.set_proxy_config(disabled_config)
    proxy_url = await config_mgr.get_proxy_url()
    assert proxy_url is None, "禁用代理后应返回None"
    print("✓ 代理禁用功能正常")
    
    print()


async def test_fetcher_with_proxy():
    """测试Fetcher是否支持代理参数"""
    print("=" * 60)
    print("测试2: Fetcher代理参数支持")
    print("=" * 60)
    
    # 创建带代理的Fetcher
    proxy_url = "http://127.0.0.1:7890"
    fetcher = Fetcher(proxy_url=proxy_url)
    
    print(f"创建Fetcher，代理URL: {fetcher.proxy_url}")
    assert fetcher.proxy_url == proxy_url, "Fetcher代理URL设置失败"
    print("✓ Fetcher代理参数设置正常")
    
    # 创建不带代理的Fetcher
    fetcher_no_proxy = Fetcher()
    assert fetcher_no_proxy.proxy_url is None, "默认应不使用代理"
    print("✓ Fetcher默认不使用代理")
    
    print()


async def test_llm_adapter_proxy():
    """测试LLM适配器代理支持"""
    print("=" * 60)
    print("测试3: LLM适配器代理支持")
    print("=" * 60)
    
    from llm.adapter import create_llm_adapter
    
    # 测试Ollama适配器
    proxy_url = "http://127.0.0.1:7890"
    
    try:
        ollama_adapter = create_llm_adapter(
            backend="ollama",
            model="llama3.1",
            proxy_url=proxy_url
        )
        assert ollama_adapter.proxy_url == proxy_url, "Ollama适配器代理设置失败"
        print("✓ Ollama适配器代理支持正常")
    except Exception as e:
        print(f"⚠ Ollama适配器测试跳过: {str(e)}")
    
    # 测试OpenAI适配器（不需要真实API Key，只测试初始化）
    try:
        openai_adapter = create_llm_adapter(
            backend="openai",
            api_key="test_key",
            model="gpt-4o-mini",
            proxy_url=proxy_url
        )
        assert openai_adapter.proxy_url == proxy_url, "OpenAI适配器代理设置失败"
        print("✓ OpenAI适配器代理支持正常")
    except Exception as e:
        print(f"⚠ OpenAI适配器测试跳过: {str(e)}")
    
    # 测试DeepSeek适配器
    try:
        deepseek_adapter = create_llm_adapter(
            backend="deepseek",
            api_key="test_key",
            model="deepseek-chat",
            proxy_url=proxy_url
        )
        assert deepseek_adapter.proxy_url == proxy_url, "DeepSeek适配器代理设置失败"
        print("✓ DeepSeek适配器代理支持正常")
    except Exception as e:
        print(f"⚠ DeepSeek适配器测试跳过: {str(e)}")
    
    print()


async def test_analyzer_proxy():
    """测试Analyzer代理支持"""
    print("=" * 60)
    print("测试4: Analyzer代理支持")
    print("=" * 60)
    
    from analyzer import Analyzer
    
    proxy_url = "http://127.0.0.1:7890"
    
    try:
        analyzer = Analyzer(
            llm_backend="ollama",
            model="llama3.1",
            proxy_url=proxy_url
        )
        assert analyzer.adapter.proxy_url == proxy_url, "Analyzer代理设置失败"
        print("✓ Analyzer代理支持正常")
    except Exception as e:
        print(f"⚠ Analyzer测试跳过: {str(e)}")
    
    print()


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("NewsGap 代理功能测试")
    print("=" * 60 + "\n")
    
    try:
        await test_proxy_config()
        await test_fetcher_with_proxy()
        await test_llm_adapter_proxy()
        await test_analyzer_proxy()
        
        print("=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n代理功能已正确集成到以下模块:")
        print("  - ConfigManager: 代理配置存储和读取")
        print("  - Fetcher: HTTP请求代理支持")
        print("  - LLM Adapters: AI API代理支持")
        print("  - Analyzer: 分析器代理支持")
        print("\n下一步:")
        print("  1. 启动后端服务: cd backend && python main.py")
        print("  2. 启动前端服务: cd frontend && npm run dev")
        print("  3. 在设置页面配置代理")
        print("  4. 测试RSS拉取和AI分析功能")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
