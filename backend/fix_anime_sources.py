"""
为anime分类添加更可靠的信息源，并禁用不可用的源
"""

import asyncio
from storage.database import Database
from models import Source, IndustryCategory, SourceType, SourcePriority

async def fix_anime_sources():
    db = Database()
    await db.initialize()
    
    # 1. 禁用当前不可用的源
    print("\n🔧 禁用不可用的源...")
    print("-" * 60)
    
    all_sources = await db.get_sources(industry=IndustryCategory.ANIME)
    for source in all_sources:
        if 'localhost:1200' in source.url:
            source.enabled = False
            await db.save_source(source)
            print(f"✗ 已禁用: {source.name}")
    
    # 2. 添加新的可靠源
    print("\n✅ 添加新的信息源...")
    print("-" * 60)
    
    new_sources = [
        Source(
            name="Bangumi 番组计划 - 动画",
            url="https://rsshub.app/bangumi/subject/anime",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.ANIME,
            enabled=True,
            fetch_interval_hours=24
        ),
        Source(
            name="萌娘百科 - 最近更新",
            url="https://rsshub.app/moegirl/latest",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.ANIME,
            enabled=True,
            fetch_interval_hours=24
        ),
        Source(
            name="Anitabi - 新番时间表",
            url="https://rsshub.app/anitabi/anime",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.ANIME,
            enabled=True,
            fetch_interval_hours=24
        ),
    ]
    
    for source in new_sources:
        try:
            await db.save_source(source)
            print(f"✓ 已添加: {source.name}")
        except Exception as e:
            print(f"✗ 添加失败: {source.name} - {str(e)}")
    
    print("-" * 60)
    
    # 3. 验证结果
    print("\n📊 当前anime分类信息源状态：")
    print("=" * 60)
    
    anime_sources = await db.get_sources(industry=IndustryCategory.ANIME)
    enabled_count = sum(1 for s in anime_sources if s.enabled)
    
    for source in anime_sources:
        status = "✓ 启用" if source.enabled else "✗ 禁用"
        print(f"{status} {source.name}")
        print(f"     {source.url}")
    
    print("=" * 60)
    print(f"总计: {len(anime_sources)} 个源，{enabled_count} 个启用")
    print()

if __name__ == "__main__":
    asyncio.run(fix_anime_sources())
