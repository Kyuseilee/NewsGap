"""
为缺少信息源的行业分类添加示例源
"""

import asyncio
from storage.database import Database
from models import Source, IndustryCategory, SourceType, SourcePriority

async def add_missing_sources():
    db = Database()
    await db.initialize()
    
    # Crypto 加密货币信息源
    crypto_sources = [
        Source(
            name="金色财经",
            url="https://rsshub.app/jinse/lives",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.CRYPTO,
            enabled=True,
            fetch_interval_hours=6
        ),
        Source(
            name="律动 BlockBeats - 快讯",
            url="https://rsshub.app/theblockbeats/newsflash",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.CRYPTO,
            enabled=True,
            fetch_interval_hours=6
        ),
        Source(
            name="CoinDesk",
            url="https://www.coindesk.com/arc/outboundfeeds/rss/",
            source_type=SourceType.RSS,
            priority=SourcePriority.OFFICIAL_RSS,
            industry=IndustryCategory.CRYPTO,
            enabled=True,
            fetch_interval_hours=12
        ),
        Source(
            name="Cointelegraph",
            url="https://cointelegraph.com/rss",
            source_type=SourceType.RSS,
            priority=SourcePriority.OFFICIAL_RSS,
            industry=IndustryCategory.CRYPTO,
            enabled=True,
            fetch_interval_hours=12
        ),
        Source(
            name="Decrypt",
            url="https://decrypt.co/feed",
            source_type=SourceType.RSS,
            priority=SourcePriority.OFFICIAL_RSS,
            industry=IndustryCategory.CRYPTO,
            enabled=True,
            fetch_interval_hours=12
        ),
    ]
    
    # Other 其他分类信息源
    other_sources = [
        Source(
            name="少数派",
            url="https://rsshub.app/sspai/series",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.OTHER,
            enabled=True,
            fetch_interval_hours=24
        ),
        Source(
            name="虎嗅网",
            url="https://rsshub.app/huxiu/article",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.OTHER,
            enabled=True,
            fetch_interval_hours=24
        ),
        Source(
            name="爱范儿",
            url="https://rsshub.app/ifanr/app",
            source_type=SourceType.RSS,
            priority=SourcePriority.RSSHUB_STABLE,
            industry=IndustryCategory.OTHER,
            enabled=True,
            fetch_interval_hours=24
        ),
    ]
    
    all_sources = crypto_sources + other_sources
    
    print(f"\n准备添加 {len(all_sources)} 个信息源...")
    print("-" * 60)
    
    for source in all_sources:
        try:
            await db.save_source(source)
            print(f"✓ 已添加: {source.name} ({source.industry.value})")
        except Exception as e:
            print(f"✗ 添加失败: {source.name} - {str(e)}")
    
    print("-" * 60)
    print("完成！\n")
    
    # 验证结果
    crypto_count = len(await db.get_sources(industry=IndustryCategory.CRYPTO))
    other_count = len(await db.get_sources(industry=IndustryCategory.OTHER))
    
    print(f"当前状态：")
    print(f"  crypto: {crypto_count} 个信息源")
    print(f"  other: {other_count} 个信息源")
    print()

if __name__ == "__main__":
    asyncio.run(add_missing_sources())
