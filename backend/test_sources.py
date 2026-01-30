#!/usr/bin/env python3
"""
测试RSS源是否可访问
"""
import asyncio
import aiosqlite
from crawler.service import CrawlerService
from storage.database import Database

async def test_sources():
    """测试所有财经类信息源"""
    db = Database()
    await db.initialize()
    
    # 获取财经类源
    from models import IndustryCategory
    sources = await db.get_sources(
        industry=IndustryCategory.FINANCE,
        enabled_only=True
    )
    
    print(f"\n找到 {len(sources)} 个财经类信息源\n")
    print("="*80)
    
    crawler = CrawlerService()
    
    for i, source in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}] 测试: {source.name}")
        print(f"URL: {source.url}")
        print(f"类型: {source.source_type.value}")
        
        try:
            articles = await crawler.fetch(source, hours=24)
            print(f"✅ 成功！获取 {len(articles)} 篇文章")
            if articles:
                print(f"   最新文章: {articles[0].title[:50]}...")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
        
        print("-"*80)
    
    print("\n测试完成！\n")

if __name__ == "__main__":
    asyncio.run(test_sources())
