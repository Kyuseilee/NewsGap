#!/usr/bin/env python3
"""
数据库迁移工具
"""

import sqlite3
import sys
from pathlib import Path

def run_migration(db_path: str, migration_file: str):
    """运行单个迁移文件"""
    print(f"📖 读取迁移文件: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"💾 连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 执行迁移...")
        cursor.executescript(migration_sql)
        conn.commit()
        print("✅ 迁移成功！")
        return True
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    # 数据库路径
    db_path = "../data/newsgap.db"
    
    # 检查数据库是否存在
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        sys.exit(1)
    
    # 运行迁移
    migration_file = "../database/migrations/001_add_industry_to_analyses.sql"
    
    if not Path(migration_file).exists():
        print(f"❌ 迁移文件不存在: {migration_file}")
        sys.exit(1)
    
    success = run_migration(db_path, migration_file)
    
    if success:
        print("\n🎉 所有迁移完成！")
        sys.exit(0)
    else:
        print("\n❌ 迁移失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
