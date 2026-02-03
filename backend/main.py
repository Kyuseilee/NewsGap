# -*- coding: utf-8 -*-
"""
NewsGap FastAPI 后端主应用

提供 REST API 用于信息爬取、存储和分析
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import fetch, analyze, intelligence, articles, config, analyses, custom_categories
from storage.database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    db = Database()
    await db.initialize()
    
    # 插入一些示例信息源（如果数据库为空）
    await _insert_default_sources(db)
    
    yield
    
    # 关闭时清理（如果需要）
    pass


async def _insert_default_sources(db: Database):
    """插入默认信息源 - 从 init_rss_sources 导入完整列表"""
    from models import Source, SourceType, IndustryCategory
    
    # 检查是否已有足够的信息源
    existing = await db.get_sources(enabled_only=False)
    if len(existing) >= 40:  # 如果已有40+个源，说明已初始化
        print(f"✓ 已有 {len(existing)} 个信息源")
        return
    
    print(f"当前有 {len(existing)} 个信息源，开始自动初始化...")
    
    # 完整的 RSS 源列表
    sources = [
        # 新闻类
        Source(name="联合早报 - 中港台即时", url="https://plink.anyfeeder.com/zaobao/realtime/china", source_type=SourceType.RSS, industry=IndustryCategory.NEWS, enabled=True),
        Source(name="联合早报 - 国际即时", url="https://plink.anyfeeder.com/zaobao/realtime/world", source_type=SourceType.RSS, industry=IndustryCategory.NEWS, enabled=True),
        Source(name="南方周末 - 新闻", url="http://localhost:1200/infzm/2", source_type=SourceType.RSS, industry=IndustryCategory.NEWS, enabled=True),
        Source(name="微博热搜榜", url="http://localhost:1200/weibo/search/hot", source_type=SourceType.RSS, industry=IndustryCategory.SOCIAL, enabled=True),
        
        # 技术/产品
        Source(name="36氪", url="https://36kr.com/feed", source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
        Source(name="少数派", url="https://sspai.com/feed", source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
        Source(name="V2EX", url="https://v2ex.com/index.xml", source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
        Source(name="IT之家", url="https://www.ithome.com/rss/", source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
        Source(name="阮一峰的网络日志", url="https://www.ruanyifeng.com/blog/atom.xml", source_type=SourceType.RSS, industry=IndustryCategory.DEVELOPER, enabled=True),
        Source(name="酷壳 CoolShell", url="https://coolshell.cn/feed", source_type=SourceType.RSS, industry=IndustryCategory.DEVELOPER, enabled=True),
        Source(name="小众软件", url="https://feed.appinn.com/", source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
        Source(name="HelloGitHub 月刊", url="https://hellogithub.com/rss", source_type=SourceType.RSS, industry=IndustryCategory.DEVELOPER, enabled=True),
        
        # AI/科技
        Source(name="机器之心", url="https://www.jiqizhixin.com/rss", source_type=SourceType.RSS, industry=IndustryCategory.TECH, enabled=True),
        
        # 金融
        Source(name="华尔街日报中文网", url="https://cn.wsj.com/zh-hans/rss", source_type=SourceType.RSS, industry=IndustryCategory.FINANCE, enabled=True),
        Source(name="FT中文网", url="https://www.ftchinese.com/rss/feed", source_type=SourceType.RSS, industry=IndustryCategory.FINANCE, enabled=True),
        Source(name="第一财经", url="http://localhost:1200/yicai/brief", source_type=SourceType.RSS, industry=IndustryCategory.FINANCE, enabled=True),
        
        # 医疗健康 -> 归类到生活方式
        Source(name="丁香园", url="http://localhost:1200/dxy/vaccine/latest", source_type=SourceType.RSS, industry=IndustryCategory.LIFESTYLE, enabled=True),
        
        # 教育
        Source(name="中国日报 - 双语新闻", url="https://plink.anyfeeder.com/chinadaily/dual", source_type=SourceType.RSS, industry=IndustryCategory.EDUCATION, enabled=True),
        Source(name="ONE · 一个", url="http://localhost:1200/one", source_type=SourceType.RSS, industry=IndustryCategory.EDUCATION, enabled=True),
        
        # 社区
        Source(name="知乎每日精选", url="https://www.zhihu.com/rss", source_type=SourceType.RSS, industry=IndustryCategory.SOCIAL, enabled=True),
        Source(name="知乎热榜", url="http://localhost:1200/zhihu/hotlist", source_type=SourceType.RSS, industry=IndustryCategory.SOCIAL, enabled=True),
    ]
    
    success_count = 0
    for source in sources:
        try:
            await db.save_source(source)
            success_count += 1
        except Exception as e:
            print(f"✗ {source.name}: {str(e)}")
    
    print(f"✓ 自动初始化完成，成功添加 {success_count}/{len(sources)} 个信息源")


# 创建 FastAPI 应用
app = FastAPI(
    title="NewsGap API",
    description="信息差情报工具后端 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite 开发服务器
        "http://localhost:1420",      # Tauri 默认端口
        "tauri://localhost",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(fetch.router)
app.include_router(analyze.router)
app.include_router(intelligence.router)
app.include_router(articles.router)
app.include_router(config.router)
app.include_router(analyses.router)
app.include_router(custom_categories.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        'name': 'NewsGap API',
        'version': '0.1.0',
        'status': 'running'
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {'status': 'healthy'}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
