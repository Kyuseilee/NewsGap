# -*- coding: utf-8 -*-
"""
NewsGap FastAPI 后端主应用

提供 REST API 用于信息爬取、存储和分析
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import fetch, analyze, intelligence, articles, config, analyses, custom_categories, export
from storage.database import Database


# 配置日志格式（添加时间戳）
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log(message: str):
    """带时间戳的日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


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
    """插入默认信息源 - 从 YAML 配置文件加载"""
    log("📄 从 YAML 配置文件加载信息源...")
    from config.source_loader import load_sources_from_config
    
    all_sources = load_sources_from_config()
    log(f"✓ 从 YAML 加载了 {len(all_sources)} 个信息源定义")
    
    # 获取现有信息源
    existing = await db.get_sources(enabled_only=False)
    existing_urls = {s.url for s in existing if s.url}
    
    log(f"📊 当前数据库有 {len(existing)} 个信息源")
    
    # 只添加不存在的源
    new_sources = [s for s in all_sources if s.url not in existing_urls]
    
    if not new_sources:
        log(f"✓ 所有信息源已存在，无需添加")
        return
    
    log(f"🔄 开始添加 {len(new_sources)} 个新信息源...")
    
    success_count = 0
    failed_count = 0
    for source in new_sources:
        try:
            await db.save_source(source)
            success_count += 1
            log(f"  ✓ {source.name}")
        except Exception as e:
            failed_count += 1
            log(f"  ✗ {source.name}: {str(e)}")
    
    log(f"✅ 添加完成: 成功 {success_count} 个, 失败 {failed_count} 个")
    log(f"📊 数据库现有 {len(existing) + success_count} 个信息源")


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
app.include_router(export.router)


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
    from log_config import LOG_CONFIG
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=LOG_CONFIG)
