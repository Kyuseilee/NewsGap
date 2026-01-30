#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将现有源迁移到优先级系统

策略：
1. 替换所有可能的源为官方RSS
2. 为RSSHub源设置正确的优先级
3. 标记高风险源
"""

import asyncio
from storage.database import Database
from official_rss_sources import get_high_quality_sources_only
from models import SourcePriority


# URL映射：RSSHub → 官方RSS
OFFICIAL_RSS_MAPPING = {
    # 科技媒体
    "https://rsshub.app/36kr": "https://36kr.com/feed",
    "https://rsshub.app/sspai": "https://sspai.com/feed",
    "https://rsshub.app/ithome": "https://www.ithome.com/rss/",
    
    # BBC
    "https://rsshub.app/bbc/chinese": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
}


# 高风险RSSHub路由（国内媒体）
HIGH_RISK_PATTERNS = [
    'xinhuanet',  # 新华社
    'thepaper',   # 澎湃
    'huanqiu',    # 环球
    'cctv',       # 央视
    'nytimes',    # 纽约时报
    'caixin',     # 财新
]


async def main():
    db = Database()
    await db.initialize()
    
    print("=" * 80)
    print("开始迁移到优先级系统...")
    print("=" * 80)
    
    # 1. 获取所有现有源
    existing = await db.get_sources(enabled_only=False)
    print(f"\n当前有 {len(existing)} 个信息源")
    
    # 2. 添加高质量官方RSS源
    print("\n添加高质量官方RSS源...")
    recommended = get_high_quality_sources_only()
    
    added = 0
    for source in recommended:
        # 检查是否已存在
        exists = any(s.url == source.url for s in existing)
        if not exists:
            await db.save_source(source)
            print(f"  ✅ 添加: {source.name} [{source.priority}]")
            added += 1
    
    print(f"\n添加了 {added} 个新源")
    
    # 3. 更新现有源的优先级
    print("\n更新现有源优先级...")
    
    updated = 0
    disabled = 0
    
    for source in existing:
        modified = False
        
        # 检查是否可以替换为官方RSS
        for rsshub_pattern, official_url in OFFICIAL_RSS_MAPPING.items():
            if rsshub_pattern in source.url:
                print(f"  🔄 替换: {source.name}")
                print(f"     旧: {source.url}")
                print(f"     新: {official_url}")
                source.url = official_url
                source.priority = SourcePriority.OFFICIAL_RSS
                modified = True
                break
        
        # 检查是否是高风险源
        if not modified:
            is_high_risk = any(pattern in source.url for pattern in HIGH_RISK_PATTERNS)
            
            if is_high_risk:
                source.priority = SourcePriority.RSSHUB_HIGH_RISK
                source.enabled = False  # 禁用高风险源
                print(f"  ⚠️  高风险源已禁用: {source.name}")
                disabled += 1
                modified = True
            elif 'rsshub.app' in source.url or 'localhost:1200' in source.url:
                # 其他RSSHub源标记为稳定
                source.priority = SourcePriority.RSSHUB_STABLE
                modified = True
            else:
                # 直接URL，标记为官方RSS
                source.priority = SourcePriority.OFFICIAL_RSS
                modified = True
        
        if modified:
            await db.save_source(source)
            updated += 1
    
    print(f"\n更新了 {updated} 个现有源")
    print(f"禁用了 {disabled} 个高风险源")
    
    # 4. 最终统计
    final = await db.get_sources(enabled_only=False)
    final_enabled = [s for s in final if s.enabled]
    
    # 按优先级统计
    by_priority = {}
    for source in final:
        priority = source.priority if hasattr(source, 'priority') else 'unknown'
        if priority not in by_priority:
            by_priority[priority] = {'total': 0, 'enabled': 0}
        by_priority[priority]['total'] += 1
        if source.enabled:
            by_priority[priority]['enabled'] += 1
    
    print("\n" + "=" * 80)
    print("迁移完成！")
    print("=" * 80)
    print(f"\n总计: {len(final)} 个源")
    print(f"启用: {len(final_enabled)} 个")
    print(f"禁用: {len(final) - len(final_enabled)} 个")
    
    print("\n按优先级分布:")
    for priority, stats in sorted(by_priority.items()):
        print(f"  {priority:20} {stats['total']:2} 个 (启用 {stats['enabled']})")
    
    print("\n💡 建议:")
    print("  - 官方RSS源最稳定，优先使用")
    print("  - RSSHub稳定源可正常使用")
    print("  - 高风险源已禁用，如需使用请配置本地RSSHub")


if __name__ == "__main__":
    asyncio.run(main())
