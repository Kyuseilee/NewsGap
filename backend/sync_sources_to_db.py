#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步 sources.yaml 配置到数据库
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.source_loader import SourceConfigLoader, log
from storage.database import Database


async def sync_sources_to_db():
    """将 sources.yaml 中的配置同步到数据库"""
    
    log("开始同步信息源配置...")
    
    # 加载配置
    loader = SourceConfigLoader()
    sources = loader.load_sources()
    log(f"从 sources.yaml 加载了 {len(sources)} 个信息源")
    
    # 连接数据库
    db = Database()
    await db.initialize()
    log("数据库连接成功")
    
    # 同步到数据库
    success_count = 0
    fail_count = 0
    
    for source in sources:
        try:
            await db.save_source(source)
            success_count += 1
        except Exception as e:
            log(f"⚠️  保存失败: {source.name} - {str(e)}")
            fail_count += 1
    
    log(f"✅ 同步完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    
    # 统计
    all_sources = await db.get_sources(enabled_only=False)
    enabled_sources = await db.get_sources(enabled_only=True)
    
    log(f"\n数据库统计:")
    log(f"  总数: {len(all_sources)} 个")
    log(f"  启用: {len(enabled_sources)} 个")
    
    # 按行业统计
    from collections import Counter
    industries = Counter(s.industry.value for s in enabled_sources)
    log(f"\n按行业分类 (仅启用):")
    for industry, count in sorted(industries.items(), key=lambda x: -x[1]):
        log(f"  {industry:15s}: {count:3d} 个源")


if __name__ == "__main__":
    asyncio.run(sync_sources_to_db())
