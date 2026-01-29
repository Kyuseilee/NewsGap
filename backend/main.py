"""
NewsGap FastAPI 后端主应用

提供 REST API 用于信息爬取、存储和分析
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import fetch, analyze, intelligence, articles, config
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
    """插入默认信息源"""
    from models import Source, SourceType, IndustryCategory
    
    # 检查是否已有信息源
    existing = await db.get_sources(enabled_only=False)
    if existing:
        return
    
    # 默认信息源列表
    default_sources = [
        Source(
            name="36氪",
            url="https://36kr.com/feed",
            source_type=SourceType.RSS,
            industry=IndustryCategory.TECH,
            enabled=True
        ),
        Source(
            name="少数派",
            url="https://sspai.com/feed",
            source_type=SourceType.RSS,
            industry=IndustryCategory.TECH,
            enabled=True
        ),
        Source(
            name="机器之心",
            url="https://www.jiqizhixin.com/rss",
            source_type=SourceType.RSS,
            industry=IndustryCategory.AI,
            enabled=True
        ),
    ]
    
    for source in default_sources:
        try:
            await db.save_source(source)
        except Exception as e:
            print(f"插入默认源失败: {str(e)}")


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
