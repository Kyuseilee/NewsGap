#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查并修复重复的信息源

重复定义：相同的 URL 和行业分类
"""

import asyncio
from storage.database import Database
from collections import defaultdict


async def main():
    db = Database()
    await db.initialize()
    
    # 获取所有信息源
    all_sources = await db.get_sources(enabled_only=False)
    
    print(f"总共找到 {len(all_sources)} 个信息源")
    
    # 按 URL 和行业分组检查重复
    source_groups = defaultdict(list)
    for source in all_sources:
        key = (source.url, source.industry)
        source_groups[key].append(source)
    
    # 找出重复的源
    duplicates = {k: v for k, v in source_groups.items() if len(v) > 1}
    
    if not duplicates:
        print("✅ 没有发现重复的信息源")
        return
    
    print(f"\n⚠️  发现 {len(duplicates)} 组重复信息源：\n")
    
    for (url, industry), sources in duplicates.items():
        print(f"URL: {url}")
        print(f"行业: {industry}")
        print(f"重复数量: {len(sources)}")
        
        # 显示每个重复源的详情
        for i, source in enumerate(sources, 1):
            status = "启用" if source.enabled else "禁用"
            print(f"  {i}. [{status}] {source.name} (ID: {source.id})")
        
        # 保留策略：保留启用的源，如果都是启用或都是禁用，保留第一个
        enabled_sources = [s for s in sources if s.enabled]
        disabled_sources = [s for s in sources if not s.enabled]
        
        if enabled_sources:
            # 保留第一个启用的源
            keep_source = enabled_sources[0]
            to_delete = [s for s in sources if s.id != keep_source.id]
        else:
            # 都是禁用的，保留第一个
            keep_source = sources[0]
            to_delete = sources[1:]
        
        print(f"  → 将保留: {keep_source.name} (ID: {keep_source.id})")
        print(f"  → 将删除: {[s.name for s in to_delete]}")
        
        # 询问是否删除
        confirm = input("\n是否删除重复的源? (y/n): ")
        if confirm.lower() == 'y':
            for source in to_delete:
                success = await db.delete_source(source.id)
                if success:
                    print(f"  ✓ 已删除: {source.name}")
                else:
                    print(f"  ✗ 删除失败: {source.name}")
        
        print("-" * 60)
    
    print("\n检查完成！")


if __name__ == "__main__":
    asyncio.run(main())
