#!/usr/bin/env python3
"""
快速测试脚本 - 验证后端是否正常工作
"""

import sys
import asyncio
from datetime import datetime

# 测试导入
print("=" * 50)
print("测试 1: 检查模块导入")
print("=" * 50)

try:
    from models import Article, Source, IndustryCategory, SourceType
    print("✓ models 模块导入成功")
except Exception as e:
    print(f"✗ models 模块导入失败: {e}")
    sys.exit(1)

try:
    from storage.database import Database
    print("✓ storage.database 模块导入成功")
except Exception as e:
    print(f"✗ storage.database 模块导入失败: {e}")
    sys.exit(1)

try:
    from crawler.service import CrawlerService
    print("✓ crawler.service 模块导入成功")
except Exception as e:
    print(f"✗ crawler.service 模块导入失败: {e}")
    sys.exit(1)

try:
    from analyzer import Analyzer
    print("✓ analyzer 模块导入成功")
except Exception as e:
    print(f"✗ analyzer 模块导入失败: {e}")
    sys.exit(1)

# 测试数据库
print("\n" + "=" * 50)
print("测试 2: 数据库操作")
print("=" * 50)

async def test_database():
    try:
        db = Database(db_path=":memory:")
        await db.initialize()
        print("✓ 数据库初始化成功")
        
        # 创建测试文章
        article = Article(
            title="测试文章",
            url="https://example.com/test",
            content="这是一篇测试文章",
            industry=IndustryCategory.AI,
            tags=["测试"],
            published_at=datetime.now(),
            fetched_at=datetime.now(),
            language="zh",
            archived=False
        )
        
        article_id = await db.save_article(article)
        print(f"✓ 文章保存成功，ID: {article_id}")
        
        loaded = await db.get_article(article_id)
        assert loaded.title == "测试文章"
        print("✓ 文章读取成功")
        
        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False

if asyncio.run(test_database()):
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！后端准备就绪")
    print("=" * 50)
    print("\n现在可以启动服务器:")
    print("  python3 main.py")
    sys.exit(0)
else:
    print("\n" + "=" * 50)
    print("❌ 测试失败")
    print("=" * 50)
    sys.exit(1)
