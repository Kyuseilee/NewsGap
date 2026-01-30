#!/usr/bin/env python3
"""
迁移旧分类到新分类体系
"""

import sqlite3
from pathlib import Path


def migrate_categories():
    """迁移分类"""
    db_path = Path(__file__).parent / "data" / "newsgap.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    print("="*80)
    print("开始分类迁移")
    print("="*80)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 分类映射
    category_mapping = {
        'ai': 'tech',           # AI归入科技互联网
        'healthcare': 'other',   # 医疗健康暂时归入其他
    }
    
    # 1. 查看当前分类
    print("\n[1/3] 当前分类分布:")
    cursor.execute("SELECT industry, COUNT(*) FROM sources GROUP BY industry")
    for industry, count in cursor.fetchall():
        print(f"  {industry}: {count} 个源")
    
    # 2. 迁移sources表
    print("\n[2/3] 迁移sources表...")
    for old_cat, new_cat in category_mapping.items():
        cursor.execute("UPDATE sources SET industry = ? WHERE industry = ?", (new_cat, old_cat))
        updated = cursor.rowcount
        if updated > 0:
            print(f"  ✓ {old_cat} -> {new_cat}: {updated} 个源")
    
    # 3. 迁移articles表
    print("\n[3/3] 迁移articles表...")
    for old_cat, new_cat in category_mapping.items():
        cursor.execute("UPDATE articles SET industry = ? WHERE industry = ?", (new_cat, old_cat))
        updated = cursor.rowcount
        if updated > 0:
            print(f"  ✓ {old_cat} -> {new_cat}: {updated} 篇文章")
    
    conn.commit()
    
    # 验证
    print("\n" + "="*80)
    print("迁移后的分类:")
    print("="*80)
    cursor.execute("SELECT industry, COUNT(*) FROM sources GROUP BY industry")
    for industry, count in cursor.fetchall():
        print(f"  {industry}: {count} 个源")
    
    conn.close()
    
    print("\n✅ 分类迁移完成！")


if __name__ == "__main__":
    migrate_categories()
