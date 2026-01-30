#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将本地RSSHub源迁移到公共RSSHub实例

策略：
1. 将所有 localhost:1200 替换为 https://rsshub.app
2. 启用所有源
3. 用户如果有本地RSSHub，可以在设置中修改实例地址
"""

import asyncio
from storage.database import Database


async def main():
    db = Database()
    await db.initialize()
    
    all_sources = await db.get_sources(enabled_only=False)
    
    print(f"检查 {len(all_sources)} 个信息源...\n")
    
    localhost_sources = [s for s in all_sources if 'localhost:1200' in s.url]
    
    if not localhost_sources:
        print("✅ 没有使用本地RSSHub的源")
        return
    
    print(f"找到 {len(localhost_sources)} 个使用本地RSSHub (localhost:1200) 的源\n")
    print("将它们迁移到公共RSSHub实例 (https://rsshub.app)...\n")
    
    migrated = 0
    enabled = 0
    
    for source in localhost_sources:
        old_url = source.url
        new_url = old_url.replace('http://localhost:1200', 'https://rsshub.app')
        
        was_disabled = not source.enabled
        
        source.url = new_url
        source.enabled = True  # 启用所有源
        
        await db.save_source(source)
        
        status = " (已启用)" if was_disabled else ""
        print(f"✅ {source.name}{status}")
        print(f"   旧: {old_url}")
        print(f"   新: {new_url}\n")
        
        migrated += 1
        if was_disabled:
            enabled += 1
    
    print("="*80)
    print(f"\n✅ 迁移完成！")
    print(f"  - 迁移的源: {migrated} 个")
    print(f"  - 启用的源: {enabled} 个")
    
    # 最终统计
    final = await db.get_sources(enabled_only=False)
    final_enabled = [s for s in final if s.enabled]
    final_disabled = [s for s in final if not s.enabled]
    
    print(f"\n最终统计:")
    print(f"  总数: {len(final)}")
    print(f"  启用: {len(final_enabled)}")
    print(f"  禁用: {len(final_disabled)}")
    
    print("\n💡 提示:")
    print("  如果你有运行本地RSSHub服务，可以在设置页面修改RSSHub实例地址")
    print("  或者在数据库中批量替换URL")


if __name__ == "__main__":
    asyncio.run(main())
