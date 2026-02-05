#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从数据库中删除不需要的游戏源
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from storage.database import Database
from models import IndustryCategory


# 要删除的源名称列表
SOURCES_TO_DELETE = [
    # Minecraft
    "Minecraft Java版更新",
    
    # indienova
    "indienova文章",
    "indienova游戏推荐",
    "indienova会员游戏库",
    
    # ファミ通
    "ファミ通Famitsu",
    
    # 明日方舟
    "明日方舟新闻",
    
    # 最终幻想
    "最终幻想XIV国服",
    
    # 王者荣耀
    "王者荣耀新闻-赛事",
    
    # 英雄联盟
    "英雄联盟台服-电竞",
]


async def delete_unwanted_sources():
    """从数据库中删除不需要的游戏源"""
    
    db = Database()
    await db.initialize()
    
    print("="*80)
    print("清理数据库中不需要的游戏源")
    print("="*80)
    
    # 获取所有gaming源
    all_gaming_sources = await db.get_sources(
        industry=IndustryCategory.GAMING,
        enabled_only=False
    )
    
    print(f"\n数据库中当前有 {len(all_gaming_sources)} 个gaming源")
    
    # 查找要删除的源（包括重复的）
    sources_to_delete = []
    seen_names = set()
    
    for source in all_gaming_sources:
        if source.name in SOURCES_TO_DELETE:
            sources_to_delete.append(source)
            if source.name in seen_names:
                print(f"  ⚠️  发现重复: {source.name} (ID: {source.id})")
            seen_names.add(source.name)
    
    print(f"\n找到 {len(sources_to_delete)} 个需要删除的源:\n")
    
    if not sources_to_delete:
        print("✅ 没有找到需要删除的源")
        return
    
    # 按名称分组显示
    from collections import defaultdict
    by_name = defaultdict(list)
    for source in sources_to_delete:
        by_name[source.name].append(source.id)
    
    for name, ids in sorted(by_name.items()):
        print(f"  - {name} ({len(ids)}个)")
        for sid in ids:
            print(f"    ID: {sid}")
    
    print("\n开始删除...")
    
    # 删除源
    deleted_count = 0
    for source in sources_to_delete:
        try:
            success = await db.delete_source(source.id)
            if success:
                print(f"  ✅ 已删除: {source.name} (ID: {source.id[:8]}...)")
                deleted_count += 1
            else:
                print(f"  ⚠️  未找到: {source.name} (ID: {source.id[:8]}...)")
        except Exception as e:
            print(f"  ❌ 删除失败 {source.name}: {str(e)}")
    
    print(f"\n删除完成: {deleted_count}/{len(sources_to_delete)}")
    
    # 验证删除结果
    remaining_sources = await db.get_sources(
        industry=IndustryCategory.GAMING,
        enabled_only=False
    )
    
    print(f"\n数据库中剩余 {len(remaining_sources)} 个gaming源")
    
    # 检查是否还有未删除的
    remaining_unwanted = [s for s in remaining_sources if s.name in SOURCES_TO_DELETE]
    if remaining_unwanted:
        print(f"\n⚠️  仍有 {len(remaining_unwanted)} 个源未删除:")
        for s in remaining_unwanted:
            print(f"  - {s.name} (ID: {s.id})")
    else:
        print("\n✅ 所有不需要的源已成功删除!")
    
    # 显示剩余的启用源（去重显示）
    enabled_sources = [s for s in remaining_sources if s.enabled]
    unique_names = sorted(set(s.name for s in enabled_sources))
    
    print(f"\n当前启用的gaming源 ({len(unique_names)}个唯一源):")
    for name in unique_names:
        print(f"  ✓ {name}")
    
    # 检查重复
    from collections import Counter
    name_counts = Counter(s.name for s in enabled_sources)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n⚠️  发现 {len(duplicates)} 个重复的源:")
        for name, count in duplicates.items():
            print(f"  - {name}: {count}次")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(delete_unwanted_sources())
