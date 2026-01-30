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


# ==================== 金融专业源（RSSHub）====================
# 按优先级分层：Layer 1（核心动态）> Layer 2（深度分析）> Layer 3（补充信号）

FINANCE_RSSHUB_SOURCES = [
    # ===== Layer 1: 核心新闻与市场动态（必订，最高权重）=====
    
    # 财联社 - 实时金融资讯（Layer 1 核心）
    Source(
        name="财联社电报",
        url="http://localhost:1200/cls/telegraph",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "全面财经快讯，包括公司/解读等分类",
            "update_freq": "实时",
            "layer": 1,
            "quality": "核心动态"
        }
    ),
    Source(
        name="财联社深度",
        url="http://localhost:1200/cls/depth",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "深度分析文章",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    
    # 金十数据 - 市场快讯（Layer 1 核心）
    Source(
        name="金十数据-重要资讯",
        url="http://localhost:1200/jin10/important",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "国内外重要市场新闻（仅重要）",
            "update_freq": "实时",
            "layer": 1,
            "quality": "核心动态"
        }
    ),
    Source(
        name="金十数据",
        url="http://localhost:1200/jin10",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用全量版，优先用重要资讯
        metadata={
            "description": "7x24小时财经快讯（全量）",
            "update_freq": "实时",
            "layer": 1,
            "quality": "核心动态"
        }
    ),
    
    # 汇通网 - 外汇市场快讯（Layer 1 核心）
    Source(
        name="汇通网7×24小时快讯",
        url="http://localhost:1200/fx678/kx",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "外汇、贵金属等全球市场快讯",
            "update_freq": "实时",
            "layer": 1,
            "quality": "核心动态"
        }
    ),
    
    # 格隆汇 - 综合市场与公司新闻（Layer 1 核心）
    Source(
        name="格隆汇实时快讯",
        url="http://localhost:1200/gelonghui/live",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "综合市场与公司新闻动态",
            "update_freq": "实时",
            "layer": 1,
            "quality": "核心动态"
        }
    ),
    
    # 财经网 - 滚动新闻（Layer 1 核心）
    Source(
        name="财经网滚动新闻",
        url="http://localhost:1200/caijing/roll",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "综合财经新闻滚动更新",
            "update_freq": "高频",
            "layer": 1,
            "quality": "核心动态"
        }
    ),
    
    # ===== Layer 2: 深度洞察与数据（重要，高价值分析）=====
    
    # 东方财富 - 研究报告（Layer 2 深度）
    Source(
        name="东方财富策略报告",
        url="http://localhost:1200/eastmoney/report/strategyreport",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "券商策略研究报告",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    Source(
        name="东方财富宏观研究",
        url="http://localhost:1200/eastmoney/report/macresearch",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "宏观经济研究报告",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    Source(
        name="东方财富行业报告",
        url="http://localhost:1200/eastmoney/report/industry",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "行业深度研究报告",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    
    # BigQuant - 专题报告（Layer 2 深度）
    Source(
        name="BigQuant专题报告",
        url="http://localhost:1200/bigquant/collections",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "数据驱动专题分析（可用于量化/趋势洞察）",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    
    # 中国货币网 - 公告/数据（Layer 2 深度）
    Source(
        name="中国货币网",
        url="http://localhost:1200/chinamoney",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "货币市场公告及行情公告",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    
    # DT财经 - 数据洞察（Layer 2 深度）
    Source(
        name="DT财经-数据洞察",
        url="http://localhost:1200/dtcj/datainsight",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "专业财经数据或洞察文章",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    Source(
        name="DT财经-数据侠",
        url="http://localhost:1200/dtcj/datahero",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "数据驱动的财经分析",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    
    # 乌拉邦 - 研究报告（Layer 2 深度）
    Source(
        name="乌拉邦-个股研报",
        url="http://localhost:1200/ulapia/reports/stock_research",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "个股深度研究报告",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    Source(
        name="乌拉邦-行业研报",
        url="http://localhost:1200/ulapia/reports/industry_research",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "行业研究报告",
            "layer": 2,
            "quality": "深度洞察"
        }
    ),
    
    # ===== Layer 3: 市场话题与细分信号（补充，情绪/趋势）=====
    
    # 雪球 - 市场情绪与话题（Layer 3 补充）
    Source(
        name="雪球今日话题",
        url="http://localhost:1200/xueqiu/today",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "热门主题与市场话题趋势",
            "layer": 3,
            "quality": "市场情绪"
        }
    ),
    Source(
        name="雪球热帖",
        url="http://localhost:1200/xueqiu/hots",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "雪球社区热门帖子",
            "layer": 3,
            "quality": "市场情绪"
        }
    ),
    
    # 淘股吧 - 社区讨论（Layer 3 补充，情绪信号）
    Source(
        name="淘股吧社区热议",
        url="http://localhost:1200/taoguba/blog/252069",  # 示例博主ID，可自定义
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，需要自定义博主ID
        metadata={
            "description": "社区投资者讨论，可作为市场情绪信号",
            "layer": 3,
            "quality": "市场情绪",
            "customizable": True
        }
    ),
    
    # 格隆汇 - 热文榜（Layer 3 补充）
    Source(
        name="格隆汇热文榜",
        url="http://localhost:1200/gelonghui/hot-article",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "每日最热投资文章",
            "layer": 3,
            "quality": "市场话题"
        }
    ),
    
    # ===== 证券交易所官方动态 =====
    
    # 北京证券交易所（Layer 2 官方）
    Source(
        name="北京证券交易所",
        url="http://localhost:1200/bse",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "北京证券交易所官方新闻/公告",
            "layer": 2,
            "quality": "官方公告"
        }
    ),
    
    # 上交所
    Source(
        name="上交所监管问询",
        url="http://localhost:1200/sse/inquire",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "上交所监管问询函",
            "layer": 2,
            "quality": "监管动态"
        }
    ),
    Source(
        name="上交所科创板",
        url="http://localhost:1200/sse/renewal",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "科创板项目动态",
            "layer": 2,
            "quality": "官方公告"
        }
    ),
    
    # 深交所
    Source(
        name="深交所创业板",
        url="http://localhost:1200/szse/projectdynamic",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "创业板项目动态",
            "layer": 2,
            "quality": "官方公告"
        }
    ),
    Source(
        name="深交所监管问询",
        url="http://localhost:1200/szse/inquire",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "深交所监管问询函",
            "layer": 2,
            "quality": "监管动态"
        }
    ),
    
    # ===== 国际财经观察（Layer 3）=====
    
    # Bloomberg（Layer 3 国际）
    Source(
        name="Bloomberg作者动态",
        url="http://localhost:1200/bloomberg/authors/ARbTQlRLRjE/matthew-s-levine",  # 示例作者
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，需要自定义作者
        metadata={
            "description": "跟踪特定彭博作者发布的财经洞察",
            "layer": 3,
            "quality": "国际视野",
            "customizable": True,
            "warning": "严格反爬"
        }
    ),
    
    # Seeking Alpha（Layer 3 国际）
    Source(
        name="Seeking Alpha-市场资讯",
        url="http://localhost:1200/seekingalpha/SPY/news",  # SPY为标普500 ETF
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "国际证券研究与公司新闻",
            "layer": 3,
            "quality": "国际视野",
            "customizable": True
        }
    ),
    
    # Finviz（Layer 3 国际）
    Source(
        name="Finviz市场新闻",
        url="http://localhost:1200/finviz",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "全球市场快讯与板块动态",
            "layer": 3,
            "quality": "国际视野"
        }
    ),
    
    # ===== 加密货币/新兴资产（单独分层）=====
    
    # 金色财经（Layer 1 加密）
    Source(
        name="金色财经-政策",
        url="http://localhost:1200/jinse/zhengce",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={
            "description": "加密货币政策动态",
            "layer": 1,
            "quality": "核心动态",
            "asset_class": "crypto"
        }
    ),
    Source(
        name="金色财经-实时",
        url="http://localhost:1200/jinse/lives",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={
            "description": "加密市场实时快讯",
            "update_freq": "实时",
            "layer": 1,
            "quality": "核心动态",
            "asset_class": "crypto"
        }
    ),
    
    # 律动 BlockBeats（Layer 1 加密）
    Source(
        name="律动快讯",
        url="http://localhost:1200/theblockbeats/newsflash",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={
            "description": "加密货币快讯",
            "layer": 1,
            "quality": "核心动态",
            "asset_class": "crypto"
        }
    ),
    Source(
        name="律动文章",
        url="http://localhost:1200/theblockbeats/article",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={
            "description": "加密货币深度报道",
            "layer": 2,
            "quality": "深度洞察",
            "asset_class": "crypto"
        }
    ),
    
    # TokenInsight（Layer 2 加密研究）
    Source(
        name="TokenInsight研究报告",
        url="http://localhost:1200/tokeninsight/report/zh",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={
            "description": "链上数据洞察/研究报告",
            "layer": 2,
            "quality": "深度洞察",
            "asset_class": "crypto"
        }
    ),
    
    # ===== 央行与监管机构 =====
    
    # 中国人民银行（Layer 2 官方）
    Source(
        name="央行工作论文",
        url="http://localhost:1200/gov/pbc/gzlw",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "央行工作论文",
            "layer": 2,
            "quality": "政策研究"
        }
    ),
    Source(
        name="央行公开市场操作",
        url="http://localhost:1200/gov/pbc/tradeAnnouncement",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={
            "description": "公开市场操作公告",
            "layer": 1,
            "quality": "政策动态"
        }
    ),
    
    # ===== 其他补充源（禁用或低频） =====
    
    # 每经网（已包含在 Layer 1，这里保留兼容）
    Source(
        name="每经网突发",
        url="http://localhost:1200/nbd",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，已有财经网滚动
        metadata={
            "description": "每日经济新闻突发",
            "layer": 1
        }
    ),
    Source(
        name="每经网原创",
        url="http://localhost:1200/nbd/daily",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,
        metadata={
            "description": "每经网精选原创内容",
            "layer": 2
        }
    ),
    
    # 证券时报
    Source(
        name="证券时报要闻",
        url="http://localhost:1200/stcn/yw",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，避免重复
        metadata={
            "description": "证券市场要闻",
            "layer": 1
        }
    ),
    
    # 智通财经
    Source(
        name="智通财经推荐",
        url="http://localhost:1200/zhitongcaijing",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，港股已有格隆汇
        metadata={
            "description": "港股美股资讯推荐",
            "layer": 1
        }
    ),
    
    # 巴伦周刊
    Source(
        name="巴伦周刊中文",
        url="http://localhost:1200/barronschina",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用
        metadata={
            "description": "巴伦周刊中文版精选",
            "layer": 3
        }
    ),
    
    # 有知有行
    Source(
        name="有知有行",
        url="http://localhost:1200/youzhiyouxing/materials",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，长期投资教育
        metadata={
            "description": "长期投资教育内容",
            "layer": 3
        }
    ),
    
    # 法布财经
    Source(
        name="法布财经快讯",
        url="http://localhost:1200/fastbull/express-news",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 默认禁用，港股已有格隆汇
        metadata={
            "description": "港美股实时快讯",
            "layer": 1
        }
    ),
    
    # AInvest
    Source(
        name="AInvest文章",
        url="http://localhost:1200/ainvest/article",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,
        metadata={
            "description": "AI投资分析文章",
            "layer": 2
        }
    ),
    
    # 麦肯锡
    Source(
        name="麦肯锡中国-金融",
        url="http://localhost:1200/mckinsey/cn/financial-services",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,
        metadata={
            "description": "麦肯锡金融行业洞察",
            "layer": 2
        }
    ),
    
    # Unusual Whales
    Source(
        name="Unusual Whales",
        url="http://localhost:1200/unusualwhales/news",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,
        metadata={
            "description": "美股期权异动监测",
            "layer": 3
        }
    ),
    
    # Followin
    Source(
        name="Followin新闻",
        url="http://localhost:1200/followin/news/en",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=False,
        metadata={
            "description": "Web3英文新闻聚合",
            "layer": 1,
            "asset_class": "crypto"
        }
    ),
    
    # Paradigm
    Source(
        name="Paradigm研究",
        url="http://localhost:1200/paradigm/writing",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=False,
        metadata={
            "description": "Paradigm投资研究",
            "layer": 2,
            "asset_class": "crypto"
        }
    ),
]


# ==================== RSSHub稳定源（次优）====================

RSSHUB_STABLE_SOURCES = [
    # 证券时报
    Source(
        name="证券时报要闻",
        url="http://localhost:1200/stcn/yw",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "证券市场要闻"}
    ),
    
    # 智通财经 - 港股美股
    Source(
        name="智通财经推荐",
        url="http://localhost:1200/zhitongcaijing",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "港股美股资讯推荐"}
    ),
    
    # 巴伦周刊中文版
    Source(
        name="巴伦周刊中文",
        url="http://localhost:1200/barronschina",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "巴伦周刊中文版精选"}
    ),
    
    # 有知有行 - 投资教育
    Source(
        name="有知有行",
        url="http://localhost:1200/youzhiyouxing/materials",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "长期投资教育内容"}
    ),
    
    # === 中国证券交易所 ===
    
    # 上交所
    Source(
        name="上交所监管问询",
        url="http://localhost:1200/sse/inquire",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "上交所监管问询函"}
    ),
    Source(
        name="上交所科创板",
        url="http://localhost:1200/sse/renewal",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "科创板项目动态"}
    ),
    
    # 深交所
    Source(
        name="深交所创业板",
        url="http://localhost:1200/szse/projectdynamic",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "创业板项目动态"}
    ),
    Source(
        name="深交所监管问询",
        url="http://localhost:1200/szse/inquire",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "深交所监管问询函"}
    ),
    
    # 北交所
    Source(
        name="北京证券交易所",
        url="http://localhost:1200/bse",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "北交所公告"}
    ),
    
    # === 国际金融源 ===
    
    # Seeking Alpha - 美股分析
    Source(
        name="Seeking Alpha - 特斯拉",
        url="http://localhost:1200/seekingalpha/TSLA/analysis",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=False,  # 示例，默认禁用，用户可自定义股票
        metadata={"description": "特斯拉深度分析", "customizable": True}
    ),
    
    # Finviz - 美股新闻
    Source(
        name="Finviz 市场新闻",
        url="http://localhost:1200/finviz",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "美股市场新闻聚合"}
    ),
    
    # McKinsey - 咨询报告
    Source(
        name="麦肯锡中国-金融",
        url="http://localhost:1200/mckinsey/cn/financial-services",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "麦肯锡金融行业洞察"}
    ),
    
    # Unusual Whales - 市场异动
    Source(
        name="Unusual Whales",
        url="http://localhost:1200/unusualwhales/news",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "美股期权异动监测"}
    ),
    
    # === 加密货币/Web3 金融 ===
    
    # 金色财经 - 加密货币
    Source(
        name="金色财经-政策",
        url="http://localhost:1200/jinse/zhengce",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "加密货币政策动态"}
    ),
    Source(
        name="金色财经-实时",
        url="http://localhost:1200/jinse/lives",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "加密市场实时快讯"}
    ),
    
    # 律动 BlockBeats
    Source(
        name="律动快讯",
        url="http://localhost:1200/theblockbeats/newsflash",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "加密货币快讯"}
    ),
    Source(
        name="律动文章",
        url="http://localhost:1200/theblockbeats/article",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "加密货币深度文章"}
    ),
    
    # Followin - Web3社交
    Source(
        name="Followin 新闻",
        url="http://localhost:1200/followin/news/en",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "Web3英文新闻聚合"}
    ),
    
    # TokenInsight - 加密研究
    Source(
        name="TokenInsight 报告",
        url="http://localhost:1200/tokeninsight/report/zh",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "加密货币研究报告"}
    ),
    
    # Paradigm - 加密投资
    Source(
        name="Paradigm 研究",
        url="http://localhost:1200/paradigm/writing",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.CRYPTO,
        enabled=True,
        metadata={"description": "Paradigm投资研究"}
    ),
    
    # === 央行与监管机构 ===
    
    # 中国人民银行
    Source(
        name="央行工作论文",
        url="http://localhost:1200/gov/pbc/gzlw",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "央行工作论文"}
    ),
    Source(
        name="央行公开市场操作",
        url="http://localhost:1200/gov/pbc/tradeAnnouncement",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "公开市场操作公告"}
    ),
    
    # 中国货币网
    Source(
        name="中国货币网",
        url="http://localhost:1200/chinamoney",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "债券市场公告"}
    ),
    
    # === 其他专业金融数据 ===
    
    # 财经网
    Source(
        name="财经网滚动",
        url="http://localhost:1200/caijing/roll",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "财经网滚动新闻"}
    ),
    
    # 法布财经
    Source(
        name="法布财经快讯",
        url="http://localhost:1200/fastbull/express-news",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "港美股实时快讯"}
    ),
    
    # 汇通网 - 外汇
    Source(
        name="汇通网快讯",
        url="http://localhost:1200/fx678/kx",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "外汇市场24h快讯"}
    ),
    
    # DT财经 - 数据分析
    Source(
        name="DT财经-数据侠",
        url="http://localhost:1200/dtcj/datahero",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "数据驱动的财经分析"}
    ),
    
    # 乌拉邦 - 研究报告
    Source(
        name="乌拉邦-个股研报",
        url="http://localhost:1200/ulapia/reports/stock_research",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "个股深度研究报告"}
    ),
    Source(
        name="乌拉邦-行业研报",
        url="http://localhost:1200/ulapia/reports/industry_research",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "行业研究报告"}
    ),
    
    # AInvest
    Source(
        name="AInvest 文章",
        url="http://localhost:1200/ainvest/article",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "AI投资分析文章"}
    ),
    
    # BigQuant - 量化分析
    Source(
        name="BigQuant 专题",
        url="http://localhost:1200/bigquant/collections",
        source_type=SourceType.RSS,
        priority=SourcePriority.RSSHUB_STABLE,
        industry=IndustryCategory.FINANCE,
        enabled=True,
        metadata={"description": "量化投资专题"}
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
        FINANCE_RSSHUB_SOURCES +
        RSSHUB_STABLE_SOURCES +
        RSSHUB_HIGH_RISK_SOURCES
    )


def get_high_quality_sources_only():
    """仅获取高质量源（官方RSS + RSSHub稳定源 + 金融专业源）"""
    return OFFICIAL_RSS_SOURCES + FINANCE_RSSHUB_SOURCES + RSSHUB_STABLE_SOURCES


def get_finance_sources_only():
    """仅获取金融专业源"""
    return FINANCE_RSSHUB_SOURCES


def get_sources_by_category(category: str):
    """根据行业类别获取信息源
    
    Args:
        category: 行业类别（finance, tech, crypto, developer等）
    """
    all_sources = get_all_recommended_sources()
    category_map = {
        'finance': IndustryCategory.FINANCE,
        'crypto': IndustryCategory.CRYPTO,
        'tech': IndustryCategory.TECH,
        'developer': IndustryCategory.DEVELOPER,
        'news': IndustryCategory.NEWS,
        'social': IndustryCategory.SOCIAL,
    }
    
    target_category = category_map.get(category.lower())
    if not target_category:
        return []
    
    return [s for s in all_sources if s.industry == target_category]
