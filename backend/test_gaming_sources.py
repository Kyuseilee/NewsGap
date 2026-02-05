#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试游戏类RSS源是否可访问
"""
import asyncio
import aiosqlite
from crawler.service import CrawlerService
from storage.database import Database

async def test_gaming_sources():
    """测试所有游戏类信息源"""
    db = Database()
    await db.initialize()
    
    # 获取游戏类源
    from models import IndustryCategory
    sources = await db.get_sources(
        industry=IndustryCategory.GAMING,
        enabled_only=True
    )
    
    print(f"\n找到 {len(sources)} 个游戏类信息源\n")
    print("="*80)
    
    crawler = CrawlerService()
    
    success_count = 0
    fail_count = 0
    results = []
    
    for i, source in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}] 测试: {source.name}")
        print(f"URL: {source.url}")
        print(f"类型: {source.source_type.value}")
        
        try:
            articles = await crawler.fetch(source, hours=168)  # 7天数据
            print(f"✅ 成功！获取 {len(articles)} 篇文章")
            if articles:
                print(f"   最新文章: {articles[0].title[:60]}...")
            success_count += 1
            results.append({
                'name': source.name,
                'status': '✅',
                'count': len(articles),
                'sample': articles[0].title[:60] if articles else 'N/A'
            })
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            fail_count += 1
            results.append({
                'name': source.name,
                'status': '❌',
                'error': str(e)[:60]
            })
        
        print("-"*80)
    
    # 打印汇总报告
    print("\n" + "="*80)
    print("测试汇总报告")
    print("="*80)
    print(f"总数: {len(sources)} | 成功: {success_count} | 失败: {fail_count}")
    print(f"成功率: {success_count/len(sources)*100:.1f}%\n")
    
    print("成功的源:")
    for result in results:
        if result['status'] == '✅':
            print(f"  ✅ {result['name']:30s} - {result['count']:3d}篇")
    
    if fail_count > 0:
        print("\n失败的源:")
        for result in results:
            if result['status'] == '❌':
                print(f"  ❌ {result['name']:30s} - {result['error']}")
    
    print("\n测试完成！\n")

if __name__ == "__main__":
    asyncio.run(test_gaming_sources())
