#!/usr/bin/env python3
"""
测试 Gemini 适配器的配置
验证 max_output_tokens 是否已更新
"""

import sys
sys.path.insert(0, '.')

from llm.gemini_adapter import GeminiAdapter
import os
import logging

logging.basicConfig(level=logging.INFO)

def test_gemini_config():
    """测试 Gemini 配置"""
    
    # 检查环境变量
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置，尝试从配置文件读取...")
        try:
            with open('config/api_keys.json', 'r') as f:
                import json
                keys = json.load(f)
                api_key = keys.get('gemini')
        except:
            pass
    
    if not api_key:
        print("❌ 无法获取 Gemini API Key，跳过测试")
        return
    
    print("=" * 80)
    print("Gemini 适配器配置测试")
    print("=" * 80)
    print()
    
    # 初始化适配器
    adapter = GeminiAdapter(api_key=api_key, model="gemini-2.5-flash")
    
    # 检查 generation_config
    print(f"✅ 适配器已初始化: {adapter.model}")
    print(f"✅ API Key: {api_key[:10]}...{api_key[-5:]}")
    
    if hasattr(adapter, 'client'):
        print(f"✅ Client 已创建")
        
        if hasattr(adapter.client, '_generation_config'):
            config = adapter.client._generation_config
            print(f"\n📋 Generation Config:")
            print(f"   - temperature: {config.temperature}")
            print(f"   - max_output_tokens: {config.max_output_tokens}")
            print(f"   - candidate_count: {config.candidate_count}")
            print(f"   - stop_sequences: {config.stop_sequences}")
            
            if config.max_output_tokens == 65536:
                print(f"\n✅ 配置正确！max_output_tokens = 65536")
            else:
                print(f"\n⚠️  配置可能未生效！max_output_tokens = {config.max_output_tokens} (期望: 65536)")
        else:
            print("\n⚠️  无法直接访问 generation_config")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    test_gemini_config()
