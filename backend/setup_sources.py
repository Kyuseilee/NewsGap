#!/usr/bin/env python3
"""
NewsGap RSSHub 信息源管理

基于 RSSHub 路由配置所有信息源
官方文档: https://docs.rsshub.app/
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from storage.database import Database
from models import Source, SourceType, IndustryCategory


# 本地 RSSHub 实例
RSSHUB = "http://localhost:1200"


# RSSHub 路由配置（只保留稳定可靠的路由）
RSSHUB_ROUTES = {
    # ===== 社交媒体 =====
    "social_media": [
        ("微博热搜", f"{RSSHUB}/weibo/search/hot", IndustryCategory.SOCIAL),
        ("知乎热榜", f"{RSSHUB}/zhihu/hotlist", IndustryCategory.SOCIAL),
        ("知乎日报", f"{RSSHUB}/zhihu/daily", IndustryCategory.SOCIAL),
        ("V2EX最热", f"{RSSHUB}/v2ex/topics/hot", IndustryCategory.SOCIAL),
        ("V2EX创意", f"{RSSHUB}/v2ex/topics/creative", IndustryCategory.SOCIAL),
    ],
    
    # ===== 新闻资讯 =====
    "news": [
        ("澎湃新闻", f"{RSSHUB}/thepaper/featured", IndustryCategory.NEWS),
        ("新华社", f"{RSSHUB}/xinhuanet/news", IndustryCategory.NEWS),
        ("环球时报", f"{RSSHUB}/huanqiu", IndustryCategory.NEWS),
        ("BBC中文", f"{RSSHUB}/bbc/chinese", IndustryCategory.NEWS),
    ],
    
    # ===== 科技互联网 =====
    "tech": [
        ("36氪快讯", f"{RSSHUB}/36kr/newsflashes", IndustryCategory.TECH),
        ("IT之家", f"{RSSHUB}/ithome/ranking/24h", IndustryCategory.TECH),
        ("cnBeta", f"{RSSHUB}/cnbeta", IndustryCategory.TECH),
        ("少数派最新", f"{RSSHUB}/sspai/matrix", IndustryCategory.TECH),
        ("爱范儿", f"{RSSHUB}/ifanr", IndustryCategory.TECH),
        ("虎嗅网", f"{RSSHUB}/huxiu/article", IndustryCategory.TECH),
        ("极客公园", f"{RSSHUB}/geekpark/news", IndustryCategory.TECH),
    ],
    
    # ===== 开发者社区 =====
    "developer": [
        ("GitHub Trending", f"{RSSHUB}/github/trending/daily", IndustryCategory.DEVELOPER),
        ("GitHub Python", f"{RSSHUB}/github/trending/daily/python", IndustryCategory.DEVELOPER),
        ("Hacker News热门", f"{RSSHUB}/hackernews/best", IndustryCategory.DEVELOPER),
        ("掘金前端", f"{RSSHUB}/juejin/category/frontend", IndustryCategory.DEVELOPER),
        ("掘金后端", f"{RSSHUB}/juejin/category/backend", IndustryCategory.DEVELOPER),
        ("阮一峰周刊", f"{RSSHUB}/ruanyifeng/weekly", IndustryCategory.DEVELOPER),
        ("V2EX技术", f"{RSSHUB}/v2ex/tab/tech", IndustryCategory.DEVELOPER),
    ],
    
    # ===== 财经金融 =====
    "finance": [
        ("华尔街见闻", f"{RSSHUB}/wallstreetcn/news/global", IndustryCategory.FINANCE),
        ("第一财经", f"{RSSHUB}/yicai/brief", IndustryCategory.FINANCE),
        ("财联社", f"{RSSHUB}/cls/telegraph", IndustryCategory.FINANCE),
    ],
    
    # ===== 娱乐影视 =====
    "entertainment": [
        ("豆瓣电影热映", f"{RSSHUB}/douban/movie/playing", IndustryCategory.ENTERTAINMENT),
        ("豆瓣电影即将上映", f"{RSSHUB}/douban/movie/coming", IndustryCategory.ENTERTAINMENT),
        ("B站热门", f"{RSSHUB}/bilibili/ranking/0/3/1", IndustryCategory.ENTERTAINMENT),
        ("B站每周必看", f"{RSSHUB}/bilibili/weekly", IndustryCategory.ENTERTAINMENT),
    ],
    
    # ===== 游戏电竞 =====
    "gaming": [
        ("Steam特惠", f"{RSSHUB}/steam/search/specials=1", IndustryCategory.GAMING),
        ("TapTap热门", f"{RSSHUB}/taptap/ranking/hot", IndustryCategory.GAMING),
        ("机核", f"{RSSHUB}/gcores/category/news", IndustryCategory.GAMING),
    ],
    
    # ===== 动漫二次元 =====
    "anime": [
        ("Bangumi每日放送", f"{RSSHUB}/bangumi/calendar/today", IndustryCategory.ANIME),
        ("AcFun文章", f"{RSSHUB}/acfun/article", IndustryCategory.ANIME),
    ],
    
    # ===== 电商购物 =====
    "shopping": [
        ("什么值得买热门", f"{RSSHUB}/smzdm/ranking/pinlei/11/0", IndustryCategory.SHOPPING),
    ],
    
    # ===== 学习教育 =====
    "education": [
        ("网易公开课", f"{RSSHUB}/163/open/vip", IndustryCategory.EDUCATION),
    ],
    
    # ===== 生活方式 =====
    "lifestyle": [
        ("下厨房", f"{RSSHUB}/xiachufang/popular/recipe", IndustryCategory.LIFESTYLE),
    ],
}


async def setup_all_sources():
    """设置所有信息源"""
    db = Database()
    await db.initialize()
    
    print("="*80)
    print("NewsGap RSSHub 信息源管理")
    print("="*80)
    print(f"RSSHub 实例: {RSSHUB}")
    print()
    
    # 第1步：清理现有源
    print("[1/2] 清理现有源...")
    existing = await db.get_sources(enabled_only=False)
    for source in existing:
        source.enabled = False
        await db.save_source(source)
    print(f"✓ 已禁用 {len(existing)} 个旧源\n")
    
    # 第2步：添加 RSSHub 路由
    print("[2/2] 添加 RSSHub 路由...")
    rsshub_count = 0
    by_category = {}
    
    for category, routes in RSSHUB_ROUTES.items():
        print(f"\n{category}:")
        for name, url, industry in routes:
            try:
                source = Source(
                    name=name,
                    url=url,
                    source_type=SourceType.RSS,
                    industry=industry,
                    enabled=True
                )
                await db.save_source(source)
                print(f"  ✓ [{industry.value}] {name}")
                rsshub_count += 1
                by_category[category] = by_category.get(category, 0) + 1
            except Exception as e:
                print(f"  ✗ {name}: {e}")
    
    print(f"\n✓ RSSHub 路由: {rsshub_count} 个")
    
    # 统计
    print("\n" + "="*80)
    print("统计信息")
    print("="*80)
    print(f"RSSHub 路由: {rsshub_count} 个\n")
    
    print("按分类:")
    for category, count in by_category.items():
        print(f"  {category}: {count} 个")
    
    print("\n按行业:")
    all_sources = await db.get_sources(enabled_only=True)
    by_industry = {}
    for s in all_sources:
        ind = s.industry.value
        by_industry[ind] = by_industry.get(ind, 0) + 1
    for ind in sorted(by_industry.keys()):
        print(f"  {ind}: {by_industry[ind]} 个")
    
    print("\n" + "="*80)
    print("✅ 设置完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(setup_all_sources())
