#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除数据库中重复的gaming源，每个源只保留最新的一个
"""
import asyncio
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from storage.database import Database
from models import IndustryCategory


async def remove_duplicates():
    """删除重复的gaming源"""
    
    db = Database()
    await db.initialize()
    
    print("="*80)
    print("清理数据库中重复的gaming源")
    print("="*80)
    
    # 获取所有gaming源
    all_sources = await db.get_sources(
        industry=IndustryCategory.GAMING,
        enabled_only=False
    )
    
    print(f"\n数据库中当前有 {len(all_sources)} 个gaming源")
    
    # 按名称分组
    by_name = defaultdict(list)
    for source in all_sources:
        by_name[source.name].append(source)
    
    # 找出重复的
    duplicates = {name: sources for name, sources in by_name.items() if len(sources) > 1}
    
    if not duplicates:
        print("\n✅ 没有发现重复的源")
        return
    
    print(f"\n发现 {len(duplicates)} 个源有重复:")
    for name, sources in sorted(duplicates.items()):
        print(f"  - {name}: {len(sources)}次")
    
    print("\n开始清理重复...")
    
    deleted_count = 0
    kept_count = 0
    
    for name, sources in sorted(duplicates.items()):
        # 按ID排序，保留第一个（通常是最早创建的）
        # 或者保留enabled=True的那个
        sources_sorted = sorted(sources, key=lambda s: (not s.enabled, s.id))
        
        keep = sources_sorted[0]
        to_delete = sources_sorted[1:]
        
        print(f"\n  {name}:")
        print(f"    保留: ID={keep.id[:8]}... enabled={keep.enabled}")
        
        for source in to_delete:
            try:
                await db.delete_source(source.id)
                print(f"    删除: ID={source.id[:8]}... enabled={source.enabled}")
                deleted_count += 1
            except Exception as e:
                print(f"    ❌ 删除失败: {str(e)}")
        
        kept_count += 1
    
    print(f"\n清理完成:")
    print(f"  保留: {kept_count} 个唯一源")
    print(f"  删除: {deleted_count} 个重复源")
    
    # 验证
    remaining = await db.get_sources(
        industry=IndustryCategory.GAMING,
        enabled_only=False
    )
    
    print(f"\n数据库中剩余 {len(remaining)} 个gaming源")
    
    # 再次检查是否还有重复
    by_name_check = defaultdict(list)
    for source in remaining:
        by_name_check[source.name].append(source)
    
    still_duplicates = {name: sources for name, sources in by_name_check.items() if len(sources) > 1}
    
    if still_duplicates:
        print(f"\n⚠️  仍有 {len(still_duplicates)} 个源重复:")
        for name, sources in still_duplicates.items():
            print(f"  - {name}: {len(sources)}次")
    else:
        print("\n✅ 所有重复源已清理完成!")
    
    # 显示最终的唯一源列表
    unique_names = sorted(set(s.name for s in remaining if s.enabled))
    print(f"\n最终启用的gaming源 ({len(unique_names)}个):")
    for name in unique_names:
        print(f"  ✓ {name}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(remove_duplicates())
