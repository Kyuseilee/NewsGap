"""
将所有使用localhost:1200的RSSHub路由替换为rsshub.app公共实例
"""

import asyncio
from storage.database import Database

async def replace_localhost_sources():
    db = Database()
    await db.initialize()
    
    all_sources = await db.get_sources()
    
    print("\n🔧 替换本地RSSHub为公共实例")
    print("=" * 80)
    
    updated_count = 0
    
    for source in all_sources:
        if 'localhost:1200' in source.url or 'http://localhost:1200' in source.url:
            old_url = source.url
            new_url = source.url.replace('localhost:1200', 'rsshub.app')
            new_url = new_url.replace('http://rsshub.app', 'https://rsshub.app')
            
            source.url = new_url
            await db.save_source(source)
            
            print(f"✓ {source.name} ({source.industry.value})")
            print(f"  旧: {old_url}")
            print(f"  新: {new_url}")
            print()
            
            updated_count += 1
    
    print("=" * 80)
    print(f"完成！共更新 {updated_count} 个信息源")
    print()
    
    # 验证
    remaining = sum(1 for s in await db.get_sources() if 'localhost:1200' in s.url)
    if remaining > 0:
        print(f"⚠️  仍有 {remaining} 个源使用localhost:1200")
    else:
        print("✅ 所有源已更新为使用rsshub.app")
    print()

if __name__ == "__main__":
    asyncio.run(replace_localhost_sources())
