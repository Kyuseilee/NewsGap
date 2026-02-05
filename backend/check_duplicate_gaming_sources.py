#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查gaming部分是否有重复的源
"""
import yaml
from pathlib import Path
from collections import Counter

def check_duplicates():
    config_path = Path(__file__).parent / "config" / "sources.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 收集gaming相关的源
    gaming_sources = []
    
    # 从general分类中提取gaming源
    if 'general' in config:
        for source in config['general']:
            if source.get('industry') == 'gaming':
                gaming_sources.append(source)
    
    # 检查重复
    name_counter = Counter(s['name'] for s in gaming_sources)
    url_counter = Counter(s['url'] for s in gaming_sources)
    
    print(f"\n检查gaming部分源配置...")
    print("="*80)
    
    print(f"\n总共找到 {len(gaming_sources)} 个gaming源\n")
    
    # 检查名称重复
    duplicates_by_name = {name: count for name, count in name_counter.items() if count > 1}
    if duplicates_by_name:
        print("⚠️  发现重复的源名称:")
        for name, count in duplicates_by_name.items():
            print(f"  - {name}: {count}次")
            # 显示这些重复源的详细信息
            for source in gaming_sources:
                if source['name'] == name:
                    print(f"    URL: {source['url']}")
                    print(f"    启用: {source.get('enabled', True)}")
    else:
        print("✅ 没有重复的源名称")
    
    print()
    
    # 检查URL重复
    duplicates_by_url = {url: count for url, count in url_counter.items() if count > 1}
    if duplicates_by_url:
        print("⚠️  发现重复的源URL:")
        for url, count in duplicates_by_url.items():
            print(f"  - {url}: {count}次")
            # 显示这些重复URL的源名称
            for source in gaming_sources:
                if source['url'] == url:
                    print(f"    名称: {source['name']}")
                    print(f"    启用: {source.get('enabled', True)}")
    else:
        print("✅ 没有重复的源URL")
    
    print("\n" + "="*80)
    
    # 列出所有启用的gaming源
    enabled_sources = [s for s in gaming_sources if s.get('enabled', True)]
    print(f"\n已启用的gaming源 ({len(enabled_sources)}个):")
    for source in enabled_sources:
        print(f"  ✓ {source['name']:40s} - {source['url']}")
    
    disabled_sources = [s for s in gaming_sources if not s.get('enabled', True)]
    if disabled_sources:
        print(f"\n已禁用的gaming源 ({len(disabled_sources)}个):")
        for source in disabled_sources:
            print(f"  ✗ {source['name']:40s} - {source['url']}")
    
    return len(duplicates_by_name) == 0 and len(duplicates_by_url) == 0

if __name__ == "__main__":
    is_clean = check_duplicates()
    print("\n" + "="*80)
    if is_clean:
        print("✅ 检查完成: 没有发现重复源")
    else:
        print("⚠️  检查完成: 发现重复源，请修复")
    print("="*80 + "\n")
