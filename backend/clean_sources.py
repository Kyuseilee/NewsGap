#!/usr/bin/env python3
"""
清理数据库中的重复和禁用信息源
"""

import asyncio
import sqlite3
from pathlib import Path


async def clean_sources():
    """清理信息源"""
    db_path = Path(__file__).parent / "data" / "newsgap.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    print("="*80)
    print("开始清理信息源")
    print("="*80)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. 查看当前状态
    print("\n[1/3] 当前信息源统计:")
    cursor.execute("SELECT COUNT(*) FROM sources")
    total = cursor.fetchone()[0]
    print(f"  总数: {total}")
    
    cursor.execute("SELECT COUNT(*) FROM sources WHERE enabled = 1")
    enabled = cursor.fetchone()[0]
    print(f"  启用: {enabled}")
    
    cursor.execute("SELECT COUNT(*) FROM sources WHERE enabled = 0")
    disabled = cursor.fetchone()[0]
    print(f"  禁用: {disabled}")
    
    # 2. 删除所有禁用的源
    print("\n[2/3] 删除所有禁用的信息源...")
    cursor.execute("DELETE FROM sources WHERE enabled = 0")
    deleted_disabled = cursor.rowcount
    print(f"  ✓ 删除 {deleted_disabled} 个禁用源")
    
    # 3. 删除重复的URL（保留最新的一个）
    print("\n[3/3] 删除重复的URL（保留最新的）...")
    
    # 找出所有重复的URL
    cursor.execute("""
        SELECT url, COUNT(*) as count 
        FROM sources 
        WHERE enabled = 1
        GROUP BY url 
        HAVING count > 1
    """)
    duplicate_urls = cursor.fetchall()
    
    if duplicate_urls:
        print(f"  发现 {len(duplicate_urls)} 个重复的URL:")
        total_deleted = 0
        
        for url, count in duplicate_urls:
            print(f"    - {url}: {count} 个重复")
            
            # 获取这个URL的所有记录，按created_at降序
            cursor.execute("""
                SELECT id, name, created_at 
                FROM sources 
                WHERE url = ? AND enabled = 1
                ORDER BY created_at DESC
            """, (url,))
            records = cursor.fetchall()
            
            # 保留第一个（最新的），删除其他的
            keep_id = records[0][0]
            delete_ids = [r[0] for r in records[1:]]
            
            if delete_ids:
                placeholders = ','.join(['?' for _ in delete_ids])
                cursor.execute(f"DELETE FROM sources WHERE id IN ({placeholders})", delete_ids)
                deleted = cursor.rowcount
                total_deleted += deleted
                print(f"      保留: {records[0][1]} (ID: {keep_id})")
                print(f"      删除: {deleted} 个旧记录")
        
        print(f"  ✓ 共删除 {total_deleted} 个重复源")
    else:
        print("  ✓ 没有发现重复的URL")
    
    # 4. 提交更改
    conn.commit()
    
    # 5. 验证结果
    print("\n" + "="*80)
    print("清理后的统计:")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM sources")
    total_after = cursor.fetchone()[0]
    print(f"总数: {total_after}")
    
    cursor.execute("SELECT COUNT(*) FROM sources WHERE enabled = 1")
    enabled_after = cursor.fetchone()[0]
    print(f"启用: {enabled_after}")
    
    cursor.execute("SELECT COUNT(*) FROM sources WHERE enabled = 0")
    disabled_after = cursor.fetchone()[0]
    print(f"禁用: {disabled_after}")
    
    print("\n按行业分布:")
    cursor.execute("SELECT industry, COUNT(*) FROM sources WHERE enabled = 1 GROUP BY industry")
    for industry, count in cursor.fetchall():
        print(f"  {industry}: {count} 个")
    
    print("\n当前所有启用的源:")
    cursor.execute("SELECT name, url, industry FROM sources WHERE enabled = 1 ORDER BY industry, name")
    for name, url, industry in cursor.fetchall():
        print(f"  [{industry}] {name}")
        print(f"    {url}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 清理完成！")
    print("="*80)
    print(f"删除了 {deleted_disabled} 个禁用源")
    print(f"删除了重复源，保留 {enabled_after} 个唯一的启用源")


if __name__ == "__main__":
    asyncio.run(clean_sources())
