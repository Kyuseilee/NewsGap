#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理数据库中所有重复的源
根据URL去重，每个URL只保留一条记录（优先保留enabled的）
"""
import asyncio
import aiosqlite
from collections import defaultdict
from pathlib import Path

DB_PATH = "data/newsgap.db"


async def remove_all_duplicates():
    """清理所有重复源"""
    
    print("="*80)
    print("开始清理数据库中的重复源...")
    print("="*80)
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # 获取所有源
        cursor = await db.execute(
            "SELECT id, name, url, enabled FROM sources ORDER BY url, enabled DESC, id"
        )
        all_sources = await cursor.fetchall()
        
        print(f"\n当前数据库总源数: {len(all_sources)}")
        
        # 按URL分组
        by_url = defaultdict(list)
        for source in all_sources:
            by_url[source['url']].append(dict(source))
        
        # 找出重复的URL
        duplicates = {url: sources for url, sources in by_url.items() if len(sources) > 1}
        
        if not duplicates:
            print("\n✅ 未发现重复源")
            return
        
        print(f"\n⚠️  发现 {len(duplicates)} 个URL存在重复")
        print(f"⚠️  共有 {sum(len(s) for s in duplicates.values())} 条重复记录")
        
        # 统计将要删除的数量
        total_to_delete = sum(len(sources) - 1 for sources in duplicates.values())
        print(f"\n将删除 {total_to_delete} 条重复记录，保留 {len(duplicates)} 条\n")
        
        deleted_count = 0
        
        # 对每个重复的URL，保留一条，删除其他
        for url, sources in sorted(duplicates.items()):
            # 排序：enabled=1的优先，然后按ID排序
            sources_sorted = sorted(sources, key=lambda s: (not s['enabled'], s['id']))
            
            # 保留第一条
            keep = sources_sorted[0]
            to_delete = sources_sorted[1:]
            
            print(f"URL: {url}")
            print(f"  ✓ 保留: {keep['name']} (ID: {keep['id'][:8]}..., Enabled: {keep['enabled']})")
            
            for source in to_delete:
                await db.execute("DELETE FROM sources WHERE id = ?", (source['id'],))
                deleted_count += 1
                print(f"  ✗ 删除: {source['name']} (ID: {source['id'][:8]}..., Enabled: {source['enabled']})")
        
        await db.commit()
        
        print("\n" + "="*80)
        print(f"✅ 清理完成！")
        print(f"   删除了 {deleted_count} 条重复记录")
        print("="*80)
        
        # 验证结果
        cursor = await db.execute("SELECT COUNT(*) FROM sources")
        final_count = (await cursor.fetchone())[0]
        print(f"\n当前数据库总源数: {final_count}")
        
        # 检查是否还有重复
        cursor = await db.execute("""
            SELECT url, COUNT(*) as count 
            FROM sources 
            GROUP BY url 
            HAVING count > 1
        """)
        remaining_duplicates = await cursor.fetchall()
        
        if remaining_duplicates:
            print(f"\n⚠️  仍有 {len(remaining_duplicates)} 个URL存在重复!")
            for row in remaining_duplicates:
                print(f"  - {row[0]}: {row[1]}次")
        else:
            print("\n✅ 所有重复已清理完毕!")


if __name__ == "__main__":
    asyncio.run(remove_all_duplicates())
