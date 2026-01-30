#!/usr/bin/env python3
"""
数据库迁移脚本

清理旧的行业分类数据
"""

import asyncio
import sqlite3
from pathlib import Path


async def migrate_database():
    """迁移数据库"""
    db_path = Path(__file__).parent / "data" / "newsgap.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    print("="*80)
    print("开始数据库迁移")
    print("="*80)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. 查看当前的行业分类分布
    print("\n[1/4] 当前行业分类分布:")
    cursor.execute("SELECT industry, COUNT(*) FROM sources GROUP BY industry")
    rows = cursor.fetchall()
    for industry, count in rows:
        print(f"  {industry}: {count} 个源")
    
    cursor.execute("SELECT industry, COUNT(*) FROM articles GROUP BY industry")
    rows = cursor.fetchall()
    print("\n当前文章行业分布:")
    for industry, count in rows:
        print(f"  {industry}: {count} 篇文章")
    
    # 2. 删除无效分类的源
    print("\n[2/4] 删除无效分类的信息源...")
    invalid_categories = ['education', 'energy', 'entertainment']
    for cat in invalid_categories:
        cursor.execute("DELETE FROM sources WHERE industry = ?", (cat,))
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"  ✓ 删除 {cat} 分类: {deleted} 个源")
    
    # 3. 将无效分类的文章移到 other 分类
    print("\n[3/4] 迁移无效分类的文章到 'other'...")
    for cat in invalid_categories:
        cursor.execute("UPDATE articles SET industry = 'other' WHERE industry = ?", (cat,))
        updated = cursor.rowcount
        if updated > 0:
            print(f"  ✓ 迁移 {cat} 分类: {updated} 篇文章")
    
    # 4. 提交更改
    conn.commit()
    
    # 验证结果
    print("\n[4/4] 迁移后的行业分类分布:")
    cursor.execute("SELECT industry, COUNT(*) FROM sources GROUP BY industry")
    rows = cursor.fetchall()
    print("\n信息源:")
    for industry, count in rows:
        print(f"  {industry}: {count} 个源")
    
    cursor.execute("SELECT industry, COUNT(*) FROM articles GROUP BY industry")
    rows = cursor.fetchall()
    print("\n文章:")
    for industry, count in rows:
        print(f"  {industry}: {count} 篇文章")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 数据库迁移完成！")
    print("="*80)
    print("\n提示：现在可以运行 setup_sources.py 来初始化新的信息源")


if __name__ == "__main__":
    asyncio.run(migrate_database())
