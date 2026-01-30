#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复禁用的信息源

策略：
1. 启用所有可访问的源
2. 对于返回503的源，尝试替换为公共RSSHub实例
3. 删除无法修复的源
"""

import asyncio
import urllib.request
import urllib.error
from storage.database import Database
from collections import defaultdict


# RSSHub公共实例列表
RSSHUB_INSTANCES = [
    "https://rsshub.app",
    "https://rss.shab.fun",
    "https://rsshub.rssforever.com",
]


def test_url(url: str) -> bool:
    """测试URL是否可访问"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode() == 200
    except:
        return False


def replace_rsshub_instance(url: str, new_instance: str) -> str:
    """替换RSSHub实例地址"""
    if 'localhost:1200' in url:
        return url.replace('http://localhost:1200', new_instance)
    return url


async def main():
    db = Database()
    await db.initialize()
    
    # 获取所有禁用的源
    all_sources = await db.get_sources(enabled_only=False)
    disabled_sources = [s for s in all_sources if not s.enabled]
    
    print(f"找到 {len(disabled_sources)} 个禁用的信息源\n")
    print("="*80)
    
    fixed_count = 0
    enabled_count = 0
    deleted_count = 0
    
    for source in disabled_sources:
        print(f"\n处理: {source.name}")
        print(f"  URL: {source.url}")
        print(f"  行业: {source.industry}")
        
        # 如果是localhost的RSSHub，尝试替换为公共实例
        if 'localhost:1200' in source.url:
            print("  检测到本地RSSHub地址，尝试替换为公共实例...")
            
            found_working = False
            for instance in RSSHUB_INSTANCES:
                new_url = replace_rsshub_instance(source.url, instance)
                print(f"    测试: {instance}...", end=" ")
                
                if test_url(new_url):
                    print("✅ 可用")
                    source.url = new_url
                    source.enabled = True
                    await db.save_source(source)
                    print(f"  ✅ 已更新URL并启用: {new_url}")
                    fixed_count += 1
                    found_working = True
                    break
                else:
                    print("❌ 不可用")
            
            if not found_working:
                print("  ⚠️  所有公共实例都不可用")
                # 询问是否删除
                print(f"  建议删除此源")
                deleted_count += 1
                await db.delete_source(source.id)
                print(f"  ✓ 已删除")
        
        else:
            # 非RSSHub源，直接测试
            print("  测试当前URL...", end=" ")
            if test_url(source.url):
                print("✅ 可访问")
                source.enabled = True
                await db.save_source(source)
                print(f"  ✅ 已启用")
                enabled_count += 1
            else:
                print("❌ 不可访问")
                print(f"  建议手动检查或删除")
    
    print("\n" + "="*80)
    print(f"\n✅ 修复完成！")
    print(f"  - 修复并启用（替换URL）: {fixed_count} 个")
    print(f"  - 直接启用: {enabled_count} 个")
    print(f"  - 删除: {deleted_count} 个")
    
    # 最终统计
    final_sources = await db.get_sources(enabled_only=False)
    final_enabled = [s for s in final_sources if s.enabled]
    final_disabled = [s for s in final_sources if not s.enabled]
    
    print(f"\n最终统计:")
    print(f"  总数: {len(final_sources)}")
    print(f"  启用: {len(final_enabled)}")
    print(f"  禁用: {len(final_disabled)}")
    
    if final_disabled:
        print(f"\n⚠️  仍有 {len(final_disabled)} 个禁用的源需要手动检查")


if __name__ == "__main__":
    asyncio.run(main())
