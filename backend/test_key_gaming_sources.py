#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关键游戏源
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crawler.service import CrawlerService
from storage.database import Database
from models import IndustryCategory


# 优先测试的关键游戏源
KEY_SOURCES = [
    "Epic Games免费游戏",
    "Steam特惠",
    "Nintendo Direct",
    "PlayStation月度免费游戏",
    "JUMP游戏折扣-Switch",
    "JUMP游戏折扣-PS5",
    "JUMP游戏折扣-Steam",
    "游戏打折情报-Steam热门中文",
    "完美世界电竞-Dota2",
    "完美世界电竞-CS2",
    "王者荣耀新闻-赛事",
    "游研社推荐",
    "indienova文章",
    "indienova游戏推荐",
    "米游社原神官方",
    "明日方舟新闻",
    "Minecraft Java版更新",
]


async def test_key_sources():
    """测试关键游戏源"""
    db = Database()
    await db.initialize()
    
    # 获取所有游戏源
    all_sources = await db.get_sources(
        industry=IndustryCategory.GAMING,
        enabled_only=True
    )
    
    # 构建名称映射
    source_map = {s.name: s for s in all_sources}
    
    print(f"\n准备测试 {len(KEY_SOURCES)} 个关键游戏源")
    print("="*80)
    
    crawler = CrawlerService()
    
    success_count = 0
    fail_count = 0
    results = []
    
    for i, source_name in enumerate(KEY_SOURCES, 1):
        if source_name not in source_map:
            print(f"\n[{i}/{len(KEY_SOURCES)}] ⚠️  {source_name} - 未找到")
            continue
        
        source = source_map[source_name]
        print(f"\n[{i}/{len(KEY_SOURCES)}] 测试: {source.name}")
        print(f"URL: {source.url}")
        
        try:
            articles = await crawler.fetch(source, hours=168)  # 7天
            print(f"✅ 成功！获取 {len(articles)} 篇")
            if articles:
                print(f"   示例: {articles[0].title[:60]}")
            success_count += 1
            results.append({
                'name': source.name,
                'status': '✅',
                'count': len(articles),
            })
        except Exception as e:
            error_msg = str(e)
            if 'HTTP error 503' in error_msg:
                print(f"⚠️  503错误 (路由可能不稳定或需要等待)")
            elif 'Network error' in error_msg:
                print(f"⚠️  网络错误")
            else:
                print(f"❌ 失败: {error_msg[:80]}")
            fail_count += 1
            results.append({
                'name': source.name,
                'status': '❌',
                'error': error_msg[:60]
            })
        
        print("-"*80)
        
        # 避免请求过快
        await asyncio.sleep(0.5)
    
    # 汇总报告
    print("\n" + "="*80)
    print("测试汇总")
    print("="*80)
    print(f"总数: {len(KEY_SOURCES)} | 成功: {success_count} | 失败: {fail_count}")
    if success_count > 0:
        print(f"成功率: {success_count/(success_count+fail_count)*100:.1f}%\n")
    
    print("✅ 成功的源:")
    for result in results:
        if result['status'] == '✅':
            print(f"  ✅ {result['name']:35s} - {result['count']:3d}篇")
    
    if fail_count > 0:
        print("\n❌ 失败的源:")
        for result in results:
            if result['status'] == '❌':
                print(f"  ❌ {result['name']:35s}")


if __name__ == "__main__":
    asyncio.run(test_key_sources())
