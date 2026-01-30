#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复重复的信息源

重复定义：相同的 URL 和行业分类
保留策略：保留启用的源，如果都是启用或都是禁用，保留第一个
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
    
    print(f"\n⚠️  发现 {len(duplicates)} 组重复信息源\n")
    
    total_deleted = 0
    
    for (url, industry), sources in duplicates.items():
        print(f"处理: {sources[0].name}")
        print(f"  URL: {url}")
        print(f"  行业: {industry}")
        print(f"  重复数量: {len(sources)}")
        
        # 保留策略：保留启用的源，如果都是启用或都是禁用，保留最新创建的
        enabled_sources = [s for s in sources if s.enabled]
        
        if enabled_sources:
            # 有启用的源，保留第一个启用的
            keep_source = enabled_sources[0]
            to_delete = [s for s in sources if s.id != keep_source.id]
        else:
            # 都是禁用的，保留最新创建的（假设ID越新越晚创建）
            sources_sorted = sorted(sources, key=lambda x: x.created_at or '', reverse=True)
            keep_source = sources_sorted[0]
            to_delete = sources_sorted[1:]
        
        status = "启用" if keep_source.enabled else "禁用"
        print(f"  → 保留: [{status}] {keep_source.name} (ID: {keep_source.id[:8]}...)")
        
        # 删除重复的源
        for source in to_delete:
            status = "启用" if source.enabled else "禁用"
            success = await db.delete_source(source.id)
            if success:
                print(f"  ✓ 已删除: [{status}] {source.name} (ID: {source.id[:8]}...)")
                total_deleted += 1
            else:
                print(f"  ✗ 删除失败: {source.name}")
        
        print()
    
    print(f"\n✅ 完成！共删除 {total_deleted} 个重复信息源")
    
    # 最终统计
    remaining_sources = await db.get_sources(enabled_only=False)
    print(f"剩余信息源总数: {len(remaining_sources)}")


if __name__ == "__main__":
    asyncio.run(main())
