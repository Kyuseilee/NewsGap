#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单修复策略：
1. 启用"得到课程"
2. 删除所有无法访问的源（因为localhost:1200未运行）
"""

import asyncio
from storage.database import Database


async def main():
    db = Database()
    await db.initialize()
    
    all_sources = await db.get_sources(enabled_only=False)
    disabled_sources = [s for s in all_sources if not s.enabled]
    
    print(f"找到 {len(disabled_sources)} 个禁用的源\n")
    
    enabled = 0
    deleted = 0
    
    for source in disabled_sources:
        if source.name == "得到课程":
            # 启用得到课程
            source.enabled = True
            await db.save_source(source)
            print(f"✅ 已启用: {source.name}")
            enabled += 1
        elif 'localhost:1200' in source.url:
            # 删除本地RSSHub源（因为服务未运行）
            await db.delete_source(source.id)
            print(f"🗑️  已删除: {source.name} (本地RSSHub未运行)")
            deleted += 1
    
    print(f"\n完成！")
    print(f"  启用: {enabled}")
    print(f"  删除: {deleted}")
    
    # 最终统计
    final = await db.get_sources(enabled_only=False)
    final_enabled = [s for s in final if s.enabled]
    
    print(f"\n最终: {len(final)} 个源，{len(final_enabled)} 个启用")


if __name__ == "__main__":
    asyncio.run(main())
