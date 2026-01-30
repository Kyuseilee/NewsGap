#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量官方RSS源列表

优先级策略：
1. OFFICIAL_RSS - 直接来自官方网站，最稳定
2. RSSHUB_STABLE - RSSHub稳定路由（国际站点）
3. RSSHUB_HIGH_RISK - RSSHub高风险路由（国内媒体）
"""

from models import Source, SourceType, SourcePriority, IndustryCategory


# ==================== 官方RSS源（最高优先级）====================

OFFICIAL_RSS_SOURCES = [
    # 科技媒体
    Source(
        name="36氪",
        url="https://36kr.com/feed",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.TECH,
        enabled=True
    ),
    Source(
        name="少数派",
        url="https://sspai.com/feed",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.TECH,
        enabled=True
    ),
    Source(
        name="IT之家",
        url="https://www.ithome.com/rss/",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.TECH,
        enabled=True
    ),
    Source(
        name="V2EX",
        url="https://v2ex.com/index.xml",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.DEVELOPER,
        enabled=True
    ),
    
    # 开发者社区
    Source(
        name="阮一峰的网络日志",
        url="https://www.ruanyifeng.com/blog/atom.xml",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.DEVELOPER,
        enabled=True
    ),
    Source(
        name="酷壳 CoolShell",
        url="https://coolshell.cn/feed",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.DEVELOPER,
        enabled=True
    ),
    Source(
        name="小众软件",
        url="https://feed.appinn.com/",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.TECH,
        enabled=True
    ),
    
    # 金融媒体
    Source(
        name="华尔街日报中文网",
        url="https://cn.wsj.com/zh-hans/rss",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.FINANCE,
        enabled=True
    ),
    Source(
        name="FT中文网",
        url="https://www.ftchinese.com/rss/feed",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.FINANCE,
        enabled=True
    ),
    
    # 社交平台
    Source(
        name="知乎每日精选",
        url="https://www.zhihu.com/rss",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.SOCIAL,
        enabled=True
    ),
    
    # BBC官方RSS（非RSSHub）
    Source(
        name="BBC中文网",
        url="https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        source_type=SourceType.RSS,
        priority=SourcePriority.OFFICIAL_RSS,
        industry=IndustryCategory.NEWS,
        enabled=True
    ),
]


# ==================== RSSHub稳定源（次优）====================

RSSHUB_STABLE_SOURCES = [
    # 国际科技媒体
    Source(
        name="GitHub Trending",
        url="https://rsshub.app/github/trending/daily",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.DEVELOPER,
        enabled=True
    ),
    Source(
        name="Hacker News",
        url="https://rsshub.app/hackernews/best",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.DEVELOPER,
        enabled=True
    ),
    
    # 社交媒体（国际）
    Source(
        name="知乎热榜",
        url="https://rsshub.app/zhihu/hotlist",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.SOCIAL,
        enabled=True
    ),
    Source(
        name="知乎日报",
        url="https://rsshub.app/zhihu/daily",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.SOCIAL,
        enabled=True
    ),
    
    # 娱乐内容
    Source(
        name="B站热门",
        url="https://rsshub.app/bilibili/ranking/0/3/1",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.ENTERTAINMENT,
        enabled=True
    ),
    Source(
        name="豆瓣电影即将上映",
        url="https://rsshub.app/douban/movie/coming",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.ENTERTAINMENT,
        enabled=True
    ),
    
    # 游戏
    Source(
        name="Steam特惠",
        url="https://rsshub.app/steam/search/specials=1",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.GAMING,
        enabled=True
    ),
]


# ==================== RSSHub高风险源（低频使用）====================
# 注意：这些源依赖RSSHub，但目标站点反爬严重，成功率低

RSSHUB_HIGH_RISK_SOURCES = [
    # 国内新闻媒体（反爬严重）
    Source(
        name="新华社",
        url="https://rsshub.app/xinhuanet/news",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_HIGH_RISK,
        industry=IndustryCategory.NEWS,
        enabled=False,  # 默认禁用
        metadata={"warning": "高风险源，反爬严重，建议使用官方渠道"}
    ),
    Source(
        name="澎湃新闻",
        url="https://rsshub.app/thepaper/featured",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_HIGH_RISK,
        industry=IndustryCategory.NEWS,
        enabled=False,
        metadata={"warning": "高风险源，建议使用搜索页爬虫"}
    ),
    Source(
        name="环球时报",
        url="https://rsshub.app/huanqiu",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_HIGH_RISK,
        industry=IndustryCategory.NEWS,
        enabled=False,
        metadata={"warning": "高风险源，IP黑名单严格"}
    ),
]


# ==================== 汇总所有源 ====================

def get_all_recommended_sources():
    """获取所有推荐的信息源"""
    return (
        OFFICIAL_RSS_SOURCES +
        RSSHUB_STABLE_SOURCES +
        RSSHUB_HIGH_RISK_SOURCES
    )


def get_high_quality_sources_only():
    """仅获取高质量源（官方RSS + RSSHub稳定源）"""
    return OFFICIAL_RSS_SOURCES + RSSHUB_STABLE_SOURCES
